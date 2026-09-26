# Week 2 - VirtualBox Laboratory

## Files

```text
week2/
  README.md
  lab_notes.md
  report/
    IT123_Week2_Lab_Report_DRAFT.pdf
  screenshots/
    01-virtualbox-settings.png
    02-ubuntu-login-prompt.png
  scripts/
    build_report.py
    requirements.txt
```

## Report and evidence

- [PDF report draft](report/IT123_Week2_Lab_Report_DRAFT.pdf)
- [Detailed lab notes](lab_notes.md)
- [VirtualBox configuration screenshot](screenshots/01-virtualbox-settings.png)
- [Ubuntu boot/login prompt screenshot](screenshots/02-ubuntu-login-prompt.png)

The screenshots record the existing Ubuntu VM. They are not original installation screenshots. A login prompt is not evidence of successful account login.

## Completion status

Verified: Ubuntu boots; 2048 MB RAM, 2 CPUs, 25 GB virtual disk, and NAT networking are configured.

Pending: password recovery, successful login, network and SSH checks, Windows Server evidence, and student name and section. The guide specifies a 30 GB Ubuntu disk; the existing VM has 25 GB.

## Rebuild the report

From the repository root, with Python installed:

```sh
python -m pip install -r week2/scripts/requirements.txt
python week2/scripts/build_report.py
```

The script writes the PDF to `week2/report/` and preview images to the ignored `tmp/pdfs/` directory. Update the report content only after verifying the corresponding work.
