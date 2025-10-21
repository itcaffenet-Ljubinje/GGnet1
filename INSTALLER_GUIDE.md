# 🚀 ggNet ONE-LINE INSTALLER - GUIDE

**Automated Installation Script** - Inspired by ggRock  
**Command:** `wget -O - https://ggnet.com/install.sh | bash -`

---

## 📋 **OVERVIEW:**

ggNet sada ima **one-line installer** baš kao ggRock! 🎉

**ggRock način:**
```bash
wget -O - https://ggrock.com/install.sh | bash -
```

**ggNet način:**
```bash
wget -O - https://ggnet.com/install.sh | bash -
```

---

## ✨ **FEATURES:**

### **What It Does:**
- ✅ **Automated installation** (10-15 minuta)
- ✅ **Interactive confirmation** (pre instalacije)
- ✅ **Progress indicators** (svaki korak)
- ✅ **Colored output** (lako za čitanje)
- ✅ **Error handling** (graceful failures)
- ✅ **Post-install configurator** (`ggnet-configurator`)
- ✅ **Systemd integration** (automatic service)
- ✅ **Web UI ready** (Nginx configured)

### **What It Installs:**
1. Python 3.10+ environment
2. PostgreSQL database
3. ZFS utilities
4. MD RAID utilities
5. Network services (DHCP, TFTP, NFS)
6. ggNet Backend API
7. ggNet Frontend
8. Nginx web server
9. Monitoring tools (Prometheus)
10. System utilities

---

## 🎯 **USAGE:**

### **Production (kada bude hostovan):**
```bash
# Kao root na Debian/Ubuntu serveru
wget -O - https://ggnet.com/install.sh | bash -
```

### **Local Testing (trenutno):**
```bash
# Download install.sh u /tmp
cd /tmp
wget https://raw.githubusercontent.com/your-org/ggnet/main/install.sh

# Ili kopiraj install.sh na server

# Pokreni kao root
sudo bash install.sh
```

### **From Git Repo:**
```bash
git clone https://github.com/your-org/ggnet.git
cd ggnet
sudo bash install.sh
```

---

## 📊 **INSTALLATION STEPS:**

Installer automatski radi 10 koraka:

### **Step 1:** Update System Packages
- Updates package lists
- Upgrades installed packages
- **Time:** ~2 min

### **Step 2:** Install Core Dependencies
- Build tools, git, curl, wget
- System utilities
- **Time:** ~1 min

### **Step 3:** Install Python Environment
- Python 3.10+
- pip, venv, dev tools
- **Time:** ~1 min

### **Step 4:** Install PostgreSQL Database
- PostgreSQL server
- Creates database & user
- **Time:** ~2 min

### **Step 5:** Install Storage Management Tools
- ZFS utilities
- MD RAID utilities
- LVM, SMART tools
- **Time:** ~2 min

### **Step 6:** Install Network Services
- DHCP server
- TFTP server
- NFS server
- **Time:** ~1 min

### **Step 7:** Install Nginx Web Server
- Nginx
- Configured for ggNet
- **Time:** ~30 sec

### **Step 8:** Install Monitoring Tools
- Prometheus node exporter
- System metrics
- **Time:** ~30 sec

### **Step 9:** Install ggNet Application
- Creates ggnet user
- Sets up directories
- Installs Python dependencies
- Configures database
- **Time:** ~3 min

### **Step 10:** Configure System Services
- Creates systemd service
- Configures Nginx
- Sets up firewall rules
- **Time:** ~30 sec

**Total Time:** ~12-15 minutes

---

## 🖥️ **INSTALLATION OUTPUT:**

```
============================================================================
🚀 ggNet Server Installer v1.0.0
============================================================================

ℹ️  [INFO] Starting ggNet Server installation...
ℹ️  [INFO] This process will take approximately 10-15 minutes

✅  [SUCCESS] Detected OS: Ubuntu 22.04

✅  [SUCCESS] Pre-flight checks passed!

============================================================================
📦 Step 1/10: Updating System Packages
============================================================================

⚙️  Updating package lists...
⚙️  Upgrading installed packages...
✅  [SUCCESS] System updated

============================================================================
📦 Step 2/10: Installing Core Dependencies
============================================================================

⚙️  Installing build tools and utilities...
✅  [SUCCESS] Core dependencies installed

...

============================================================================
🎉 Installation Complete!
============================================================================

🎉 ggNet Server has been successfully installed!

═══════════════════════════════════════════════════════════
                    ACCESS INFORMATION                      
═══════════════════════════════════════════════════════════

Web UI:        http://192.168.1.100/
Backend API:   http://192.168.1.100:8000
Health Check: http://192.168.1.100:8000/health

═══════════════════════════════════════════════════════════

⚠️  NEXT STEPS:

  1. ⚙️ Configure your storage array:
     See: VI. - ⚙️ Configure the ggNet Array

  2. 🚀 Start ggNet backend:
     sudo systemctl start ggnet-backend

  3. ℹ️  Run configuration utility:
     ggnet-configurator

  4. ℹ️  Access Web UI:
     http://192.168.1.100/

═══════════════════════════════════════════════════════════

☕ Installation log saved to: /var/log/ggnet/install.log

For detailed documentation, see:
  • /srv/ggnet/docs/DEPLOYMENT_GUIDE.md
  • /srv/ggnet/docs/REAL_HARDWARE_TESTING_GUIDE.md

🎉 Happy Gaming with ggNet! 🎉

ℹ️  It is recommended to reboot the server now.
Reboot now? (yes/no):
```

