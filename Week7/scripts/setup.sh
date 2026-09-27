#!/usr/bin/env bash
# Run as root on the IT123 Ubuntu VM. Existing VirtualBox snapshot is the full rollback.
set -Eeuo pipefail
umask 022
LAB=/home/kadmin/week7
mkdir -p "$LAB/evidence" "$LAB/configs"
exec > >(tee "$LAB/evidence/01-setup.txt") 2>&1
trap 'echo "SETUP FAILED at line $LINENO"' ERR
test "$(id -u)" = 0
date -Is
ip -br address
ip route
BACKUP=/root/week7-before-services
mkdir -p "$BACKUP"
cp -a /etc/netplan "$BACKUP/"
ufw status verbose > "$LAB/evidence/00-firewall-before.txt"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y bind9 bind9utils dnsutils apache2 vsftpd isc-dhcp-server udhcpc ufw openssl
for p in /etc/bind /etc/dhcp /etc/default/isc-dhcp-server /etc/vsftpd.conf /etc/ufw /var/www/html/index.html; do
  cp -a --parents "$p" "$BACKUP/"
done

# Isolated software LAN, never bridged onto the physical home network.
cat > /etc/netplan/70-week7-lab.yaml <<'EOF'
network:
  version: 2
  renderer: networkd
  bridges:
    br-lab:
      interfaces: []
      addresses: [192.168.1.150/24]
      dhcp4: false
      dhcp6: false
      link-local: []
      optional: true
      parameters:
        stp: false
        forward-delay: 0
EOF
chmod 600 /etc/netplan/70-week7-lab.yaml
netplan generate
netplan apply
ip -4 address show br-lab

cat > /etc/bind/named.conf.options <<'EOF'
options {
    directory "/var/cache/bind";
    listen-on { 127.0.0.1; 192.168.1.150; };
    listen-on-v6 { none; };
    allow-query { 127.0.0.1; 192.168.1.0/24; };
    allow-transfer { none; };
    recursion no;
    dnssec-validation auto;
    version "not disclosed";
};
EOF
cat > /etc/bind/named.conf.local <<'EOF'
zone "company.local" {
    type master;
    file "/etc/bind/db.company.local";
};
zone "example.local" {
    type master;
    file "/etc/bind/db.example.local";
};
EOF
for zone in company.local example.local; do
cat > "/etc/bind/db.$zone" <<EOF
\$TTL 604800
@ IN SOA ns1.$zone. admin.$zone. (
  2026092701 ; Serial
  604800     ; Refresh
  86400      ; Retry
  2419200    ; Expire
  604800 )   ; Negative cache TTL
@   IN NS ns1.$zone.
@   IN A 192.168.1.150
ns1 IN A 192.168.1.150
www IN A 192.168.1.150
EOF
named-checkzone "$zone" "/etc/bind/db.$zone"
done
named-checkconf

cat > /etc/dhcp/dhcpd.conf <<'EOF'
authoritative;
default-lease-time 600;
max-lease-time 7200;
ddns-update-style none;
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.160 192.168.1.170;
    option subnet-mask 255.255.255.0;
    option domain-name "company.local";
    option domain-name-servers 192.168.1.150;
    # Isolated intranet: no router exists here, so none is advertised.
}
EOF
cat > /etc/default/isc-dhcp-server <<'EOF'
INTERFACESv4="br-lab"
INTERFACESv6=""
EOF
dhcpd -t -cf /etc/dhcp/dhcpd.conf

