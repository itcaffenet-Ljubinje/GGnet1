# 🚀 Self-Hosted Runner Setup Guide

Complete guide for setting up GitHub Actions self-hosted runner for ggNet deployment.

---

## Table of Contents

1. [What is Self-Hosted Runner?](#what-is-self-hosted-runner)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## What is Self-Hosted Runner?

**Self-hosted runner** = GitHub Actions runs on **your server** instead of GitHub's servers.

### Benefits:
- ✅ **Faster deployment** - No SSH overhead
- ✅ **Direct access** - To local resources
- ✅ **Full control** - Over environment
- ✅ **Free** - Unlimited minutes
- ✅ **Security** - Code stays on your server

### Architecture:
```
GitHub Actions Workflow
         ↓
    Self-Hosted Runner (Your Debian Server)
         ↓
    Deploy ggNet directly
```

---

## Prerequisites

### Server Requirements:
- **OS**: Debian 11+ or Ubuntu 20.04+
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: 50GB+ free space
- **Network**: Internet access for GitHub
- **User**: Root or sudo access

### Software:
- Python 3.10+
- Node.js 18+
- Nginx
- systemd
- curl, wget, git

---

## Setup Instructions

### Step 1: Prepare Your Server

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  nodejs \
  npm \
  nginx \
  sqlite3 \
  curl \
  wget \
  git \
  jq

# Create ggnet user (optional but recommended)
sudo useradd -m -s /bin/bash ggnet
sudo usermod -aG sudo ggnet
```

### Step 2: Add Runner to GitHub Repository

1. **Go to GitHub Repository Settings:**
   ```
   https://github.com/itcaffenet-Ljubinje/GGnet1/settings/actions/runners
   ```

2. **Click "New self-hosted runner"**

3. **Select:**
   - Operating System: Linux
   - Architecture: x64

4. **Copy the registration commands** (you'll see something like):
   ```bash
   # Create a folder
   mkdir actions-runner && cd actions-runner
   
   # Download the latest runner package
   curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
   
   # Extract the installer
   tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
   
   # Configure the runner
   ./config.sh --url https://github.com/itcaffenet-Ljubinje/GGnet1 --token AXXXXXXXXXXXXXXXXXXXXX
   ```

### Step 3: Install Runner on Server

```bash
# On your Debian server
cd /opt

# Create actions-runner directory
sudo mkdir actions-runner
sudo chown $USER:$USER actions-runner
cd actions-runner

# Download runner (use version from GitHub)
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure
./config.sh --url https://github.com/itcaffenet-Ljubinje/GGnet1 --token YOUR_TOKEN_HERE
```

**Configuration Options:**
```
Enter the name of the runner: [press Enter for default]
Enter the name of the work folder: [press Enter for _work]

# Select how to run the runner
1. Run as a service (recommended)
2. Run interactively

# Choose option 1
Enter the name of the user: [press Enter for current user]

# Confirm
```

### Step 4: Install as Systemd Service

```bash
# Install runner as service
sudo ./svc.sh install

# Start the service
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

### Step 5: Verify Runner is Online

1. Go back to GitHub:
   ```
   https://github.com/itcaffenet-Ljubinje/GGnet1/settings/actions/runners
   ```

2. You should see your runner listed with a green dot ✅

---

## Verification

### Test the Runner

```bash
# Check runner service
sudo systemctl status actions.runner.itcaffenet-Ljubinje-GGnet1.*.service

# Check runner logs
sudo journalctl -u actions.runner.itcaffenet-Ljubinje-GGnet1.*.service -f

# Test connectivity
curl https://api.github.com
```

### Run Test Workflow

1. **Go to Actions tab:**
   ```
   https://github.com/itcaffenet-Ljubinje/GGnet1/actions
   ```

2. **Select "Debian Production Deployment"**

3. **Click "Run workflow"**

4. **Select:**
   - Branch: `ggnet-refactor`
   - Environment: `production`

5. **Click "Run workflow"**

6. **Watch it run on your self-hosted runner!** 🎉

---

## Troubleshooting

### Runner Not Appearing in GitHub

**Problem:** Runner doesn't show up in GitHub settings

**Solution:**
```bash
# Check if runner is running
sudo systemctl status actions.runner.itcaffenet-Ljubinje-GGnet1.*.service

# Check logs
sudo journalctl -u actions.runner.itcaffenet-Ljubinje-GGnet1.*.service -n 50

# Restart runner
sudo ./svc.sh stop
sudo ./svc.sh start
```

### Runner Offline

**Problem:** Runner shows as offline in GitHub

**Solution:**
```bash
# Check internet connectivity
ping github.com

# Check if runner process is running
ps aux | grep Runner.Listener

# Restart service
sudo ./svc.sh restart

# Check firewall
sudo ufw status
```

### Permission Denied Errors

**Problem:** Runner can't access files or run commands

**Solution:**
```bash
# Check runner user
cat /etc/systemd/system/actions.runner.*.service | grep User

# Fix permissions
sudo chown -R ggnet:ggnet /opt/ggnet
sudo chown -R ggnet:ggnet /opt/actions-runner

# Add to sudoers (if needed)
sudo visudo
# Add: ggnet ALL=(ALL) NOPASSWD: ALL
```

### Workflow Fails with "Permission Denied"

**Problem:** Can't create directories or run scripts

**Solution:**
```bash
# Make scripts executable
chmod +x /opt/ggnet/scripts/*.sh

# Fix ownership
sudo chown -R $USER:$USER /opt/ggnet

# Check sudo access
sudo -v
```

### Service Won't Start

**Problem:** systemd service fails to start

**Solution:**
```bash
# Check service status
sudo systemctl status actions.runner.*.service

# View detailed logs
sudo journalctl -xe

# Reinstall service
sudo ./svc.sh uninstall
sudo ./svc.sh install
sudo ./svc.sh start
```

### Runner Can't Connect to GitHub

**Problem:** Connection timeout or SSL errors

**Solution:**
```bash
# Test connectivity
curl -I https://github.com

# Check DNS
nslookup github.com

# Check proxy (if behind one)
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Configure proxy if needed
./config.sh --url https://github.com/... --token ... --proxyurl http://proxy:port
```

---

## Advanced Configuration

### Multiple Runners

To run multiple runners on the same server:

```bash
# Create second runner
cd /opt
sudo mkdir actions-runner-2
cd actions-runner-2

# Download and extract
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure with different name
./config.sh --url https://github.com/... --token ... --name "runner-2"

# Install as separate service
sudo ./svc.sh install
sudo ./svc.sh start
```

### Labels

Add custom labels to runners:

```bash
# Add label during configuration
./config.sh --url https://github.com/... --token ... --labels "debian,production,ggnet"

# Or add later
./config.sh --url https://github.com/... --token ... --labels "debian,production,ggnet" --replace
```

### Environment Variables

Set environment variables for runner:

```bash
# Edit service file
sudo systemctl edit actions.runner.*.service

# Add environment variables
[Service]
Environment="GGNET_ENV=production"
Environment="GGNET_LOG_LEVEL=info"
```

### Resource Limits

Set resource limits for runner:

```bash
# Edit service file
sudo systemctl edit actions.runner.*.service

# Add resource limits
[Service]
MemoryLimit=2G
CPUQuota=200%
```

---

## Maintenance

### Update Runner

```bash
# Stop service
sudo ./svc.sh stop

# Download latest version
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz --overwrite

# Start service
sudo ./svc.sh start
```

### Remove Runner

```bash
# Stop and uninstall service
sudo ./svc.sh stop
sudo ./svc.sh uninstall

# Remove runner from GitHub (via web interface)
# https://github.com/itcaffenet-Ljubinje/GGnet1/settings/actions/runners

# Delete files
cd /opt
sudo rm -rf actions-runner
```

### Backup Runner Configuration

```bash
# Backup runner config
sudo cp -r /opt/actions-runner /opt/actions-runner.backup

# Backup service files
sudo cp /etc/systemd/system/actions.runner.*.service /opt/actions-runner.backup/
```

---

## Security Best Practices

1. **Run as Non-Root User:**
   ```bash
   # Create dedicated user
   sudo useradd -m -s /bin/bash runner
   sudo usermod -aG sudo runner
   ```

2. **Restrict Network Access:**
   ```bash
   # Allow only GitHub IPs
   sudo ufw allow from 140.82.112.0/20 to any port 443
   sudo ufw allow from 143.55.64.0/20 to any port 443
   ```

3. **Use SSH Keys:**
   ```bash
   # Disable password authentication
   sudo nano /etc/ssh/sshd_config
   # PasswordAuthentication no
   sudo systemctl restart sshd
   ```

4. **Regular Updates:**
   ```bash
   # Update system regularly
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

5. **Monitor Logs:**
   ```bash
   # Set up log rotation
   sudo nano /etc/logrotate.d/actions-runner
   ```

---

## Support

**Issues or Questions?**
- 📧 Open an issue on GitHub
- 📚 Check GitHub Actions documentation
- 🔍 Review runner logs

**Useful Commands:**
```bash
# Check runner status
sudo systemctl status actions.runner.*.service

# View logs
sudo journalctl -u actions.runner.*.service -f

# Restart runner
sudo ./svc.sh restart

# Check runner version
./run.sh --version
```

---

**Last Updated:** 2025-10-15
**Runner Version:** 2.311.0
**Status:** Production Ready ✅