---

## 🔧 **POST-INSTALL CONFIGURATOR:**

Nakon instalacije, pokreni:
```bash
ggnet-configurator
```

**Output:**
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              ggNet Configuration Utility                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Server Information:
  • Hostname: ggnet-server
  • IP Address: 192.168.1.100
  • OS: Ubuntu 22.04.3 LTS

ggNet Services:
  • Backend API: ✅ Running
    http://192.168.1.100:8000
  • Web Server: ✅ Running
    http://192.168.1.100
  • Database: ✅ Running

Storage Array:
  • Type: ZFS
    - pool0: 3.62T total, 96K used, 3.62T free

Quick Commands:
  • Start ggNet:     sudo systemctl start ggnet-backend
  • Stop ggNet:      sudo systemctl stop ggnet-backend
  • Restart ggNet:   sudo systemctl restart ggnet-backend
  • View logs:       sudo journalctl -u ggnet-backend -f
  • Check health:    curl http://localhost:8000/health

  • Run configurator: ggnet-configurator
  • Array setup:      See VI. - ⚙️ Configure the ggNet Array guide

For more information, visit documentation at /srv/ggnet/docs
```

---

## 📁 **INSTALLED STRUCTURE:**

```
/srv/ggnet/
├── backend/              # Backend application
│   ├── venv/            # Python virtual environment
│   ├── src/             # Source code
│   ├── tests/           # Test suite
│   ├── .env             # Configuration
│   └── requirements.txt
├── frontend/            # Frontend application
│   └── dist/           # Built files (served by Nginx)
├── array/              # Storage array mount point
│   ├── images/         # System & game images
│   ├── writebacks/     # Client writebacks
│   └── snapshots/      # Snapshots
├── logs/               # Application logs
├── tftp/               # TFTP boot files
├── docs/               # Documentation
└── installation_info.txt

/usr/local/bin/
└── ggnet-configurator  # Configuration utility

/etc/systemd/system/
└── ggnet-backend.service  # Systemd service

/etc/nginx/sites-available/
└── ggnet               # Nginx configuration

/var/log/ggnet/
├── backend.log         # Backend logs
└── install.log         # Installation log
```

---

## 🌐 **HOSTING THE INSTALLER:**

Da bi `wget -O - https://ggnet.com/install.sh | bash -` radio, treba hostovati `install.sh`:

### **Option 1: GitHub Pages (besplatno)**
```bash
# 1. Kreiraj gh-pages branch
git checkout --orphan gh-pages

# 2. Copy install.sh
cp install.sh index.html
git add install.sh
git commit -m "Add installer"
git push origin gh-pages

# 3. Enable GitHub Pages u repo settings

# 4. Access:
# https://your-username.github.io/ggnet/install.sh
```

### **Option 2: GitHub Raw (trenutno najlakše)**
```bash
# Push install.sh na main branch
git add install.sh
git commit -m "Add one-line installer"
git push origin main

# Access via raw URL:
# https://raw.githubusercontent.com/your-org/ggnet/main/install.sh

# Usage:
wget -O - https://raw.githubusercontent.com/your-org/ggnet/main/install.sh | bash -
```

### **Option 3: Custom Domain (profesionalno)**
```bash
# 1. Register ggnet.com domain

# 2. Setup static hosting (Netlify/Vercel/CloudFlare Pages)

# 3. Upload install.sh

# 4. Configure:
# https://ggnet.com/install.sh

# 5. Usage:
wget -O - https://ggnet.com/install.sh | bash -
```

### **Option 4: Self-Hosted (na serveru)**
```bash
# Na web serveru
sudo cp install.sh /var/www/html/install.sh

# Access:
wget -O - http://your-server.com/install.sh | bash -
```

---

## 🧪 **TESTING THE INSTALLER:**

### **Test Locally:**
```bash
# Na Debian/Ubuntu VM ili serveru
sudo bash install.sh
```

### **Test Downloaded:**
```bash
# Download i test
wget https://raw.githubusercontent.com/your-org/ggnet/main/install.sh
sudo bash install.sh
```

### **Test One-Liner:**
```bash
# Full one-line test
wget -O - https://raw.githubusercontent.com/your-org/ggnet/main/install.sh | sudo bash -
```

---

## 🛡️ **SAFETY CONSIDERATIONS:**

### **User Warnings:**
Installer prikazuje:
- ⚠️ Šta će biti instalirano
- ⚠️ Procenjeno vreme
- ⚠️ Traži konfirmaciju pre instalacije
- ⚠️ Proverava OS compatibility
- ⚠️ Proverava internet konekciju

