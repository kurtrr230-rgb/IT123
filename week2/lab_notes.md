# IT 123 - Week 2 Laboratory Notes

## Scope and evidence

The Ubuntu VM was installed previously during Lab 1, according to the student. This session inspects that existing installation and prepares account recovery and documentation. Original installation screenshots were not supplied; the attached photographs are the laboratory guide, not evidence of the student's installation.

## Verified configuration (26 September 2026)

| Item | Observed value |
| --- | --- |
| VirtualBox VM | ubuntu_server |
| Guest OS boot banner | Ubuntu 24.04.1 LTS |
| RAM | 2048 MB |
| Virtual CPUs | 2 |
| Virtual disk | VDI, 25.00 GB shown in VirtualBox Manager |
| Firmware | BIOS |
| Network | Adapter 1: NAT, cable connected |
| Graphics | VMSVGA, 16 MB video memory |
| Optical drive | Empty |
| Existing snapshot | Snapshot 1 |
| Boot verification | Reached the Ubuntu console login prompt |
| Successful account login | Not yet verified |

The guide specifies a 30 GB Ubuntu disk; the existing VM shows 25 GB. No disk resizing has been performed. The presence of a snapshot was verified, but its contents and whether it represents a clean installation have not been verified.

## Evidence collected

1. [VirtualBox settings](screenshots/01-virtualbox-settings.png)
2. [Ubuntu console login prompt](screenshots/02-ubuntu-login-prompt.png)

A login prompt demonstrates boot completion, not a successful user login.

## Account recovery status

Password reset is pending. The VM boots normally; the GRUB recovery menu has not yet been opened. Credentials will not be included in this report or committed to Git.

## Outstanding deliverables

- Recover the Ubuntu account and verify successful login.
- Check Ubuntu networking and OpenSSH service status after access is restored.
- Obtain student name and section for the report.
- Clarify whether Windows Server was installed elsewhere; only Ubuntu is currently registered in VirtualBox.
- Obtain original installation screenshots or label a reconstruction of installation steps clearly as retrospective.
- Produce the final PDF with verified findings and evidence.
- Confirm the GitHub repository destination, commit the documentation, and push it.

## Source

Student-supplied photographs of the IT 123 Week 2 Laboratory Guide, covering VM configuration, documentation in week2, GitHub upload, and a PDF lab report.
