# 🚀 **ggNet Quick Start Guide**

**Version:** 1.0.0  
**Last Updated:** October 20, 2025

---

## ✅ **Problem Solved!**

Greška "Failed to fetch status: Internal Server Error" je bila zbog:
1. Core services (DHCP, TFTP, NFS, PXE) se pokušavaju da pokrenu na Windows-u
2. Ti servisi zahtevaju Linux

**Rešenje:** Core services se sada automatski preskaču na Windows-u i vraćaju status "not_initialized" umesto da bace error.

---

## 🏃 **Quick Start - Development Mode**

### **1. Start Backend**

```bash
cd backend
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe src/main.py
```

**Backend će se pokrenuti na:** `http://localhost:5000`

**Output:**
```
[STARTUP] Starting ggNet Backend...
[OK] Database ready
[OK] Monitoring initialized
[OK] Core services skipped (running on Windows)
[OK] Server running at http://0.0.0.0:5000
[OK] API docs at http://0.0.0.0:5000/docs
```

### **2. Start Frontend**

```bash
cd frontend
npm run dev
```

**Frontend će se pokrenuti na:** `http://localhost:5173`

**Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### **3. Access Application**

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000
- **API Docs:** http://localhost:5000/docs

---

## 🔧 **Configuration**

### **Backend Configuration**

Backend koristi default konfiguraciju:
- **Port:** 5000
- **Database:** SQLite (`./ggnet.db`)
- **CORS:** `http://localhost:5173`, `http://localhost:3000`

### **Frontend Configuration**

Frontend koristi Vite proxy:
- **Port:** 5173
- **API Proxy:** `/api` → `http://localhost:5000`

---

## 🐛 **Troubleshooting**

### **Problem: "Failed to fetch" Error**

**Rešenje:**
1. Proverite da li backend radi: `curl http://localhost:5000/health`
2. Proverite da li frontend radi: `curl http://localhost:5173`
3. Proverite da li proxy radi: `curl http://localhost:5173/api/v1/health`

### **Problem: Backend ne pokreće**

**Rešenje:**
```bash
cd backend
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe src/main.py
```

### **Problem: Frontend ne pokreće**

**Rešenje:**
```bash
cd frontend
npm install
npm run dev
```

### **Problem: CORS Error**

**Rešenje:**
Backend već ima CORS konfigurisan. Proverite da li frontend koristi pravi port (5173).

---

## 📊 **Testing**

### **Test Backend API**

```bash
# Health check
curl http://localhost:5000/health

# Network services status
curl http://localhost:5000/api/v1/network/services/status

# Machines list
curl http://localhost:5000/api/v1/machines

# Images list
curl http://localhost:5000/api/v1/images
```

### **Test Frontend Proxy**

```bash
# Through proxy
curl http://localhost:5173/api/v1/health
curl http://localhost:5173/api/v1/machines
```

### **Run Tests**

```bash
cd backend
$env:PYTHONPATH = "src"
.\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 🎯 **Features**

### **Working Features (Development Mode)**

- ✅ **Backend API** - Sve endpoint-i rade
- ✅ **Frontend UI** - Sve stranice rade
- ✅ **Database** - SQLite database
- ✅ **Monitoring** - Logging i metrics
- ✅ **Authentication** - Login/logout
- ✅ **Machine Management** - CRUD operations
- ✅ **Image Management** - CRUD operations
- ✅ **Writeback Management** - CRUD operations
- ✅ **Snapshot Management** - CRUD operations
- ✅ **Network Configuration** - Configuration management

### **Not Working (Windows)**

- ❌ **DHCP Server** - Requires Linux (dnsmasq)
- ❌ **TFTP Server** - Requires Linux (tftpd-hpa)
- ❌ **NFS Server** - Requires Linux (nfs-kernel-server)
- ❌ **PXE Boot** - Requires Linux services

**Note:** Core services će raditi na Linux production server-u.

---

## 📝 **Next Steps**

1. **Development:**
   - Backend i frontend rade u development mode
   - Sve osnovne funkcionalnosti rade
   - Core services se preskaču na Windows-u

2. **Production Deployment:**
   - Koristite `scripts/install-production.sh` na Linux server-u
   - Core services će se automatski pokrenuti
   - Sve funkcionalnosti će raditi

3. **Testing:**
   - Run tests: `pytest tests/ -v`
   - Test API: `curl http://localhost:5000/api/v1/...`
   - Test frontend: `http://localhost:5173`

---

## 🔗 **Useful Links**

- **Backend API Docs:** http://localhost:5000/docs
- **Backend Health:** http://localhost:5000/health
- **Frontend:** http://localhost:5173
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`

---

## ✅ **Summary**

**Status:** ✅ **WORKING!**

- Backend: ✅ Running on port 5000
- Frontend: ✅ Running on port 5173
- API: ✅ All endpoints working
- Database: ✅ SQLite working
- Monitoring: ✅ Working
- Core Services: ⚠️ Skipped on Windows (will work on Linux)

**The error is fixed!** 🎉

---

**Happy coding!** 🚀