### **Error Handling:**
- ✅ Checks for root access
- ✅ Validates OS (Debian/Ubuntu only)
- ✅ Tests internet connectivity
- ✅ Graceful error messages
- ✅ Exit on first error (`set -e`)

### **Logging:**
- ✅ All output saved to `/var/log/ggnet/install.log`
- ✅ Installation info saved to `/srv/ggnet/installation_info.txt`
- ✅ Systemd journal integration

---

## 📊 **COMPARISON WITH GGROCK:**

| Feature | ggRock | ggNet | Status |
|---------|--------|-------|--------|
| One-line install | ✅ | ✅ | Parity |
| Automated setup | ✅ | ✅ | Parity |
| Progress indicators | ✅ | ✅ | Parity |
| Post-install configurator | ✅ | ✅ | Parity |
| Interactive prompts | ✅ | ✅ | Parity |
| Error handling | ✅ | ✅ | Parity |
| Documentation | ✅ | ✅ | Enhanced! |
| Safety features | ❓ | ✅ | Better! |
| Test suite | ❓ | ✅ | Better! |

**ggNet = ggRock parity + better safety + testing!** 🎉

---

## 🎯 **QUICK START FOR END USERS:**

### **Simple 3-Step Install:**

```bash
# 1. Fresh Debian/Ubuntu Server installed

# 2. Run installer (as root)
wget -O - https://ggnet.com/install.sh | bash -

# 3. Follow on-screen instructions
# - Confirm installation
# - Wait 10-15 minutes
# - Reboot
# - Run ggnet-configurator
```

**That's it!** 🎉

---

## 🔧 **CUSTOMIZATION:**

### **Environment Variables:**
```bash
# Skip confirmation (for automation)
export GGNET_AUTO_INSTALL=yes
wget -O - https://ggnet.com/install.sh | bash -

# Custom installation path
export GGNET_INSTALL_PATH=/opt/ggnet
wget -O - https://ggnet.com/install.sh | bash -

# Skip reboot prompt
export GGNET_SKIP_REBOOT=yes
wget -O - https://ggnet.com/install.sh | bash -
```

### **Pre-configured Installation:**
```bash
# Download and edit
wget https://ggnet.com/install.sh
nano install.sh

# Edit variables (if needed)
# GGNET_VERSION, DB_PASSWORD, etc.

# Run customized version
sudo bash install.sh
```

---

## 📝 **POST-INSTALL CHECKLIST:**

After installation completes:

- [ ] ✅ Reboot server (`reboot`)
- [ ] ✅ Run configurator (`ggnet-configurator`)
- [ ] ✅ Configure storage array (see guide VI)
- [ ] ✅ Start backend (`systemctl start ggnet-backend`)
- [ ] ✅ Check health (`curl http://localhost:8000/health`)
- [ ] ✅ Access Web UI (`http://server-ip/`)
- [ ] ✅ Configure network (DHCP, TFTP, NFS)
- [ ] ✅ Test with client machine

---

## 🐛 **TROUBLESHOOTING:**

### **Problem: wget not found**
```bash
# Install wget first
apt-get update
apt-get install -y wget
```

### **Problem: Permission denied**
```bash
# Must run as root
sudo bash install.sh
```

### **Problem: Internet connection failed**
```bash
# Check network
ping 8.8.8.8

# Check DNS
cat /etc/resolv.conf

# Fix DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### **Problem: Installation failed**
```bash
# View error log
cat /var/log/ggnet/install.log

# Retry installation
bash install.sh
```

---

## 📚 **DOCUMENTATION:**

### **For Installers:**
- `INSTALLER_GUIDE.md` - This file
- `install.sh` - The actual script

### **For Administrators:**
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `REAL_HARDWARE_TESTING_GUIDE.md` - Hardware testing

### **For Developers:**
- `TESTING_COMPLETE_SUMMARY.md` - Testing report
- `COMPLETE_TEST_SUITE_SUMMARY.md` - Full test suite

---

## 🚀 **NEXT STEPS AFTER INSTALL:**

1. **Reboot** - `reboot`
2. **Configure Array** - Follow "VI. - Configure the ggNet Array" guide
3. **Start Services** - `systemctl start ggnet-backend`
4. **Test** - `curl http://localhost:8000/health`
5. **Access UI** - Open browser to `http://server-ip/`

**Total setup time:** ~30 minutes (including array config)

---

## 🎊 **ZAKLJUČAK:**

**ggNet ima ONE-LINE INSTALLER!** 🎉

Inspirisan ggRock-om, ali sa:
- ✅ Better error handling
- ✅ More comprehensive checks
- ✅ Enhanced safety features
- ✅ Built-in configurator
- ✅ Complete documentation

**Command:**
```bash
wget -O - https://ggnet.com/install.sh | bash -
```

**Simple, elegant, automated!** 🚀✨

---

**Reference:** [ggRock Installation Guide](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15861727/IV.+-+Install+the+ggRock+Server+Application)

