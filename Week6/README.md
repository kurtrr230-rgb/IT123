# IT 123 — Week 6 Ubuntu Server network lab

This folder contains the completed Ubuntu-only portion of the Week 6 lab. The existing `ubuntu_server` VirtualBox VM was used. The VM is back on its original DHCP configuration and was verified online after the test.

Start with [lab_notes.md](lab_notes.md) for an easy step-by-step account. The [PDF report](report/IT123_Week6_Ubuntu_Network_Lab.pdf) is the submission copy.

## What is included

- `evidence/`: unedited command output from the DHCP baseline, temporary static configuration, and restored DHCP configuration.
- `screenshots/`: actual Ubuntu VM console captures of the netplan settings and connectivity tests.
- `scripts/netplan-static.yaml`: the temporary static configuration used on this VM's VirtualBox NAT network.
- `report/`: the PDF lab report.

The course exercise names `192.168.1.150/24`, but this VM's adapter is on VirtualBox NAT `10.0.2.0/24` with gateway `10.0.2.2`. The working static test therefore used `10.0.2.150/24`. A second server was not available, so server-to-server ping was not claimed or fabricated.

No passwords or virtual disk images are stored here.
