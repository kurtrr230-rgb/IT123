#!/usr/bin/env bash
set -Eeuo pipefail
LAB=/home/kadmin/week7
exec > >(tee "$LAB/evidence/02-verification.txt") 2>&1
cleanup() {
  ip netns del week7-client 2>/dev/null || true
  ip netns del week7-outside 2>/dev/null || true
  ip link del w7lan 2>/dev/null || true
  ip link del w7wan 2>/dev/null || true
  if id week7check >/dev/null 2>&1; then userdel week7check; fi
  sed -i '/^week7check$/d' /etc/vsftpd.userlist
}
trap cleanup EXIT
trap 'echo "VERIFICATION FAILED at line $LINENO"' ERR
date -Is
test "$(id -u)" = 0
cleanup
echo '=== CONFIGURATION VALIDATION ==='
named-checkconf
named-checkzone company.local /etc/bind/db.company.local
named-checkzone example.local /etc/bind/db.example.local
dhcpd -t -cf /etc/dhcp/dhcpd.conf
apache2ctl configtest
systemctl is-active named apache2 isc-dhcp-server vsftpd
systemctl is-enabled named apache2 isc-dhcp-server vsftpd
ip -br address
ss -lntup
ufw status numbered
echo '=== ISOLATED DHCP CLIENT ==='
ip netns add week7-client
ip link add w7lan type veth peer name eth0 netns week7-client
ip link set w7lan master br-lab
ip link set w7lan up
ip netns exec week7-client ip link set lo up
ip netns exec week7-client ip link set eth0 address 02:00:00:07:00:01
ip netns exec week7-client ip link set eth0 up
cat > /run/week7-udhcpc.sh <<'EOF'
#!/bin/sh
case "$1" in
  bound|renew)
    ip address replace "$ip/24" dev "$interface"
    printf 'DHCP address=%s subnet=%s DNS=%s domain=%s\n' "$ip" "$subnet" "$dns" "$domain"
    test "$dns" = 192.168.1.150 || exit 1
    ;;
esac
EOF
chmod 755 /run/week7-udhcpc.sh
ip netns exec week7-client udhcpc -i eth0 -f -n -q -t 4 -T 3 -s /run/week7-udhcpc.sh
CLIENT_IP=$(ip netns exec week7-client ip -4 -o address show eth0 | awk '{print $4}')
echo "CLIENT_ADDRESS=$CLIENT_IP"
[[ "$CLIENT_IP" =~ ^192\.168\.1\.(16[0-9]|170)/24$ ]]
echo '=== CLIENT DNS UDP AND TCP ==='
ip netns exec week7-client nslookup www.company.local 192.168.1.150
test "$(ip netns exec week7-client dig +short @192.168.1.150 www.company.local)" = 192.168.1.150
ip netns exec week7-client dig +tcp @192.168.1.150 www.company.local
test "$(ip netns exec week7-client dig +tcp +short @192.168.1.150 www.company.local)" = 192.168.1.150
nslookup www.example.local 127.0.0.1
echo '=== CLIENT HTTP ==='
ip netns exec week7-client curl --fail --show-error --resolve www.company.local:80:192.168.1.150 http://www.company.local/
echo
ip netns exec week7-client curl --fail --silent http://192.168.1.150/ | grep -F 'Welcome to Company Intranet'

echo '=== ENCRYPTED FTP UPLOAD AND DOWNLOAD ==='
useradd --no-create-home --home-dir /srv/ftp/week7check --shell /bin/bash week7check
install -d -m 755 /srv/ftp/week7check
install -d -m 700 -o week7check -g week7check /srv/ftp/week7check/uploads
printf 'week7check\n' >> /etc/vsftpd.userlist
python3 - <<'PY'
import secrets, subprocess
password = secrets.token_urlsafe(32)
subprocess.run(['chpasswd'], input='week7check:'+password+'\n', text=True, check=True)
code = r'''
import ftplib, io, ssl, sys
password = sys.stdin.read().strip()
ctx = ssl.create_default_context(cafile='/etc/ssl/certs/week7-ftps.crt')
ftp = ftplib.FTP_TLS(context=ctx, timeout=10)
ftp.connect('192.168.1.150', 21)
ftp.login('week7check', password)
ftp.prot_p()
print('FTPS TLS:', ftp.sock.version())
payload = b'IT123 Week7 verified encrypted file transfer\n'
ftp.storbinary('STOR uploads/verification.txt', io.BytesIO(payload))
received = bytearray()
ftp.retrbinary('RETR uploads/verification.txt', received.extend)
assert bytes(received) == payload
print('PASS: encrypted login, upload, download and exact content comparison')
ftp.quit()
plain = ftplib.FTP('192.168.1.150', timeout=5)
try:
    plain.login('week7check', password)
except ftplib.error_perm as exc:
    assert str(exc).startswith('530'), str(exc)
    print('PASS: plaintext login rejected:', exc)
else:
    raise AssertionError('Plaintext FTP login unexpectedly succeeded')
finally:
    plain.close()
'''
subprocess.run(['ip','netns','exec','week7-client','python3','-c',code], input=password, text=True, check=True)
PY
echo '=== OUTSIDE-LAN FTP RESTRICTION ==='
ip netns add week7-outside
ip link add w7wan type veth peer name eth0 netns week7-outside
ip address add 198.18.0.1/30 dev w7wan
ip link set w7wan up
ip netns exec week7-outside ip link set lo up
ip netns exec week7-outside ip link set eth0 up
ip netns exec week7-outside ip address add 198.18.0.2/30 dev eth0
ip netns exec week7-outside ip route add 192.168.1.150/32 via 198.18.0.1
# HTTP control proves the route to the server works before FTP rejection checks.
ip netns exec week7-outside curl --fail --silent --max-time 5 http://192.168.1.150/ > /dev/null
echo 'PASS: outside test route reaches Apache'
ip netns exec week7-outside python3 - <<'PY'
import socket
for port in (21,40000):
    try:
        s=socket.create_connection(('192.168.1.150',port),timeout=3)
    except TimeoutError:
        print(f'PASS: outside-LAN TCP {port} blocked (timeout)')
    else:
        s.close()
        raise AssertionError(f'Outside-LAN TCP {port} unexpectedly accessible')
PY
echo '=== DHCP LEASE AND SERVICE LOG ==='
cat /var/lib/dhcp/dhcpd.leases
journalctl -u isc-dhcp-server -n 25 --no-pager
echo 'WEEK7_ALL_TESTS_PASSED'
