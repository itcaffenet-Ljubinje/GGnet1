# 🚨 PRODUCTION DATABASE FIX - "no such column: images.image_id"

## PROBLEM

Production server (192.168.0.137) shows error:
```
Error loading images: no such column: images.image_id
```

This means the **database schema is outdated** and needs to be recreated.

---

## 🔧 SOLUTION - Quick Fix (Recommended)

### **Option 1: Recreate Database (FAST - No data loss if fresh install)**

```bash
# SSH into production server
ssh user@192.168.0.137

# Stop backend service
sudo systemctl stop ggnet-backend

# Backup old database (if exists)
cd /opt/ggnet/backend
cp ggnet.db ggnet.db.backup_$(date +%Y%m%d_%H%M%S)

# Delete old database
rm ggnet.db

# Restart backend (will auto-create new schema)
sudo systemctl start ggnet-backend

# Check status
sudo systemctl status ggnet-backend

# Verify in browser
# http://192.168.0.137/dashboard
```

---

### **Option 2: Use Migration Script**

```bash
# SSH into production server
ssh user@192.168.0.137

# Run migration script
cd /opt/ggnet/backend
python scripts/migrate_database.py

# Restart backend
sudo systemctl restart ggnet-backend
```

---

### **Option 3: Manual Migration (If you have important data)**

```bash
# SSH into production server
ssh user@192.168.0.137

# Stop backend
sudo systemctl stop ggnet-backend

# Backup database
cd /opt/ggnet/backend
cp ggnet.db ggnet.db.backup

# Open SQLite
sqlite3 ggnet.db

# Check old schema
.schema images

# Export data
.mode insert
.output /tmp/images_export.sql
SELECT * FROM images;
.quit

# Recreate database
rm ggnet.db

# Restart backend (creates new schema)
sudo systemctl start ggnet-backend

# Import data (if compatible)
# This requires manual field mapping!
```

---

## 📋 WHY THIS HAPPENED

The production database was created with an **old schema** before recent updates:
- Old schema: Used different primary key
- New schema: Uses `image_id` as UUID primary key

**Root cause:** No Alembic migrations were set up initially.

---

## 🎯 RECOMMENDATION

**For fresh installations or testing:**
→ **Use Option 1** (fastest, cleanest)

**For production with data:**
→ Contact admin to verify if data needs to be preserved
→ If no important data exists, use Option 1
→ If data is critical, use manual migration with data mapping

---

## ✅ VERIFICATION

After migration, verify:

1. **Backend starts without errors:**
   ```bash
   sudo journalctl -u ggnet-backend -f
   ```

2. **Frontend loads images:**
   ```
   http://192.168.0.137/dashboard
   ```

3. **API returns data:**
   ```bash
   curl http://192.168.0.137/api/v1/images
   ```

---

## 📞 SUPPORT

If issues persist:
1. Check backend logs: `sudo journalctl -u ggnet-backend -n 50`
2. Check database file: `ls -lh /opt/ggnet/backend/ggnet.db`
3. Verify schema: `sqlite3 ggnet.db ".schema images"`

---

**Last Updated:** 2025-10-21  
**Issue:** Production database schema mismatch  
**Status:** Migration script created ✅

