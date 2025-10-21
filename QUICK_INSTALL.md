# ⚡ ggNet - QUICK INSTALL

**Get ggNet running in 15 minutes!**

---

## 🚀 **ONE-LINE INSTALL:**

```bash
wget -O - https://ggnet.com/install.sh | bash -
```

**That's it!** ☕ Grab a coffee and wait 10-15 minutes.

---

## 📋 **REQUIREMENTS:**

- **OS:** Debian 11/12 or Ubuntu 20.04/22.04 LTS Server
- **Access:** Root/sudo privileges
- **Network:** Internet connection
- **Hardware:** 4GB RAM, 2+ CPU cores, 2+ storage drives

---

## 🎯 **INSTALLATION PROCESS:**

### **1. Fresh Server:**
- Install Debian or Ubuntu Server
- Login as root

### **2. Run Installer:**
```bash
wget -O - https://ggnet.com/install.sh | bash -
```

### **3. Confirm:**
- Script shows what will be installed
- Type `yes` to continue

### **4. Wait:**
- Installation runs automatically
- Progress shown for each step
- Takes 10-15 minutes

### **5. Reboot:**
- Script asks to reboot
- Type `yes` to reboot now

### **6. Configure:**
```bash
# After reboot, run:
ggnet-configurator
```

### **7. Setup Storage:**
```bash
# Example: ZFS Mirror
zpool create pool0 mirror /dev/sdb /dev/sdc

# Example: MD RAID10
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{b,c,d,e}
```

### **8. Start ggNet:**
```bash
systemctl start ggnet-backend
```

### **9. Access Web UI:**
- Open browser: `http://your-server-ip/`
- Login with default credentials
- Configure your gaming center!

---

## ✅ **WHAT GETS INSTALLED:**

- ✅ Python 3 + FastAPI backend
- ✅ PostgreSQL database
- ✅ React frontend
- ✅ Nginx web server
- ✅ ZFS utilities
- ✅ MD RAID utilities
- ✅ DHCP/TFTP/NFS servers
- ✅ Monitoring tools
- ✅ System utilities

**Total:** ~500MB download, ~2GB installed

---

## 🔧 **QUICK COMMANDS:**

```bash
# Start ggNet
sudo systemctl start ggnet-backend

# Stop ggNet
sudo systemctl stop ggnet-backend

# Check status
sudo systemctl status ggnet-backend

# View logs
sudo journalctl -u ggnet-backend -f

# Check health
curl http://localhost:8000/health

# Run configurator
ggnet-configurator
```

---

## 🌐 **ACCESS POINTS:**

- **Web UI:** `http://server-ip/`
- **API:** `http://server-ip:8000`
- **API Docs:** `http://server-ip:8000/docs`
- **Health:** `http://server-ip:8000/health`
- **Metrics:** `http://server-ip:9100/metrics`

---

## 📖 **FULL GUIDES:**

For detailed instructions:

1. **Installation:** `DEPLOYMENT_GUIDE.md`
2. **Hardware Testing:** `REAL_HARDWARE_TESTING_GUIDE.md`
3. **Installer Details:** `INSTALLER_GUIDE.md`
4. **Testing:** `COMPLETE_TEST_SUITE_SUMMARY.md`

---

## 💡 **TIPS:**

- ☕ Installation takes 10-15 min - grab a coffee!
- 🔄 Reboot after installation
- ⚙️ Run `ggnet-configurator` to check status
- 📚 Documentation in `/srv/ggnet/docs/`
- 🆘 View logs: `journalctl -u ggnet-backend -f`

---

## 🎉 **THAT'S IT!**

From zero to ggNet in 15 minutes! 🚀

**Simple. Fast. Automated.**

---

**Inspired by:** [ggRock Install Guide](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15861727/IV.+-+Install+the+ggRock+Server+Application)

