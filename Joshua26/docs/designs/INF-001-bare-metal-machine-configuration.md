# INF-001: Bare Metal Machine Configuration

**Status:** Draft
**Created:** 2026-01-11

## Overview

This document defines the standard configuration for bare metal machines in the infrastructure. All machines are peers in a Docker Swarm cluster, differentiated by hardware capabilities rather than hierarchy.

## Machine Inventory

| Machine | IP | Role | Hardware Strengths |
|---------|-----|------|-------------------|
| irina | x.x.x.110 | Swarm Leader | 87TB ZFS storage, Tesla P4 (8GB) |
| M5 | x.x.x.120 | Swarm Manager | 256GB RAM, 2TB NVMe, 6x GPU (3x P40 24GB, 1x V100 PCIe 32GB, 2x V100 SXM2 32GB NVLink) |
| Hymie | x.x.x.130 | Swarm Manager | Desktop automation workstation |
| J-Desktop | x.x.x.250 | Windows compute node | Intel i7-4790K, 16GB RAM, RTX 3050 8GB, 2TB SSD + 16TB HDD |

Workload placement follows hardware affinity: databases on storage-rich nodes, ML/memory workloads on GPU/RAM-rich nodes.

---

## BASE CONFIGURATION (All Machines)

### 1. Operating System

- Ubuntu 24.04 LTS (Noble)
- Kernel: 6.14.x

### 2. User Account

- Username: aristotle9
- UID/GID: 1000
- Groups: adm, cdrom, sudo, dip, plugdev, users, lpadmin, docker
- Home: /home/aristotle9
- Password: [REDACTED] (synced via lsyncd)

### 3. Network Configuration

#### 3.1 Host Bonding

Machines with multiple NICs use bonded interfaces for redundancy:

- Bond Interface: bond0
- Mode: XOR load balancing (balance-xor)
- Hash Policy: layer2
- Slaves: 2x 1Gbps NICs
- Subnet: x.x.x.0/24
- Gateway: x.x.x.1

**Note:** Bonding is only applicable to machines with multiple network interfaces. Single-NIC machines should configure their interface directly with a static IP and skip bonding configuration (ifenslave package not required).

#### 3.2 Static IP Assignment

Each machine has a static IP on the x.x.x.0/24 subnet.

### 4. SSH Configuration

#### 4.1 OpenSSH Server

Package: openssh-server

All machines run OpenSSH server with password authentication enabled for user access.

#### 4.2 Password Authentication

Password authentication is enabled for interactive and scripted access.

/etc/ssh/sshd_config settings:
```
PasswordAuthentication yes
PermitRootLogin prohibit-password
```

#### 4.3 sshpass for Scripted Access

Package: sshpass

sshpass enables non-interactive password-based SSH for automation and scripting.

Installation:
```bash
sudo apt-get install -y sshpass
```

Usage:
```bash
sshpass -p 'password' ssh user@host "command"
```

This is used for:
- Cross-node administration from Claude Code and other automation tools
- Scripted commands when key-based auth is not configured
- Initial setup before SSH keys are exchanged

#### 4.4 SSH Keys for lsyncd

Root accounts have ed25519 SSH keys for lsyncd identity synchronization:

- Key location: /root/.ssh/id_ed25519
- Key type: ed25519

Generate on new machine:
```bash
sudo ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ""
```

Copy to peer nodes:
```bash
sudo ssh-copy-id -i /root/.ssh/id_ed25519.pub root@<peer-ip>
```

#### 4.5 Known Hosts

Add peer hosts to avoid interactive prompts:
```bash
ssh-keyscan -H <peer-ip> >> ~/.ssh/known_hosts
sudo ssh-keyscan -H <peer-ip> >> /root/.ssh/known_hosts
```

#### 4.6 User SSH Keys for Remote Administration

User aristotle9 has SSH key-based authentication configured for passwordless remote access from Windows development machine.

**Key Setup:**
- Private key: Windows machine (~/.ssh/id_ed25519)
- Public key installed: ~/.ssh/authorized_keys on each host
- Key type: ed25519

**Public Key Content:**
```
[REDACTED]
```

**Verification:**
```bash
# From Windows
ssh aristotle9@x.x.x.110 whoami  # Should connect without password
ssh aristotle9@x.x.x.110 docker ps  # Should work without sudo
```

**Benefits:**
- Passwordless SSH for remote docker commands
- Passwordless docker access (user in docker group)
- Simpler deployment automation
- More secure than password authentication

**See Also:** `docs/guides/remote-docker-access-via-ssh.md` for usage examples

