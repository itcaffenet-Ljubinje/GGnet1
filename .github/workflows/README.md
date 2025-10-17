# GitHub Actions Workflows

This directory contains CI/CD workflows for the ggNet project.

## Available Workflows

### 1. `ci.yml` - Main CI Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
- **Backend Tests**: Runs pytest on backend code
- **Frontend Build**: Builds React frontend with Vite
- **PXE Validation**: Validates PXE configuration files
- **Scripts Validation**: Checks bash script syntax
- **Documentation Check**: Verifies documentation exists

**Usage:**
```bash
# Automatically runs on push/PR
# Or manually trigger from GitHub Actions tab
```

---

### 2. `debian-install-test.yml` - Installation Testing

**Triggers:**
- Push to `main`, `develop`, or `ggnet-refactor` branches
- Pull requests to `main` or `develop`
- Manual trigger (workflow_dispatch)

**Purpose:**
Tests the `scripts/install.sh` script on a Debian-based system (Ubuntu runner).

**What it does:**
1. ✅ Installs prerequisites (Python, Node.js, Nginx, etc.)
2. ✅ Runs system check script
3. ✅ Executes installation script
4. ✅ Verifies installation structure
5. ✅ Checks Python virtual environment
6. ✅ Validates backend dependencies
7. ✅ Verifies frontend build
8. ✅ Tests database initialization
9. ✅ Tests backend startup
10. ✅ Verifies systemd service files
11. ✅ Checks Nginx configuration
12. ✅ Validates PXE files
13. ✅ Verifies storage scripts

**Usage:**
```bash
# Automatically runs on push/PR
# Or manually trigger from GitHub Actions tab
```

**Manual Trigger:**
1. Go to GitHub Actions tab
2. Select "Debian Installation Test"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

---

### 3. `debian-production-deploy.yml` - Production Deployment

**Triggers:**
- Push to `main` branch only
- Manual trigger with environment selection

**Purpose:**
Deploys ggNet to a production Debian server via SSH.

**What it does:**
1. 🔐 Sets up SSH connection to server
2. 💾 Backs up existing installation
3. 🛑 Stops running services
4. 📦 Copies files to server (rsync)
5. 🔧 Runs installation script
6. ✅ Verifies installation
7. 🚀 Starts services
8. 🏥 Runs health checks
9. 📊 Shows deployment summary

**Requirements:**
You need to configure these GitHub Secrets:

```
SSH_PRIVATE_KEY          # SSH private key for server access
DEBIAN_SERVER_HOST       # Server hostname or IP
DEBIAN_SERVER_USER       # SSH username
```

**Setup Instructions:**

1. **Generate SSH Key Pair:**
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@ggnet"
   # Save as: ~/.ssh/github_actions_rsa
   ```

2. **Copy Public Key to Server:**
   ```bash
   ssh-copy-id -i ~/.ssh/github_actions_rsa.pub user@your-server.com
   ```

3. **Add Secrets to GitHub:**
   - Go to: Settings → Secrets and variables → Actions
   - Add each secret:
     - `SSH_PRIVATE_KEY`: Contents of `~/.ssh/github_actions_rsa`
     - `DEBIAN_SERVER_HOST`: Your server IP or domain
     - `DEBIAN_SERVER_USER`: SSH username

4. **Test Connection:**
   ```bash
   ssh -i ~/.ssh/github_actions_rsa user@your-server.com
   ```

**Usage:**

**Automatic Deployment:**
```bash
# Push to main branch
git checkout main
git merge ggnet-refactor
git push origin main
# Deployment starts automatically
```

**Manual Deployment:**
1. Go to GitHub Actions tab
2. Select "Debian Production Deployment"
3. Click "Run workflow"
4. Select environment (production/staging)
5. Click "Run workflow"

**Environment Selection:**
- **Production**: Deploys to production server
- **Staging**: Deploys to staging server (if configured)

---

## Workflow Status Badges

Add these to your README.md:

```markdown
![CI](https://github.com/itcaffenet-Ljubinje/GGnet1/workflows/ggNet%20CI/badge.svg)
![Installation Test](https://github.com/itcaffenet-Ljubinje/GGnet1/workflows/Debian%20Installation%20Test/badge.svg)
![Production Deploy](https://github.com/itcaffenet-Ljubinje/GGnet1/workflows/Debian%20Production%20Deployment/badge.svg)
```

---

## Troubleshooting

### Installation Test Fails

**Problem:** Installation script fails during CI

**Solutions:**
1. Check logs in GitHub Actions output
2. Verify script syntax: `bash -n scripts/install.sh`
3. Test locally in Docker:
   ```bash
   docker run -it debian:12 bash
   # Inside container:
   apt-get update && apt-get install -y git
   git clone https://github.com/itcaffenet-Ljubinje/GGnet1.git
   cd GGnet1
   bash scripts/install.sh
   ```

### Deployment Fails

**Problem:** SSH connection fails

**Solutions:**
1. Verify SSH key is correct in GitHub Secrets
2. Check server firewall allows SSH (port 22)
3. Test SSH manually:
   ```bash
   ssh -i ~/.ssh/github_actions_rsa user@server
   ```

**Problem:** Services don't start

**Solutions:**
1. Check systemd logs:
   ```bash
   ssh user@server
   sudo journalctl -u ggnet-backend -n 50
   ```
2. Verify Nginx config:
   ```bash
   sudo nginx -t
   ```
3. Check port availability:
   ```bash
   sudo netstat -tulpn | grep :8080
   ```

---

## Advanced Configuration

### Custom Deployment Environments

To add more environments, edit `debian-production-deploy.yml`:

```yaml
environment: ${{ github.event.inputs.environment || 'production' }}
```

And add environment-specific secrets:
- `PRODUCTION_SSH_PRIVATE_KEY`
- `STAGING_SSH_PRIVATE_KEY`
- `DEVELOPMENT_SSH_PRIVATE_KEY`

### Scheduled Deployments

Add to workflow:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
```

### Slack Notifications

Add to workflow:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Best Practices

1. ✅ **Test Before Deploy**: Always run installation test before production deploy
2. ✅ **Use Branches**: Deploy from `main` only, test on feature branches
3. ✅ **Monitor Logs**: Check deployment logs after each deployment
4. ✅ **Backup First**: Deployment workflow automatically backs up existing installation
5. ✅ **Rollback Plan**: Keep backups and know how to restore them
6. ✅ **Security**: Never commit secrets, always use GitHub Secrets
7. ✅ **Documentation**: Update this README when adding new workflows

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing workflow logs
- Review server logs: `sudo journalctl -u ggnet-backend`

---

**Last Updated:** 2025-10-15
**Workflow Version:** 1.0.0

