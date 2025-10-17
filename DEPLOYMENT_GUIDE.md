# 🚀 ggNet Deployment Guide

Complete guide for deploying ggNet to Debian/Ubuntu servers.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Manual Installation](#manual-installation)
3. [Automated Deployment (GitHub Actions)](#automated-deployment-github-actions)
4. [Production Setup](#production-setup)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: One-Command Install (Recommended)

```bash
# On your Debian/Ubuntu server
git clone https://github.com/itcaffenet-Ljubinje/GGnet1.git
cd GGnet1
chmod +x scripts/install.sh
sudo bash scripts/install.sh
```

### Option 2: Automated via GitHub Actions

1. Configure GitHub Secrets (see below)
2. Push to `main` branch
3. Deployment runs automatically

---

## Manual Installation

### Prerequisites

- **OS**: Debian 11+ or Ubuntu 20.04+
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: 50GB+ free space
- **Network**: Static IP address
- **User**: Root or sudo access

### Step 1: Clone Repository

```bash
cd /opt
git clone https://github.com/itcaffenet-Ljubinje/GGnet1.git ggnet
cd ggnet
```

### Step 2: Run Installation Script

```bash
chmod +x scripts/install.sh
sudo bash scripts/install.sh
```

**What the installer does:**
- ✅ Updates system packages
- ✅ Installs Python 3, Node.js, Nginx, SQLite
- ✅ Creates `ggnet` user and directories
- ✅ Sets up Python virtual environment
- ✅ Installs backend dependencies
- ✅ Builds frontend production bundle
- ✅ Initializes SQLite database
- ✅ Configures systemd services
- ✅ Sets up Nginx reverse proxy
- ✅ Enables and starts services

### Step 3: Verify Installation

```bash
# Check services
sudo systemctl status ggnet-backend
sudo systemctl status nginx

# Test API
curl http://localhost:8080/api/status

# Test frontend
curl http://localhost
```

### Step 4: Access Web Interface

Open browser and navigate to:
- **Frontend**: `http://your-server-ip`
- **Backend API**: `http://your-server-ip:8080`
- **API Docs**: `http://your-server-ip/docs`

---

## Automated Deployment (GitHub Actions)

### Setup GitHub Secrets

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@ggnet"
   # Save as: ~/.ssh/github_actions_rsa
   ```

2. **Copy Public Key to Server:**
   ```bash
   ssh-copy-id -i ~/.ssh/github_actions_rsa.pub user@your-server.com
   ```

3. **Add Secrets to GitHub:**
   - Go to: `Settings → Secrets and variables → Actions`
   - Add these secrets:
     ```
     SSH_PRIVATE_KEY       # Contents of ~/.ssh/github_actions_rsa
     DEBIAN_SERVER_HOST    # your-server.com or IP
     DEBIAN_SERVER_USER    # SSH username
     ```

### Deploy

**Automatic (on push to main):**
```bash
git checkout main
git merge ggnet-refactor
git push origin main
# Deployment starts automatically
```

**Manual:**
1. Go to GitHub Actions tab
2. Select "Debian Production Deployment"
3. Click "Run workflow"
4. Select environment
5. Click "Run workflow"

### What Happens During Deployment

1. 🔐 SSH connection established
2. 💾 Existing installation backed up
3. 🛑 Services stopped
4. 📦 Files synced to server
5. 🔧 Installation script runs
6. ✅ Installation verified
7. 🚀 Services started
8. 🏥 Health checks run
9. 📊 Deployment summary shown

---

## Production Setup

### 1. Firewall Configuration

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8080/tcp  # Backend API (optional, if not using Nginx proxy)
sudo ufw enable
```

### 2. SSL/TLS Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### 3. Configure Nginx for Production

Edit `/etc/nginx/sites-available/ggnet`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        root /opt/ggnet/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Database Backup

Create cron job for automatic backups:

```bash
# Edit crontab
sudo crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * /opt/ggnet/scripts/backup-db.sh
```

Create backup script:

```bash
#!/bin/bash
# /opt/ggnet/scripts/backup-db.sh

BACKUP_DIR="/opt/ggnet/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ggnet-$TIMESTAMP.db"

# Backup database
cp /opt/ggnet/backend/ggnet.db "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "ggnet-*.db.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_FILE.gz"
```

### 5. Monitoring

**System Resources:**
```bash
# Install monitoring tools
sudo apt-get install htop iotop

# Check system status
htop
iotop
df -h
free -h
```

**Service Logs:**
```bash
# Backend logs
sudo journalctl -u ggnet-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -xe
```

### 6. Performance Tuning

**Backend (systemd service):**
Edit `/etc/systemd/system/ggnet-backend.service`:

```ini
[Service]
# Increase worker processes
Environment="WORKERS=4"

# Memory limits
LimitNOFILE=65536
MemoryMax=2G
```

**Nginx:**
Edit `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_connections 1024;

# Gzip compression
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript;
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status ggnet-backend

# View logs
sudo journalctl -u ggnet-backend -n 50

# Check if port is in use
sudo netstat -tulpn | grep :8080

# Restart service
sudo systemctl restart ggnet-backend
```

### Database Issues

```bash
# Check database file
ls -lh /opt/ggnet/backend/ggnet.db

# Check database integrity
sqlite3 /opt/ggnet/backend/ggnet.db "PRAGMA integrity_check;"

# Backup and recreate
cp /opt/ggnet/backend/ggnet.db /opt/ggnet/backend/ggnet.db.backup
cd /opt/ggnet/backend
source venv/bin/activate
python -c "from src.db.base import init_db; import asyncio; asyncio.run(init_db())"
```

### Frontend Not Loading

```bash
# Check Nginx config
sudo nginx -t

# Check frontend build
ls -lh /opt/ggnet/frontend/dist/

# Rebuild frontend
cd /opt/ggnet/frontend
npm install
npm run build

# Restart Nginx
sudo systemctl restart nginx
```

### API Not Responding

```bash
# Test backend directly
curl http://localhost:8080/api/status

# Test through Nginx
curl http://localhost/api/status

# Check CORS settings
cat /opt/ggnet/backend/.env | grep CORS

# Check firewall
sudo ufw status
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ggnet:ggnet /opt/ggnet

# Fix permissions
sudo chmod +x /opt/ggnet/backend/run.py
sudo chmod +x /opt/ggnet/scripts/*.sh

# Check systemd service user
cat /etc/systemd/system/ggnet-backend.service | grep User
```

### Low Disk Space

```bash
# Check disk usage
df -h

# Clean old logs
sudo journalctl --vacuum-time=7d

# Remove old backups
find /opt/ggnet/backups -name "*.db.gz" -mtime +30 -delete

# Clean npm cache
cd /opt/ggnet/frontend
npm cache clean --force

# Clean pip cache
cd /opt/ggnet/backend
source venv/bin/activate
pip cache purge
```

---

## Uninstallation

### Safe Uninstall

```bash
cd /opt/ggnet
sudo bash scripts/uninstall.sh
```

**What it does:**
- 🛑 Stops services
- 🗑️ Removes systemd units
- 🗑️ Removes Nginx config
- 🗑️ Deletes application files
- 💾 Optionally backs up data

### Manual Uninstall

```bash
# Stop services
sudo systemctl stop ggnet-backend
sudo systemctl disable ggnet-backend

# Remove systemd files
sudo rm /etc/systemd/system/ggnet-backend.service
sudo rm /etc/systemd/system/ggnet-frontend.service

# Remove Nginx config
sudo rm /etc/nginx/sites-enabled/ggnet
sudo rm /etc/nginx/sites-available/ggnet
sudo systemctl reload nginx

# Remove application
sudo rm -rf /opt/ggnet

# Remove user (optional)
sudo userdel -r ggnet
```

---

## Support

**Issues or Questions?**
- 📧 Open an issue on GitHub
- 📚 Check documentation in `README.md`
- 🔍 Review logs: `sudo journalctl -u ggnet-backend`

**Useful Commands:**
```bash
# Service management
sudo systemctl start ggnet-backend
sudo systemctl stop ggnet-backend
sudo systemctl restart ggnet-backend
sudo systemctl status ggnet-backend

# Logs
sudo journalctl -u ggnet-backend -f
sudo tail -f /var/log/nginx/error.log

# Database
sqlite3 /opt/ggnet/backend/ggnet.db

# Configuration
cat /opt/ggnet/backend/.env
cat /etc/nginx/sites-available/ggnet
```

---

**Last Updated:** 2025-10-15
**Version:** 1.0.0

