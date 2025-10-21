# 📦 ggNet Installation Guide

## 📋 Overview

This guide provides step-by-step instructions for installing ggNet on Debian/Ubuntu servers.

---

## 🎯 **Installation Options**

### **Option 1: Standard Installation** (Recommended for Development)

**Script:** `scripts/install.sh`

**Features:**
- ✅ Idempotent (can be run multiple times safely)
- ✅ Interactive network bridge setup
- ✅ Automatic dependency installation
- ✅ Systemd service deployment
- ✅ Nginx configuration
- ✅ Frontend build

**Usage:**
```bash
cd /path/to/ggnet
sudo ./scripts/install.sh
```

**Options:**
```bash
# Skip package installation (if packages already installed)
sudo ./scripts/install.sh --skip-packages

# Setup PostgreSQL database
sudo ./scripts/install.sh --setup-db

# Show help
sudo ./scripts/install.sh --help
```

---

### **Option 2: Production Installation** (Recommended for Production)

**Script:** `scripts/install-production.sh`

**Features:**
- ✅ Production-ready configuration
- ✅ Enhanced security
- ✅ PostgreSQL database setup
- ✅ Firewall configuration
- ✅ SSL/TLS support
- ✅ Monitoring setup

**Usage:**
```bash
cd /path/to/ggnet
sudo ./scripts/install-production.sh
```

---

## 🔧 **Prerequisites**

### **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Debian 11+ / Ubuntu 22+ | Debian 12 / Ubuntu 24 |
| **RAM** | 4 GB | 16 GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 50 GB | 500 GB+ (RAID array) |
| **Network** | 1 Gbps | 10 Gbps |

### **Required Packages**

The install script will automatically install:
- `nginx` - Web server
- `python3` - Python runtime
- `python3-pip` - Python package manager
- `python3-venv` - Python virtual environments
- `nodejs` - Node.js runtime
- `npm` - Node.js package manager
- `isc-dhcp-server` - DHCP server
- `tftpd-hpa` - TFTP server
- `nfs-kernel-server` - NFS server
- `mdadm` - RAID management
- `jq` - JSON processor
- `rsync` - File synchronization
- `curl`, `wget` - HTTP clients
- `git` - Version control
- `sudo` - Privilege escalation
- `sqlite3` - SQLite database
- `qemu-utils` - QEMU utilities

---

## 📦 **Installation Steps**

### **Step 1: Download ggNet**

```bash
# Clone repository
git clone https://github.com/yourusername/ggnet.git
cd ggnet

# Or download and extract
wget https://github.com/yourusername/ggnet/releases/latest/download/ggnet.tar.gz
tar -xzf ggnet.tar.gz
cd ggnet
```

---

### **Step 2: Run Installation Script**

```bash
# Make script executable
chmod +x scripts/install.sh

# Run installation
sudo ./scripts/install.sh
```

---

### **Step 3: Follow Interactive Prompts**

The installation script will:

1. ✅ **Validate prerequisites** (OS version, root access)
2. ✅ **Install system packages** (nginx, python3, nodejs, etc.)
3. ✅ **Ask about network bridge** (optional, for VM networking)
4. ✅ **Create system user** (`ggnet`)
5. ✅ **Create directories** (`/opt/ggnet`, `/srv/ggnet`, `/etc/ggnet`, `/var/log/ggnet`)
6. ✅ **Copy application files**
7. ✅ **Setup Python virtual environment**
8. ✅ **Install Python dependencies**
9. ✅ **Build frontend** (React + TypeScript + Vite)
10. ✅ **Configure Nginx** (reverse proxy)
11. ✅ **Deploy systemd services**
12. ✅ **Initialize database** (optional)
13. ✅ **Start services**

---

### **Step 4: Verify Installation**

```bash
# Check backend status
systemctl status ggnet-backend

# Check Nginx status
systemctl status nginx

# Check logs
journalctl -u ggnet-backend -f

# Test API
curl http://localhost:8080/api/status

# Test web interface
curl http://localhost
```

---

## 🌐 **Access Points**

After installation, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Web Interface** | `http://<server-ip>` | Main web UI |
| **API Docs** | `http://<server-ip>/docs` | Swagger/OpenAPI docs |
| **API Status** | `http://<server-ip>/api/status` | Health check |
| **Backend API** | `http://<server-ip>:8080` | Direct API access |

---

## 🔧 **Post-Installation Configuration**

### **1. Storage Array Setup**

```bash
# Create RAID10 array (recommended)
sudo ./storage/raid/create_raid10.sh

# Or use existing ZFS pool
sudo zpool create pool0 /dev/sda /dev/sdb
```

### **2. Network Configuration**

```bash
# Configure DHCP
sudo cp pxe/dhcp/generated-dhcp.conf /etc/dhcp/dhcpd.conf
sudo systemctl restart isc-dhcp-server

# Configure NFS
sudo cp pxe/nfs/exports.template /etc/exports
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server

# Configure TFTP
sudo systemctl restart tftpd-hpa
```

### **3. PXE Boot Setup**

