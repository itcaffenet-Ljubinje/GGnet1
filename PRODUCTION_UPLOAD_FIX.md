# 🚨 PRODUCTION UPLOAD FIX - "NetworkError when attempting to fetch resource"

## PROBLEM

Frontend shows error when uploading images:
```
Failed to upload image: NetworkError when attempting to fetch resource.
```

---

## 🔧 ROOT CAUSES & SOLUTIONS

### **1. Nginx File Size Limit (MOST COMMON)**

**Problem:** Nginx default `client_max_body_size` is **1MB**  
**Fix:** Increase limit for image uploads (Windows images can be 20GB+)

```bash
# SSH into production server
ssh user@192.168.0.137

# Edit Nginx config
sudo nano /etc/nginx/sites-available/ggnet

# Add this INSIDE the server {} block:
client_max_body_size 50G;  # Allow up to 50GB uploads

# Test config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

**Example Nginx config:**
```nginx
server {
    listen 80;
    server_name 192.168.0.137;
    
    # IMPORTANT: Increase upload limit
    client_max_body_size 50G;
    
    # Frontend
    location / {
        root /opt/ggnet/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # IMPORTANT: Increase timeouts for large uploads
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_connect_timeout 300s;
    }
}
```

---

### **2. Backend Not Running**

**Check if backend is running:**
```bash
sudo systemctl status ggnet-backend

# If not running:
sudo systemctl start ggnet-backend

# Check logs:
sudo journalctl -u ggnet-backend -f
```

---

### **3. CORS Configuration**

**Check backend CORS settings:**

```bash
# Check main.py CORS config
cat /opt/ggnet/backend/src/main.py | grep -A 10 "CORS"
```

Should have:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### **4. Storage Directory Permissions**

**Ensure upload directory exists and is writable:**

```bash
# Create directory
sudo mkdir -p /var/lib/ggnet/images/{windows,linux,other}

# Set ownership
sudo chown -R ggnet:ggnet /var/lib/ggnet

# Set permissions
sudo chmod -R 755 /var/lib/ggnet/images
```

---

### **5. FastAPI File Size Limit**

**Check if FastAPI has limits:**

Currently no limits set in code. If needed, add to `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# No file size limits by default
# Nginx handles this
```

---

## 🔍 DEBUGGING

### **Test Backend Directly:**

```bash
# Test upload endpoint from server
curl -X POST http://127.0.0.1:8000/api/v1/images/upload \
  -F "file=@test.iso" \
  -F "name=test-image" \
  -F "type=linux" \
  -F "description=Test upload"
```

### **Check Browser Console:**

Open Developer Tools (F12) and look for:
- CORS errors
- 413 Payload Too Large
- 504 Gateway Timeout
- Network tab - see actual error

### **Check Backend Logs:**

```bash
sudo journalctl -u ggnet-backend -n 100 --no-pager | grep -i error
```

---

## ✅ VERIFICATION

After applying fixes:

1. **Reload Nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

2. **Restart Backend:**
   ```bash
   sudo systemctl restart ggnet-backend
   ```

3. **Test small file first:**
   - Upload a small ISO (~100MB) to verify endpoint works
   - Then try larger images

4. **Monitor logs:**
   ```bash
   sudo journalctl -u ggnet-backend -f
   ```

---

## 📊 EXPECTED BEHAVIOR

**Small file (<1MB):** Should work without Nginx changes  
**Large file (>1MB):** Requires `client_max_body_size` increase  
**Very large (>10GB):** Requires timeout adjustments too

---

## 🎯 QUICK FIX COMMAND

**All-in-one fix for most cases:**

```bash
# On production server (192.168.0.137)
sudo tee -a /etc/nginx/sites-available/ggnet > /dev/null <<'EOF'

# Inside server {} block, add:
client_max_body_size 50G;
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
EOF

sudo nginx -t && sudo systemctl reload nginx
sudo systemctl restart ggnet-backend
```

---

**Last Updated:** 2025-10-21  
**Issue:** NetworkError on image upload  
**Root Cause:** Nginx file size limit (1MB default)  
**Status:** Fix documented ✅