### 5. Identity Synchronization (lsyncd)

Bidirectional sync of identity files between all nodes:

Files synced:
- /etc/passwd
- /etc/group
- /etc/shadow
- /etc/gshadow
- /etc/subuid
- /etc/subgid

This keeps user accounts, passwords, and group memberships identical across all machines.

Service: lsyncd-identity.service

Configuration (/etc/lsyncd/lsyncd.conf.lua):

```lua
settings {
    logfile = "/var/log/lsyncd/lsyncd.log",
    statusFile = "/var/log/lsyncd/lsyncd.status",
    nodaemon = false
}

sync {
    default.rsync,
    source = "/etc/",
    target = "<OTHER_NODE_IP>:/etc/",
    delay = 1,
    rsync = {
        archive = true,
        perms = true,
        owner = true,
        group = true,
        rsh = "/usr/bin/ssh -i /root/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
    },
    filter = {
        "+ passwd",
        "+ group",
        "+ shadow",
        "+ gshadow",
        "+ subuid",
        "+ subgid",
        "- *"
    }
}
```

Systemd service (/etc/systemd/system/lsyncd-identity.service):

```ini
[Unit]
Description=Lsyncd Identity Sync
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/lsyncd -nodaemon /etc/lsyncd/lsyncd.conf.lua
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lsyncd-identity.service
sudo systemctl start lsyncd-identity.service
```

### 6. VNC (Remote Desktop)

TigerVNC with XFCE4 desktop environment.

#### 6.1 Required Packages

```bash
sudo apt-get install -y tigervnc-standalone-server tigervnc-common xfce4 xfce4-goodies dbus-x11
```

#### 6.2 xstartup (~/.vnc/xstartup)

```bash
#!/bin/bash
# XFCE4 VNC startup script
unset SESSION_MANAGER
export XKL_XMODMAP_DISABLE=1

# Start dbus session and XFCE4 desktop environment
if command -v dbus-run-session >/dev/null 2>&1; then
    exec dbus-run-session startxfce4
elif command -v dbus-launch >/dev/null 2>&1; then
    exec dbus-launch --exit-with-session startxfce4
else
    exec startxfce4
fi
```

Make executable: `chmod +x ~/.vnc/xstartup`

#### 6.3 Systemd Service (/etc/systemd/system/vncserver@.service)

```ini
[Unit]
Description=Start TigerVNC server at startup
After=syslog.target network.target

[Service]
Type=forking
User=aristotle9
Group=aristotle9
WorkingDirectory=/home/aristotle9

PIDFile=/home/aristotle9/.vnc/%H:%i.pid
ExecStartPre=-/usr/bin/vncserver -kill :%i
ExecStart=/usr/bin/vncserver -depth 24 -geometry 1920x1080 -localhost no :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
```

#### 6.4 Setup

```bash
vncpasswd
sudo systemctl daemon-reload
sudo systemctl enable vncserver@2.service
sudo systemctl start vncserver@2.service
```

Ports: Display :n = port 5900+n (e.g., :2 = 5902)

### 7. Docker

#### 7.1 Installation

Standard Docker from Ubuntu repos:
- docker.io or docker-ce
- docker-compose-plugin

User aristotle9 must be in docker group:
```bash
sudo usermod -aG docker aristotle9
```

**Important:** Docker group membership allows running docker commands without sudo. This is required for MCP tools since Claude Code cannot handle interactive sudo password prompts.

#### 7.2 Docker Swarm

All machines participate in a multi-manager swarm for HA.

Current topology:
- irina: Leader
- M5: Reachable (backup manager)

Initialize swarm (first node):
```bash
docker swarm init --advertise-addr <node-ip>
```

Join as manager (subsequent nodes):
```bash
docker swarm join --token <manager-token> <leader-ip>:2377
```

Get manager token:
```bash
docker swarm join-token manager
```

#### 7.3 Overlay Network

- Network: joshua-net
- Driver: overlay
- Subnet: 10.0.1.0/24
- Gateway: 10.0.1.1

Create network (once, from any manager):
```bash
docker network create --driver overlay --attachable joshua-net
```

Services communicate via this overlay network across nodes.

### 8. NFS (Shared Storage)

All machines mount shared storage from the storage-rich node.

Client configuration (/etc/fstab):
```
x.x.x.110:/mnt/storage /mnt/storage nfs defaults 0 0
```

Required package: nfs-common

Create mount point and mount:
```bash
sudo mkdir -p /mnt/storage
sudo mount -a
```

