# IT 123 — Week 6 Ubuntu Server network lab

**Scope:** Ubuntu Server only. Work was performed on the existing VirtualBox VM `ubuntu_server` (Ubuntu 26.04.1 LTS), with one NAT-connected interface named `enp0s3`. No Windows Server work was requested. No second Ubuntu VM was available.

**Result:** A temporary static IPv4 address was applied and tested, then the VM's original DHCP file was restored. The final address is `10.0.2.15/24`, with default gateway `10.0.2.2`. Internet ping and DNS resolution worked after restoration.

## Why the static address differs from the guide

The guide's `192.168.1.150/24` and `192.168.1.1` gateway assume a `192.168.1.0/24` network. This VM's VirtualBox NAT adapter was actually on `10.0.2.0/24`. Applying the guide's address to that adapter would remove the working route. For a real, reachable static-IP demonstration, I used `10.0.2.150/24` with gateway `10.0.2.2` and DNS `8.8.8.8`, `8.8.4.4`. The original DHCP settings were then restored. The exact `192.168.1.150` requirement would need a compatible network or a separate adapter.

## Step 1 — Check the current configuration

I saved a VirtualBox snapshot named `Week6-before-network` before changing the network file. The original netplan file was copied to [evidence/00-installer-config.original.yaml](evidence/00-installer-config.original.yaml).

Commands used in the VM:

```bash
ip -4 a show dev enp0s3
ip route
resolvectl dns enp0s3
cat /etc/netplan/00-installer-config.yaml
ping -c 2 10.0.2.2
ping -c 2 8.8.8.8
nslookup google.com
```

The VM had DHCP address `10.0.2.15/24`, gateway `10.0.2.2`, and a working DNS resolver. See [baseline output](evidence/01-before.txt) and [original netplan screenshot](screenshots/01-netplan-before.png).

## Step 2 — Apply a temporary static address

I installed the `traceroute` package, copied [scripts/netplan-static.yaml](scripts/netplan-static.yaml) to `/etc/netplan/00-installer-config.yaml` with root ownership and mode `600`, checked syntax with `sudo netplan generate`, then ran `sudo netplan try --timeout 120` at the VM console. This trial mode would automatically revert if the new address failed. I confirmed the new connection before accepting it.

Key settings:

```yaml
enp0s3:
  dhcp4: false
  addresses: [10.0.2.150/24]
  routes:
    - to: default
      via: 10.0.2.2
  nameservers:
    addresses: [8.8.8.8, 8.8.4.4]
```

The complete, tested file also preserves the original MAC match, interface name, and IPv6 DHCP setting. The live address became `10.0.2.150/24`. See [static settings screenshot](screenshots/02-netplan-static.png).

## Step 3 — Test connectivity and troubleshoot

Commands used:

```bash
ip -4 a show dev enp0s3
ip route
resolvectl dns enp0s3
ping -c 4 10.0.2.2
ping -c 4 8.8.8.8
ping -4 -c 4 google.com
nslookup google.com
traceroute -4 -m 12 -q 1 -w 1 google.com
ss -tuln
```

The static address and default route were present. Gateway, public-IP, and domain-name pings each received **4 of 4 replies**. `nslookup` returned IPv4 and IPv6 records for `google.com`. `traceroute` reached the NAT gateway as hop 1; subsequent hops showed `*`, which means those probes did not receive a reply. This does not contradict the successful internet ping and DNS checks. `ss -tuln` listed SSH and local DNS listeners. Full unedited output is in [static test output](evidence/02-static-tests.txt), with [ping](screenshots/03-ping.png) and [DNS/traceroute](screenshots/04-dns-traceroute.png) screenshots.

## Step 4 — Restore and verify DHCP

I restored the saved original file, ran `sudo netplan generate`, and used `sudo netplan try --timeout 120` again. Before accepting the change, I checked that the VM had `10.0.2.15/24`, the default route via `10.0.2.2`, a working public-IP ping, and a successful DNS lookup. A file comparison confirmed the active netplan file exactly matched the original backup.

The full post-restore run again received **4 of 4 replies** from the gateway, `8.8.8.8`, and `google.com`; DNS resolution succeeded. See [restored DHCP output](evidence/03-dhcp-restored.txt) and [restored configuration screenshot](screenshots/05-dhcp-restored.png). Temporary host-side SSH forwarding rules used for the lab were removed afterward.

## Student exercise limit

Only one Ubuntu VM was available. It demonstrated a static-IP Server A state and a DHCP Server B state sequentially, but these were not two simultaneous servers. Therefore the two-server ping test was **not performed**. A second VM and a shared network would be required to complete that part. The optional Windows task was outside the requested Ubuntu-only scope.
