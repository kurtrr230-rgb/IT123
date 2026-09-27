#!/usr/bin/env bash
set -Eeuo pipefail
LAB=/home/kadmin/week7
test "$(id -u)" = 0
# Only the IPv4 DHCP lab was configured.
systemctl disable --now isc-dhcp-server6
# Remove the disposable FTPS test directory after its account has been removed.
if ! id week7check >/dev/null 2>&1; then
  python3 - <<'PY'
from pathlib import Path
import shutil
p = Path('/srv/ftp/week7check')
if p.is_dir() and not p.is_symlink():
    shutil.rmtree(p)
PY
fi
{
  date -Is
  echo '=== PACKAGE VERSIONS ==='
  dpkg-query -W bind9 apache2 isc-dhcp-server vsftpd ufw
  echo '=== SERVICE STATE ==='
  for service in named apache2 isc-dhcp-server vsftpd; do
    printf '%s: ' "$service"
    systemctl is-active "$service"
    systemctl is-enabled "$service"
  done
  echo '=== STATIC LAB ADDRESS ==='
  ip -br address
  echo '=== FIREWALL ==='
  ufw status verbose
  ufw status numbered
  echo '=== FTP ACCOUNT ALLOWLIST ==='
  cat /etc/vsftpd.userlist
  ls -ld /srv/ftp/kadmin /srv/ftp/kadmin/uploads
  echo '=== FTPS CERTIFICATE ==='
  openssl x509 -in /etc/ssl/certs/week7-ftps.crt -noout -subject -dates -fingerprint -sha256
  echo '=== TEMPORARY TEST RESOURCES REMOVED ==='
  ip netns list
  if id week7check; then exit 1; else echo 'Temporary FTP test account removed'; fi
} > "$LAB/evidence/03-final-state.txt" 2>&1
for p in /etc/systemd/system/named.service.d/week7-network.conf /etc/systemd/system/isc-dhcp-server.service.d/week7-network.conf /etc/systemd/system/vsftpd.service.d/week7-network.conf /etc/ufw/user.rules /etc/ufw/user6.rules /etc/vsftpd.userlist /etc/ssl/certs/week7-ftps.crt; do
  cp --parents "$p" "$LAB/configs/"
done
chmod -R a+rX "$LAB/configs" "$LAB/evidence"
echo 'WEEK7_EVIDENCE_COMPLETE'