### 9. MCP Access

MAD MCP endpoints are exposed directly on `joshua-net` (the Docker overlay network). Claude Code and other clients connect to MADs via their gateway ports listed in `registry.yml`. Each MAD gateway listens on `joshua-net` at its assigned port and serves MCP at `/mcp`.

**Connecting Claude Code to a MAD:**

```bash
claude mcp add -s user <mad-name> --transport http --url http://<mad-host>:<port>/mcp
```

Refer to `registry.yml` for the authoritative list of MAD names, hosts, and ports.

---

## STORAGE NODE ADDITIONS (e.g., irina)

Machines with large storage arrays serve NFS exports.

### 1. ZFS

- Pool: storage
- Mountpoint: /mnt/storage

### 2. NFS Server

Package: nfs-kernel-server

Export (/etc/exports):
```
/mnt/storage x.x.x.0/24(rw,sync,no_subtree_check,no_root_squash,insecure)
```

Apply exports:
```bash
sudo exportfs -ra
```

---

## GPU NODE ADDITIONS (e.g., M5)

Machines with GPUs require NVIDIA drivers and container toolkit.

### 1. NVIDIA Drivers

Install appropriate drivers for GPU hardware.

### 2. NVIDIA Container Toolkit

Enables GPU access from Docker containers.

---

## WINDOWS COMPUTE NODE (J-Desktop)

**Host:** DESKTOP-2IRN4KA
**IP:** x.x.x.250
**OS:** Windows 10 Pro

**Hardware:**
- CPU: Intel Core i7-4790K @ 4.00GHz (4 cores / 8 threads)
- RAM: 16GB
- Storage: 2TB SSD + 16TB HDD (Seagate ST16000VE000)
- GPU: NVIDIA GeForce RTX 3050, 8GB VRAM (CUDA, driver 577.00)

**Role:** K3s compute worker node for Sutherland GPU workloads. Contributes RTX 3050
for smaller model inference and embedding tasks.

**Setup approach:** Linux VM via Hyper-V with Discrete Device Assignment (DDA) for
GPU passthrough. The Ubuntu VM runs K3s agent, joins the cluster, and gets raw GPU
access. NVIDIA drivers + container toolkit installed in the VM. The Windows host acts
as a dumb hypervisor.

**Constraints:**
- 8GB VRAM limits model size — suitable for 7B class models (Q4/Q8) and embedding models
- i7-4790K (Haswell, 2014) is older generation but adequate for the host hypervisor role
- Not a Linux bare-metal node — does not run docker-compose MAD containers directly

---

## REQUIRED PACKAGES SUMMARY

Base (all machines):
- openssh-server
- sshpass
- docker.io (or docker-ce)
- docker-compose-plugin
- tigervnc-standalone-server
- tigervnc-common
- xfce4
- xfce4-goodies
- dbus-x11
- nfs-common
- lsyncd
- ifenslave (for bonding)

Storage nodes:
- zfsutils-linux
- nfs-kernel-server

GPU nodes:
- nvidia-driver-xxx
- nvidia-container-toolkit

---

## NEW MACHINE SETUP CHECKLIST

1. Install Ubuntu 24.04 LTS
2. Configure network (bond0 if multiple NICs, or static IP for single NIC)
3. Create aristotle9 user (uid 1000)
4. Install base packages (including sshpass)
5. Configure SSH (password auth enabled)
6. Generate root SSH keys and exchange with peers
7. Configure lsyncd identity sync
8. Mount NFS storage
9. Set VNC password and configure service
10. Join Docker Swarm as manager
11. Deploy relevant MAD containers for this host (per registry.yml host assignments)
12. Configure Claude Code MCP connections to MAD gateways
13. Verify all services running and MCP tools accessible

---

## TROUBLESHOOTING

**VNC shows gray screen:**
- Check xfce4 packages installed: `dpkg -l | grep xfce4`
- Check VNC log: `cat ~/.vnc/$(hostname):2.log`
- Verify xstartup is executable

**Identity not syncing:**
- Check lsyncd service: `systemctl status lsyncd-identity`
- Check logs: `/var/log/lsyncd/lsyncd.log`
- Verify root SSH keys between nodes

**SSH connection refused:**
- Check sshd running: `systemctl status ssh`
- Verify password auth: `grep PasswordAuthentication /etc/ssh/sshd_config`
- Check firewall: `sudo ufw status`

**Swarm issues:**
- Check node status: `docker node ls`
- Rejoin if needed: `docker swarm join --token <token> <manager-ip>:2377`