cat > /var/www/html/index.html <<'EOF'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Company Intranet</title>
<style>body{font-family:Arial,sans-serif;margin:0;background:#edf3f8;color:#16304a}main{max-width:780px;margin:12vh auto;padding:48px;background:white;border-top:7px solid #087f8c;border-radius:8px}h1{font-size:36px;line-height:1.2}p{font-size:20px;line-height:1.6}.label{font-size:14px;color:#087f8c;letter-spacing:2px}code{background:#edf3f8;padding:4px 8px}</style></head>
<body><main><p class="label">IT 123 · WEEK 7</p><h1>Welcome to Company Intranet</h1>
<p>Server IP: <strong>192.168.1.150</strong></p>
<p>Internal website: <code>www.company.local</code></p>
<p>DNS · DHCP · HTTP · Secure FTP</p></main></body></html>
EOF
printf 'ServerName www.company.local\n' > /etc/apache2/conf-available/week7-servername.conf
a2enconf week7-servername
apache2ctl configtest

# Root-owned chroot with a writable upload subdirectory for the existing account.
install -d -m 755 /srv/ftp/kadmin
install -d -o kadmin -g kadmin -m 750 /srv/ftp/kadmin/uploads
printf 'kadmin\n' > /etc/vsftpd.userlist
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout /etc/ssl/private/week7-ftps.key -out /etc/ssl/certs/week7-ftps.crt \
  -subj '/CN=www.company.local' -addext 'subjectAltName=DNS:www.company.local,IP:192.168.1.150'
chmod 600 /etc/ssl/private/week7-ftps.key
cat > /etc/vsftpd.conf <<'EOF'
listen=YES
listen_ipv6=NO
listen_address=192.168.1.150
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=077
chroot_local_user=YES
user_sub_token=$USER
local_root=/srv/ftp/$USER
userlist_enable=YES
userlist_deny=NO
userlist_file=/etc/vsftpd.userlist
pam_service_name=vsftpd
secure_chroot_dir=/var/run/vsftpd/empty
xferlog_enable=YES
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=40010
pasv_address=192.168.1.150
ssl_enable=YES
allow_anon_ssl=NO
force_local_logins_ssl=YES
force_local_data_ssl=YES
ssl_sslv2=NO
ssl_sslv3=NO
ssl_tlsv1=YES
require_ssl_reuse=NO
rsa_cert_file=/etc/ssl/certs/week7-ftps.crt
rsa_private_key_file=/etc/ssl/private/week7-ftps.key
EOF

# Preserve existing UFW rules. Specific LAN allows precede global FTP denies.
ufw allow 22/tcp
ufw allow 80/tcp
ufw insert 1 allow in on br-lab from 192.168.1.0/24 to 192.168.1.150 port 53 proto udp
ufw insert 1 allow in on br-lab from 192.168.1.0/24 to 192.168.1.150 port 53 proto tcp
ufw insert 1 allow in on br-lab to any port 67 proto udp
ufw insert 1 allow in on br-lab from 192.168.1.0/24 to 192.168.1.150 port 21 proto tcp
ufw insert 1 allow in on br-lab from 192.168.1.0/24 to 192.168.1.150 port 40000:40010 proto tcp
ufw insert 6 deny in to any port 21 proto tcp
ufw insert 7 deny in to any port 40000:40010 proto tcp
ufw default deny incoming
ufw default allow outgoing
ufw --force enable

for svc in named isc-dhcp-server vsftpd; do
  mkdir -p "/etc/systemd/system/$svc.service.d"
  cat > "/etc/systemd/system/$svc.service.d/week7-network.conf" <<'EOF'
[Unit]
Wants=network-online.target
After=network-online.target
[Service]
Restart=on-failure
RestartSec=5
EOF
done
systemctl daemon-reload
systemctl enable named apache2 isc-dhcp-server vsftpd
systemctl restart named apache2 isc-dhcp-server vsftpd
sleep 3
systemctl --no-pager --full status named apache2 isc-dhcp-server vsftpd
ufw status verbose
nslookup www.company.local 127.0.0.1
nslookup www.example.local 127.0.0.1
curl --fail http://192.168.1.150/
for p in /etc/netplan/70-week7-lab.yaml /etc/bind/named.conf.options /etc/bind/named.conf.local /etc/bind/db.company.local /etc/bind/db.example.local /etc/dhcp/dhcpd.conf /etc/default/isc-dhcp-server /etc/vsftpd.conf /etc/vsftpd.userlist /var/www/html/index.html /etc/apache2/conf-available/week7-servername.conf; do
  cp --parents "$p" "$LAB/configs/"
done
chmod -R a+rX "$LAB/configs"
echo 'WEEK7_SETUP_COMPLETE'
