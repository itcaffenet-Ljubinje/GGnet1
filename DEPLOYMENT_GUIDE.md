# 🚀 ggNet DEPLOYMENT GUIDE

**Production Deployment na Linux Server**

---

## 📋 **TABLE OF CONTENTS**

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Server Requirements](#server-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Production Startup](#production-startup)
7. [Monitoring](#monitoring)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## ✅ **PRE-DEPLOYMENT CHECKLIST:**

Pre nego što započneš deployment:

### **Planning:**
- [ ] ✅ Identifikovao si target server
- [ ] ✅ Proverio si hardware requirements
- [ ] ✅ Planirao si storage array konfiguraciju
- [ ] ✅ Rezervisao si IP adrese (static)
- [ ] ✅ Pripremio si DNS records
- [ ] ✅ Napravio si backup plan

### **Access:**
- [ ] ✅ Imaš SSH pristup serveru
- [ ] ✅ Imaš sudo/root privilegije
- [ ] ✅ Imaš console access (iLO/iDRAC)
- [ ] ✅ Možeš da restartuješ server

### **Testing:**
- [ ] ✅ Unit testovi prolaze (59/59)
- [ ] ✅ Integration testovi prolaze (21/21)
- [ ] ✅ Frontend build uspešan
- [ ] ✅ Lokalno testiranje završeno

---

## 💻 **SERVER REQUIREMENTS:**

### **Minimum:**
- **OS:** Debian 11/12 ili Ubuntu 20.04/22.04 LTS Server
- **CPU:** 2 cores (Intel Xeon/AMD EPYC)
- **RAM:** 4GB
- **Storage:** 
  - 100GB OS disk (SSD preporučeno)
  - 2+ diskova za array (identični)
- **Network:** 1Gbps Ethernet

### **Preporučeno:**
- **OS:** Ubuntu 22.04 LTS Server
- **CPU:** 4+ cores @ 2.4GHz+
- **RAM:** 8-16GB ECC
- **Storage:**
  - 250GB NVMe OS disk
  - 4-10x 1.92TB SSD za array (identični model)
- **Network:** 10Gbps Ethernet (dual port)
- **RAID Controller:** HBA mode (ako postoji)

### **Production:**
- **OS:** Ubuntu 22.04 LTS Server
- **CPU:** 8+ cores (Intel Xeon Silver/Gold)
- **RAM:** 32GB+ ECC
- **Storage:**
  - 500GB NVMe OS disk (RAID1)
  - 10+ x 3.84TB NVMe SSD za array
- **Network:** 25Gbps Ethernet (bonded)
- **Redundancy:** Dual PSU, IPMI/iLO

---

## 🔧 **INSTALLATION STEPS:**

### **STEP 1: Server Preparation** (5 min)

```bash
# 1. SSH na server
ssh root@your-server-ip

# 2. Update sistema
apt-get update && apt-get upgrade -y

# 3. Install git
apt-get install -y git

# 4. Preuzmi kod
cd /opt
git clone https://github.com/your-org/ggnet.git
cd ggnet
```

---

### **STEP 2: System Setup** (10 min)

```bash
# Pokreni Linux server setup
cd backend
chmod +x scripts/setup_linux_server.sh
sudo bash scripts/setup_linux_server.sh
```

**Ovaj script instalira:**
- ✅ Python 3 + pip + venv
- ✅ PostgreSQL database
- ✅ ZFS utilities (zpool, zfs)
- ✅ MD RAID utilities (mdadm)
- ✅ Network services (DHCP, TFTP, NFS)
- ✅ Monitoring tools (Prometheus)
- ✅ Systemd service files

---

### **STEP 3: Storage Array Setup** (15-30 min)

#### **Option A: ZFS (Preporučeno)**

```bash
# 1. Proveri dostupne diskove
lsblk

# 2. Kreiraj ZFS pool
# RAID1 (mirror) - 2 diska:
zpool create pool0 mirror /dev/sdb /dev/sdc

# RAID10 (striped mirrors) - 4 diska:
zpool create pool0 mirror /dev/sdb /dev/sdc mirror /dev/sdd /dev/sde

# RAIDZ2 (double parity) - 6+ diskova:
zpool create pool0 raidz2 /dev/sdb /dev/sdc /dev/sdd /dev/sde /dev/sdf /dev/sdg

# 3. Proveri status
zpool status pool0
zpool list pool0

# 4. Kreiraj filesystems
zfs create pool0/images
zfs create pool0/writebacks
zfs create pool0/snapshots

# 5. Set mountpoints
zfs set mountpoint=/srv/ggnet/array/images pool0/images
zfs set mountpoint=/srv/ggnet/array/writebacks pool0/writebacks
zfs set mountpoint=/srv/ggnet/array/snapshots pool0/snapshots

# 6. Set compression (optional, preporučeno)
zfs set compression=lz4 pool0

# 7. Set permissions
chown -R ggnet:ggnet /srv/ggnet/array
```

#### **Option B: MD RAID**

```bash
# 1. Kreiraj RAID array
# RAID1 - 2 diska:
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# RAID10 - 4 diska:
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{b,c,d,e}

# 2. Format i mount
mkfs.ext4 /dev/md0
mkdir -p /srv/ggnet/array
mount /dev/md0 /srv/ggnet/array

# 3. Add to fstab
echo "/dev/md0 /srv/ggnet/array ext4 defaults 0 2" >> /etc/fstab

# 4. Kreiraj direktorijume
mkdir -p /srv/ggnet/array/{images,writebacks,snapshots}
chown -R ggnet:ggnet /srv/ggnet/array
```

---

### **STEP 4: Backend Setup** (5 min)

```bash
# 1. Kopiraj backend kod
sudo cp -r /opt/ggnet/backend /srv/ggnet/

# 2. Promeni na ggnet user
sudo su - ggnet

# 3. Setup backend
cd /srv/ggnet/backend
bash scripts/setup_backend.sh
```

---

### **STEP 5: Database Configuration** (2 min)

```bash
# Kao postgres user
sudo -u postgres psql << EOF
CREATE DATABASE ggnet;
CREATE USER ggnet WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE ggnet TO ggnet;
\q
EOF

# Update .env fajl
sudo -u ggnet nano /srv/ggnet/backend/.env
# Promeni DATABASE_URL i SECRET_KEY
```

---

### **STEP 6: Network Configuration** (10 min)

```bash
# 1. Configure DHCP
sudo nano /etc/dhcp/dhcpd.conf

# Add:
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option domain-name-servers 8.8.8.8;
    next-server 192.168.1.10;  # PXE server (this server)
    filename "pxelinux.0";
}

# 2. Restart DHCP
sudo systemctl restart isc-dhcp-server

# 3. Configure TFTP
sudo nano /etc/default/tftpd-hpa

# Set:
TFTP_DIRECTORY="/srv/ggnet/tftp"
TFTP_OPTIONS="--secure"

sudo systemctl restart tftpd-hpa

# 4. Configure NFS
sudo nano /etc/exports

# Add:
/srv/ggnet/array/images *(ro,sync,no_subtree_check)
/srv/ggnet/array/writebacks *(rw,sync,no_subtree_check)

sudo exportfs -a
sudo systemctl restart nfs-kernel-server
```

---

## ⚙️ **CONFIGURATION:**

### **Environment Variables (.env):**

```bash
# Production configuration
DATABASE_URL=postgresql+asyncpg://ggnet:SECURE_PASSWORD@localhost/ggnet
SECRET_KEY=your-32-char-hex-key
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production

# Storage paths
STORAGE_ROOT=/srv/ggnet/array
IMAGES_PATH=/srv/ggnet/array/images
WRITEBACKS_PATH=/srv/ggnet/array/writebacks
SNAPSHOTS_PATH=/srv/ggnet/array/snapshots

# Array settings
DEFAULT_ARRAY_TYPE=zfs
RESERVED_SPACE_PERCENT=15

# Dry-run mode (for testing)
GGNET_DRY_RUN=false

# Feature flags
ENABLE_AUTO_DISCOVERY=true
ENABLE_METRICS=true
ENABLE_WEBHOOKS=false
```

---

## 🧪 **TESTING:**

### **1. Safe Detection Tests:**

```bash
cd /srv/ggnet/backend
source venv/bin/activate

# Test array detection
pytest tests/test_real_hardware.py::TestRealHardwareDetection -v -s

# Test commands availability
pytest tests/test_real_hardware.py::TestRealHardwareReadOnly -v -s
```

### **2. Dry-Run Mode Testing:**

```bash
# Enable dry-run
export GGNET_DRY_RUN=true

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Test API (neće izvršiti stvarne komande)
curl -X POST http://localhost:8000/api/v1/storage/array/stripes \
  -H "Content-Type: application/json" \
  -d '{
    "stripe_number": 1,
    "raid_type": "mirror",
    "devices": ["sdd", "sde"]
  }'

# Check logs (trebalo bi da kaže "DRY RUN")
tail -f /var/log/ggnet/backend.log
```

### **3. Live Testing:**

```bash
# Disable dry-run
export GGNET_DRY_RUN=false

# Test with real API calls
curl http://localhost:8000/api/v1/storage/array/status | jq
curl http://localhost:8000/api/v1/storage/array/available-drives | jq
```

---

## 🚀 **PRODUCTION STARTUP:**

### **Manual Start:**

```bash
sudo su - ggnet
cd /srv/ggnet/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Systemd Service (Preporučeno):**

```bash
# Enable service
sudo systemctl enable ggnet-backend

# Start service
sudo systemctl start ggnet-backend

# Check status
sudo systemctl status ggnet-backend

# View logs
sudo journalctl -u ggnet-backend -f
```

### **With Nginx Reverse Proxy:**

```bash
# Install Nginx
sudo apt-get install -y nginx

# Configure
sudo nano /etc/nginx/sites-available/ggnet

# Add:
server {
    listen 80;
    server_name ggnet.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Enable
sudo ln -s /etc/nginx/sites-available/ggnet /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 📊 **MONITORING:**

### **1. System Monitoring:**

```bash
# Check services
sudo systemctl status ggnet-backend
sudo systemctl status postgresql
sudo systemctl status nginx

# Check resources
htop
df -h
zpool iostat 1  # For ZFS
cat /proc/mdstat  # For MD RAID

# Check logs
sudo journalctl -u ggnet-backend -f
tail -f /var/log/ggnet/backend.log
```

### **2. API Health Checks:**

```bash
# Health endpoint
curl http://localhost:8000/health

# Array status
curl http://localhost:8000/api/v1/storage/array/status

# Metrics endpoint (if enabled)
curl http://localhost:8000/metrics
```

### **3. Prometheus Integration:**

```bash
# View node exporter metrics
curl http://localhost:9100/metrics

# Configure Prometheus to scrape ggNet
sudo nano /etc/prometheus/prometheus.yml

# Add:
scrape_configs:
  - job_name: 'ggnet-backend'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

# Restart Prometheus
sudo systemctl restart prometheus
```

---

## 💾 **BACKUP & RECOVERY:**

### **Database Backup:**

```bash
# Manual backup
sudo -u postgres pg_dump ggnet > /backup/ggnet_$(date +%Y%m%d).sql

# Automated backup (cron)
sudo crontab -e

# Add:
0 2 * * * /usr/bin/pg_dump -U postgres ggnet > /backup/ggnet_$(date +\%Y\%m\%d).sql
```

### **ZFS Snapshots:**

```bash
# Create snapshot
zfs snapshot pool0/images@backup_$(date +%Y%m%d)

# List snapshots
zfs list -t snapshot

# Restore snapshot
zfs rollback pool0/images@backup_20251021

# Auto-snapshot (cron)
0 */4 * * * /usr/sbin/zfs snapshot pool0/images@auto_$(date +\%Y\%m\%d_\%H\%M)
```

### **Configuration Backup:**

```bash
# Backup config files
tar -czf /backup/ggnet_config_$(date +%Y%m%d).tar.gz \
  /srv/ggnet/backend/.env \
  /etc/systemd/system/ggnet-backend.service \
  /etc/nginx/sites-available/ggnet \
  /etc/dhcp/dhcpd.conf
```

---

## 🐛 **TROUBLESHOOTING:**

### **Problem 1: Service won't start**

```bash
# Check logs
sudo journalctl -u ggnet-backend -n 50

# Check permissions
ls -la /srv/ggnet/backend
ls -la /srv/ggnet/array

# Fix permissions
sudo chown -R ggnet:ggnet /srv/ggnet
```

### **Problem 2: Database connection failed**

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
sudo -u ggnet psql -h localhost -U ggnet -d ggnet

# Reset password
sudo -u postgres psql
ALTER USER ggnet WITH PASSWORD 'new-password';
```

### **Problem 3: Array not detected**

```bash
# For ZFS:
zpool list
zpool import -a  # Import all pools
zpool status

# For MD RAID:
cat /proc/mdstat
mdadm --detail --scan
mdadm --assemble --scan
```

### **Problem 4: API returns 500 errors**

```bash
# Check logs
tail -f /var/log/ggnet/backend.log

# Check storage manager
sudo -u ggnet python3 << EOF
from core.storage_manager import get_storage_manager
manager = get_storage_manager()
print(f"Array Type: {manager.array_type}")
print(f"Array Name: {manager.array_name}")
status = manager.get_array_status()
print(f"Status: {status}")
EOF
```

---

## 🔒 **SECURITY:**

### **Firewall:**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend API (internal only)
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Allow DHCP/TFTP/NFS (internal only)
sudo ufw allow from 192.168.1.0/24 to any port 67 proto udp
sudo ufw allow from 192.168.1.0/24 to any port 69 proto udp
sudo ufw allow from 192.168.1.0/24 to any port 2049

# Status
sudo ufw status
```

### **SSL/TLS:**

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d ggnet.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 📈 **PERFORMANCE TUNING:**

### **ZFS Tuning:**

```bash
# Set ARC size (50% of RAM)
echo "options zfs zfs_arc_max=17179869184" >> /etc/modprobe.d/zfs.conf

# Disable atime
zfs set atime=off pool0

# Enable LZ4 compression
zfs set compression=lz4 pool0

# Set recordsize (for VM images)
zfs set recordsize=64K pool0/images
```

### **System Tuning:**

```bash
# Edit sysctl
sudo nano /etc/sysctl.conf

# Add:
vm.swappiness=10
net.core.rmem_max=134217728
net.core.wmem_max=134217728
net.ipv4.tcp_rmem=4096 87380 67108864
net.ipv4.tcp_wmem=4096 65536 67108864
fs.file-max=2097152

# Apply
sudo sysctl -p
```

---

## 📊 **MONITORING DASHBOARD:**

### **Grafana Setup:**

```bash
# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Access: http://your-server-ip:3000
# Default: admin/admin
```

### **Add ggNet Dashboard:**

1. Open Grafana (http://server:3000)
2. Add Prometheus data source (http://localhost:9090)
3. Import dashboard or create custom
4. Monitor:
   - CPU usage
   - RAM usage
   - Disk I/O
   - Network traffic
   - Array health
   - API response times

---

## ✅ **POST-DEPLOYMENT VERIFICATION:**

### **Checklist:**

```bash
# 1. Service running
sudo systemctl is-active ggnet-backend
# Expected: active

# 2. API responding
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 3. Array detected
curl http://localhost:8000/api/v1/storage/array/status | jq '.exists'
# Expected: true

# 4. Devices listed
curl http://localhost:8000/api/v1/storage/array/status | jq '.devices | length'
# Expected: 2+ (broj diskova u array-u)

# 5. Frontend can connect
curl -I http://server-ip/api/v1/storage/array/status
# Expected: HTTP/1.1 200 OK

# 6. Logs clean
sudo journalctl -u ggnet-backend --since "5 minutes ago" | grep ERROR
# Expected: No critical errors

# 7. Database connected
sudo -u ggnet psql -h localhost -U ggnet -d ggnet -c "SELECT 1;"
# Expected: 1

# 8. Disk performance
sudo dd if=/dev/zero of=/srv/ggnet/array/images/test bs=1M count=1000 oflag=direct
# Expected: 500+ MB/s
```

---

## 🎯 **QUICK COMMANDS:**

```bash
# Start backend
sudo systemctl start ggnet-backend

# Stop backend
sudo systemctl stop ggnet-backend

# Restart backend
sudo systemctl restart ggnet-backend

# View logs
sudo journalctl -u ggnet-backend -f

# Check array
zpool status  # For ZFS
cat /proc/mdstat  # For MD RAID

# Check API
curl http://localhost:8000/health

# Run tests
cd /srv/ggnet/backend
source venv/bin/activate
pytest tests/ -v
```

---

## 📞 **SUPPORT:**

### **Logs Location:**
- **Backend:** `/var/log/ggnet/backend.log`
- **Systemd:** `journalctl -u ggnet-backend`
- **PostgreSQL:** `/var/log/postgresql/`
- **Nginx:** `/var/log/nginx/`
- **ZFS:** `zpool events`
- **MD RAID:** `dmesg | grep md`

### **Status Commands:**
```bash
# All ggNet services
sudo systemctl status ggnet-*

# Storage health
zpool status -v  # ZFS
mdadm --detail /dev/md0  # MD RAID

# System health
top
iostat -x 1
```

---

## 🎉 **ZAKLJUČAK:**

**Deployment steps:**
1. ✅ Pripremi server (10 min)
2. ✅ Setup system (10 min)
3. ✅ Kreiraj array (15-30 min)
4. ✅ Setup backend (5 min)
5. ✅ Configure network (10 min)
6. ✅ Test (30 min)
7. ✅ Deploy (5 min)

**Total time:** ~1.5-2 hours

**Status check:**
- Backend API: http://server-ip:8000
- Health: http://server-ip:8000/health
- Storage status: http://server-ip:8000/api/v1/storage/array/status
- Metrics: http://server-ip:8000/metrics

**Production ready!** 🚀

---

**Za pitanja i support, vidi dokumentaciju ili kontaktiraj tim.** ✨
