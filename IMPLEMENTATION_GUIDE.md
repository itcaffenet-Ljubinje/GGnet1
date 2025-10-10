# GGRock Integration Implementation Guide

This guide provides step-by-step instructions for implementing and deploying the GGRock Management System.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Development Setup](#development-setup)
3. [GGRock Backend Integration](#ggrock-backend-integration)
4. [Production Deployment](#production-deployment)
5. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Node.js 18+ installed
- GGRock backend server running (v0.1.2200.2324-1)
- pnpm, npm, or yarn package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd GGnet1

# Install dependencies
pnpm install

# Copy environment configuration
cp .env.example .env

# Start development server
pnpm dev
```

The application will be available at `http://localhost:3000`

## Development Setup

### 1. Install Dependencies

```bash
# Using pnpm (recommended)
pnpm install

# Using npm
npm install

# Using yarn
yarn install
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# GGRock Backend Configuration
VITE_GGROCK_API_URL=http://localhost:5000
VITE_GGROCK_WS_URL=ws://localhost:5000
VITE_GGROCK_VNC_URL=http://localhost:6080

# Feature Flags
VITE_ENABLE_VNC=true
VITE_ENABLE_GRAFANA=true
VITE_GRAFANA_URL=http://localhost:3000
```

### 3. Start Development Server

```bash
pnpm dev
```

The Vite dev server will start with hot module replacement (HMR) enabled.

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Proxy**: http://localhost:3000/api/ggrock/*
- **WebSocket**: ws://localhost:3000/ws/*

## GGRock Backend Integration

### Backend Requirements

The GGRock backend (v0.1.2200.2324-1) should be running with the following services:

- **API Server**: Port 5000
- **PostgreSQL**: Port 5432
- **noVNC Server**: Port 6080
- **Prometheus**: Port 9090
- **Grafana**: Port 3000

### API Endpoints

The frontend expects these GGRock API endpoints:

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Token refresh

#### Computers
- `GET /computers` - List all computers
- `GET /computers/:id` - Get computer details
- `POST /computers/:id/action` - Execute action (reboot, shutdown, wakeup)

#### Sessions
- `GET /sessions` - List all sessions
- `GET /sessions/active` - List active sessions
- `GET /sessions/:id` - Get session details
- `POST /sessions/:id/end` - End session

#### Boot Images
- `GET /boot/images` - List boot images
- `GET /boot/images/:id` - Get boot image details
- `POST /boot/deploy` - Deploy boot image

#### System
- `GET /metrics/system` - System metrics
- `GET /health` - Health check

### WebSocket Endpoints

Real-time updates via WebSocket:

- `/ws/computers/status` - Computer status updates
- `/ws/sessions/updates` - Session updates
- `/ws/metrics/system` - System metrics updates

### Authentication Flow

1. User enters credentials on login page
2. Frontend sends `POST /auth/login` with credentials
3. Backend returns JWT token and user info
4. Token stored in localStorage
5. All subsequent requests include `Authorization: Bearer <token>` header
6. On 401 response, automatic token refresh attempted
7. If refresh fails, user redirected to login

## Production Deployment

### Option 1: Docker Deployment (Recommended)

#### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down
```

The stack includes:
- Frontend (React app): Port 3000
- PostgreSQL: Port 5432
- Prometheus: Port 9090
- Grafana: Port 3001

#### Custom Docker Build

```bash
# Build image
docker build -t ggrock-management:1.0.0 .

# Run container
docker run -d \
  -p 3000:80 \
  -e VITE_GGROCK_API_URL=http://your-ggrock-server:5000 \
  -e VITE_GGROCK_WS_URL=ws://your-ggrock-server:5000 \
  --name ggrock-frontend \
  --restart unless-stopped \
  ggrock-management:1.0.0
```

### Option 2: Traditional Deployment

#### Build for Production

```bash
# Build optimized production bundle
pnpm build

# The build output will be in the 'dist' directory
```

#### Deploy to Nginx

```bash
# Copy build files to nginx web root
sudo cp -r dist/* /var/www/html/

# Configure nginx
sudo nano /etc/nginx/sites-available/ggrock
```

Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ggrock/ {
        proxy_pass http://localhost:5000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://localhost:5000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/ggrock /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Deploy to CDN/Static Host

The built files can be deployed to any static hosting service:

- **Vercel**: `vercel deploy`
- **Netlify**: `netlify deploy --prod`
- **AWS S3 + CloudFront**
- **GitHub Pages**

**Important**: Configure rewrites for SPA routing and API proxy.

## Environment-Specific Configurations

### Development

```env
VITE_GGROCK_API_URL=http://localhost:5000
VITE_GGROCK_WS_URL=ws://localhost:5000
```

### Staging

```env
VITE_GGROCK_API_URL=https://staging-api.yourdomain.com
VITE_GGROCK_WS_URL=wss://staging-api.yourdomain.com
```

### Production

```env
VITE_GGROCK_API_URL=https://api.yourdomain.com
VITE_GGROCK_WS_URL=wss://api.yourdomain.com
VITE_GGROCK_VNC_URL=https://vnc.yourdomain.com
```

## Security Considerations

### Production Checklist

- [ ] Change default admin credentials
- [ ] Enable HTTPS/TLS for all connections
- [ ] Configure CORS properly on backend
- [ ] Set secure session timeout
- [ ] Enable rate limiting on API
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Use environment-specific secrets
- [ ] Implement IP whitelisting (if applicable)

### SSL/TLS Configuration

For production, always use HTTPS:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Maintenance

### Health Checks

The application provides health check endpoints:

- Frontend: `GET /health`
- Backend: `GET /api/ggrock/health`

### Monitoring

#### Prometheus Metrics

Access Prometheus UI at `http://localhost:9090`

Key metrics:
- API response times
- Computer online/offline status
- Active session counts
- System resource usage

#### Grafana Dashboards

Access Grafana at `http://localhost:3001` (default: admin/admin)

Pre-configured dashboards:
- System Overview
- Computer Monitoring
- Session Analytics

### Logs

View application logs:

```bash
# Docker deployment
docker-compose logs -f frontend

# Traditional deployment
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup and Recovery

#### Database Backup

```bash
# Backup PostgreSQL database
docker exec ggrock-postgres pg_dump -U ggrock ggrock > backup.sql

# Restore database
docker exec -i ggrock-postgres psql -U ggrock ggrock < backup.sql
```

#### Configuration Backup

Important files to backup:
- `.env` - Environment configuration
- `docker-compose.yml` - Docker configuration
- `nginx.conf` - Nginx configuration

## Troubleshooting

### Common Issues

#### 1. Cannot connect to backend API

**Symptoms**: "Network error occurred" messages

**Solutions**:
- Verify GGRock backend is running: `curl http://localhost:5000/health`
- Check `VITE_GGROCK_API_URL` in `.env`
- Verify network connectivity
- Check firewall rules

#### 2. WebSocket connection fails

**Symptoms**: "Live updates" indicator not showing, no real-time updates

**Solutions**:
- Verify WebSocket endpoint: `wscat -c ws://localhost:5000/ws/computers/status`
- Check `VITE_GGROCK_WS_URL` configuration
- Ensure nginx WebSocket proxy is configured correctly
- Check browser console for WebSocket errors

#### 3. Authentication errors

**Symptoms**: Redirected to login repeatedly, 401 errors

**Solutions**:
- Clear localStorage: `localStorage.clear()`
- Verify backend authentication endpoint
- Check token expiration settings
- Verify CORS configuration on backend

#### 4. Build errors

**Symptoms**: `pnpm build` fails

**Solutions**:
```bash
# Clean install
rm -rf node_modules
rm -rf dist
pnpm install

# Clear cache
pnpm store prune

# Rebuild
pnpm build
```

#### 5. Docker container won't start

**Symptoms**: Container exits immediately

**Solutions**:
```bash
# Check logs
docker logs ggrock-frontend

# Rebuild without cache
docker-compose build --no-cache

# Check environment variables
docker exec ggrock-frontend env
```

### Debug Mode

Enable debug logging:

```typescript
// In src/services/ggrock-api.ts
// Add console.log statements in request/response interceptors

this.client.interceptors.request.use((config) => {
  console.log('API Request:', config.method, config.url);
  return config;
});

this.client.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  }
);
```

### Getting Help

- Check the [README.md](README.md) for general documentation
- Review GGRock backend logs for API errors
- Check browser console for frontend errors
- Verify network tab in browser DevTools
- Contact GGRock support: info@ggcircuit.com

## Performance Optimization

### Production Build Optimization

The production build is automatically optimized with:
- Code splitting
- Tree shaking
- Minification
- Gzip compression
- Asset caching

### Further Optimizations

1. **Enable CDN** for static assets
2. **Configure caching** headers appropriately
3. **Implement service worker** for offline support
4. **Use image optimization** for logos and icons
5. **Enable HTTP/2** on web server

## Updating

### Update Dependencies

```bash
# Check for updates
pnpm outdated

# Update all dependencies
pnpm update

# Update specific package
pnpm update react
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Install new dependencies
pnpm install

# Rebuild
pnpm build

# Restart services
docker-compose restart frontend
```

## Next Steps

After successful deployment:

1. Configure user accounts and permissions
2. Set up monitoring alerts
3. Configure automated backups
4. Test disaster recovery procedures
5. Train operators on the system
6. Document custom configurations
7. Set up CI/CD pipeline (optional)

---

For additional help, refer to the main [README.md](README.md) or contact support.

