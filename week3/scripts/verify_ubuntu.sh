#!/usr/bin/env bash
# Tests actual identity-based access, not password authentication.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo bash verify_ubuntu.sh'; exit 1; }
failures=0
check() {
  local expected=$1 user=$2 label=$3 rc=0
  shift 3
  runuser -u "$user" -- "$@" || rc=$?
  if { [[ $expected == allow && $rc -eq 0 ]]; } || { [[ $expected == deny && $rc -ne 0 ]]; }; then
    printf 'PASS | %s | %s | exit=%s\n' "$user" "$label" "$rc"
  else
    printf 'FAIL | %s | %s | exit=%s\n' "$user" "$label" "$rc"
    failures=$((failures+1))
  fi
}
for user in student2 faculty2 student4; do id "$user"; done
for path in /labdata /facultydata /studentdata; do
  [[ -d "$path" && ! -L "$path" && -f "$path/sample.txt" ]] || { echo "Missing expected setup: $path"; exit 1; }
done
[[ $(stat -c '%U:%G:%a' /labdata) == root:labusers:770 ]] || { echo 'Expected initial /labdata root:labusers mode 770; inspect before testing.'; exit 1; }
[[ $(stat -c '%U:%G:%a' /facultydata) == root:facultygrp:770 ]] || exit 1
[[ $(stat -c '%U:%G:%a' /studentdata) == root:studentgrp:750 ]] || exit 1
for path in /labdata/student2-test.txt /labdata/denied-test.txt /facultydata/faculty2-test.txt /studentdata/denied-test.txt; do
  [[ ! -e "$path" && ! -L "$path" ]] || { echo "Existing test file: $path"; exit 1; }
done
stat -c '%A %a %U:%G %n' /labdata /facultydata /studentdata
check allow student2 'read lab sample at 770' cat /labdata/sample.txt
check allow student2 'create lab file at 770' touch /labdata/student2-test.txt
chmod 0750 /labdata
stat -c '%A %a %U:%G %n' /labdata
check allow student2 'read lab sample at 750' cat /labdata/sample.txt
check deny student2 'create lab file at 750' touch /labdata/denied-test.txt
check allow faculty2 'read faculty sample' cat /facultydata/sample.txt
check allow faculty2 'create faculty file' touch /facultydata/faculty2-test.txt
check allow student4 'read student sample' cat /studentdata/sample.txt
check deny student4 'create student file' touch /studentdata/denied-test.txt
check deny student4 'modify existing student sample' sh -c 'echo attempt >> /studentdata/sample.txt'
check deny student4 'read faculty sample' cat /facultydata/sample.txt
check deny faculty2 'read student sample' cat /studentdata/sample.txt
check deny student2 'read faculty sample' cat /facultydata/sample.txt
check deny student2 'read student sample' cat /studentdata/sample.txt
printf 'Failed checks: %s\n' "$failures"
echo 'Now verify passwords through interactive logins; runuser does not test them.'
[[ $failures -eq 0 ]]