```bash
# Generate PXE configurations
cd /opt/ggnet/backend
source venv/bin/activate
python scripts/generate_pxe_configs.py
```

---

## 🎨 **Dark Mode**

ggNet includes comprehensive dark mode support:

- ✅ **Automatic detection** - Detects system preference
- ✅ **Manual toggle** - Toggle button in sidebar
- ✅ **Persistent** - Saves preference to localStorage
- ✅ **WCAG compliant** - Sufficient contrast ratios

**Toggle Dark Mode:**
- Click the Moon/Sun icon in the sidebar
- Preference is saved automatically

---

## 🔐 **Security**

### **Firewall Configuration**

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS (if using SSL)
sudo ufw allow 443/tcp

# Allow DHCP
sudo ufw allow 67/udp

# Allow TFTP
sudo ufw allow 69/udp

# Allow NFS
sudo ufw allow from 10.0.0.0/8 to any port 2049
```

### **SSL/TLS Setup (Optional)**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 🐛 **Troubleshooting**

### **Backend Not Starting**

```bash
# Check logs
journalctl -u ggnet-backend -n 50

# Check database
ls -la /opt/ggnet/backend/src/ggnet.db

# Restart service
sudo systemctl restart ggnet-backend
```

### **Frontend Not Loading**

```bash
# Check Nginx logs
tail -f /var/log/nginx/error.log

# Verify frontend build
ls -la /opt/ggnet/frontend/dist

# Rebuild frontend
cd /opt/ggnet/frontend
sudo -u ggnet npm run build
```

### **Database Issues**

```bash
# Check database file
ls -la /opt/ggnet/backend/src/ggnet.db

# Recreate database
cd /opt/ggnet/backend/src
sudo -u ggnet python ../scripts/seed_db.py
```

### **Network Bridge Issues**

```bash
# Check bridge status
ip addr show br0

# Recreate bridge
sudo python3 scripts/create_network_bridge.py eth0 br0
```

---

## 📚 **Useful Commands**

### **Service Management**

```bash
# Start services
sudo systemctl start ggnet-backend
sudo systemctl start nginx

# Stop services
sudo systemctl stop ggnet-backend
sudo systemctl stop nginx

# Restart services
sudo systemctl restart ggnet-backend
sudo systemctl restart nginx

# Check status
sudo systemctl status ggnet-backend
sudo systemctl status nginx

# View logs
journalctl -u ggnet-backend -f
journalctl -u nginx -f
```

### **Database Management**

```bash
# Backup database
sudo cp /opt/ggnet/backend/src/ggnet.db /opt/ggnet/backend/src/ggnet.db.backup

# Restore database
sudo cp /opt/ggnet/backend/src/ggnet.db.backup /opt/ggnet/backend/src/ggnet.db

# View database
sqlite3 /opt/ggnet/backend/src/ggnet.db
```

### **System Check**

```bash
# Run system check script
sudo ./scripts/check_system.sh

# Check disk space
df -h

# Check memory
free -h

# Check network
ip addr show
```

---

## 🔄 **Upgrading**

```bash
# Pull latest changes
cd /path/to/ggnet
git pull

# Re-run installation script (idempotent)
sudo ./scripts/install.sh

# Restart services
sudo systemctl restart ggnet-backend
sudo systemctl reload nginx
```

---

## 🗑️ **Uninstallation**

```bash
# Run uninstall script
sudo ./scripts/uninstall.sh

# Or manually:
# Stop services
sudo systemctl stop ggnet-backend
sudo systemctl disable ggnet-backend

# Remove files
sudo rm -rf /opt/ggnet
sudo rm -rf /srv/ggnet
sudo rm -rf /etc/ggnet
sudo rm -rf /var/log/ggnet

# Remove user
sudo userdel ggnet

# Remove systemd service
sudo rm /etc/systemd/system/ggnet-backend.service
sudo systemctl daemon-reload
```

---

## 📖 **Additional Resources**

- **Backend README:** `/opt/ggnet/backend/README.md`
- **Frontend README:** `/opt/ggnet/frontend/README.md`
- **API Documentation:** `http://<server-ip>/docs`
- **Storage Guide:** `STORAGE_COMPLETE.md`
- **Network Guide:** `NETWORK_SETUP.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`

---

## ✅ **Installation Checklist**

- [ ] System meets minimum requirements
- [ ] Downloaded ggNet source code
- [ ] Ran installation script
- [ ] Verified backend is running
- [ ] Verified Nginx is running
- [ ] Tested web interface
- [ ] Tested API endpoints
- [ ] Configured storage array
- [ ] Configured network (DHCP, TFTP, NFS)
- [ ] Configured PXE boot
- [ ] Set up firewall rules
- [ ] Configured SSL/TLS (optional)
- [ ] Set up monitoring (optional)
- [ ] Created backup strategy
- [ ] Documented configuration

---

**Installation complete! 🎉**

For support, visit: https://github.com/yourusername/ggnet/issues

---

**Last Updated:** October 20, 2025  
**Version:** 1.8.0  
**Status:** ✅ Production Ready

