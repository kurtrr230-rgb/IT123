#!/usr/bin/env bash
# Prepared for the Ubuntu Week 3 lab; not yet executed.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo bash setup_ubuntu.sh'; exit 1; }
for user in student2 faculty2 student4; do
  if getent passwd "$user" >/dev/null; then
    echo "STOP: account $user already exists; inspect it before changing anything."; exit 1
  fi
done
for group in student2 faculty2 student4 labusers facultygrp studentgrp; do
  if getent group "$group" >/dev/null; then
    echo "STOP: group $group already exists; inspect it before changing anything."; exit 1
  fi
done
for path in /labdata /facultydata /studentdata /home/student2 /home/faculty2 /home/student4; do
  [[ ! -e "$path" && ! -L "$path" ]] || { echo "STOP: $path already exists."; exit 1; }
done
for user in student2 faculty2 student4; do
  adduser --disabled-password --gecos '' "$user"
done
usermod -c 'Test account for Week 3 Lab' student2
for group in labusers facultygrp studentgrp; do groupadd "$group"; done
usermod -aG labusers student2
usermod -aG facultygrp faculty2
usermod -aG studentgrp student4
install -d -o root -g labusers -m 0770 /labdata
install -d -o root -g facultygrp -m 0770 /facultydata
install -d -o root -g studentgrp -m 0750 /studentdata
for path in /labdata /facultydata /studentdata; do
  printf 'Week 3 permission verification sample\n' > "$path/sample.txt"
  chown root:root "$path/sample.txt"
  chmod 0644 "$path/sample.txt"
done
echo 'Setup complete. Set passwords with sudo passwd USER before login tests.'
echo 'No passwords were set or written to this script.'
