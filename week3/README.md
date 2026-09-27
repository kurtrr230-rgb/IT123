# Week 3 - Ubuntu Users, Groups, and Permissions

Scope: Ubuntu only, as requested. Windows Server work is deferred.

## Contents

- [Lab notes and procedure](lab_notes.md)
- [Verification results](verification.md)
- [Setup script](scripts/setup_ubuntu.sh)
- [Access-test script](scripts/verify_ubuntu.sh)
- [Ubuntu lab report PDF](report/IT123_Week3_Ubuntu_Lab_Report.pdf)
- [VM test output](verification-output.txt)
- [VM screenshots](screenshots/)

**Status: Ubuntu lab executed and verified.** Three user password logins succeeded and all 12 access checks passed. Windows Server is deferred because no Windows Server VM is installed. Student name and section were not supplied.

## Procedure used

The scripts were copied into Ubuntu and run from kadmin's home directory:

```sh
sudo bash ~/setup_ubuntu.sh
sudo passwd student2
sudo passwd faculty2
sudo passwd student4
sudo bash ~/verify_ubuntu.sh 2>&1 | tee ~/week3-verification.txt
```

Passwords were entered interactively and are absent from the repository.

The setup script checks for existing target users, groups, and paths before making changes. The test script uses new user contexts and leaves `/labdata` at mode 750 after testing the initial mode 770. The three account passwords were entered through hidden prompts; no password is stored in this repository.

Each account was checked with a password-backed `su - ACCOUNT -c 'id'` login. The PDF records actual outcomes and the scope limitation.
