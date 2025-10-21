# 🧪 **TESTING GUIDE - STORAGE CONFIGURE FUNCTIONALITY**

## 🚀 **SERVERS RUNNING**

### **Backend:**
- URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Status: ✅ Running

### **Frontend:**
- URL: `http://localhost:5173`
- Status: ✅ Running

---

## 🧪 **TESTING STEPS**

### **1. Test Storage Page** ✅

**Steps:**
1. Open browser: `http://localhost:5173`
2. Navigate to **Storage** page (left sidebar)
3. Verify "No Array Detected" message appears
4. Verify **Configure** button is visible (top-right)

**Expected Result:**
- ✅ "No Array Detected" message displayed
- ✅ Configure button visible in top-right corner
- ✅ Dark mode support working

---

### **2. Test Configure Button** ✅

**Steps:**
1. Click **Configure** button
2. Verify dropdown menu appears
3. Verify "Add Stripe" option is visible

**Expected Result:**
- ✅ Dropdown menu opens
- ✅ "Add Stripe" option visible
- ✅ Clicking outside closes dropdown

---

### **3. Test Add Stripe Dialog** ✅

**Steps:**
1. Click **Configure** → **Add Stripe**
2. Verify dialog opens
3. Verify stripe number dropdown (0-10)
4. Select stripe number (e.g., 0)
5. Click **Add Stripe** button

**Expected Result:**
- ✅ Dialog opens with stripe number dropdown
- ✅ Stripe numbers 0-10 available
- ✅ "Add Stripe" and "Cancel" buttons visible
- ✅ Success message appears after clicking "Add Stripe"

**API Call:**
```bash
POST http://localhost:8000/api/v1/storage/array/stripes
Content-Type: application/json

{
  "stripe_number": 0
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Stripe 0 added successfully"
}
```

---

### **4. Test Add Drive to Stripe Dialog** ✅

**Steps:**
1. After adding stripe, click **Add Drive** button
2. Verify dialog opens
3. Verify drive dropdown with available drives
4. Select drive (e.g., sdf)
5. Click **Add Drive** button

**Expected Result:**
- ✅ Dialog opens with drive dropdown
- ✅ Available drives listed
- ✅ Warning message about drive capacity
- ✅ Success message appears after clicking "Add Drive"

**API Call:**
```bash
POST http://localhost:8000/api/v1/storage/array/stripes/0/drives
Content-Type: application/json

{
  "device": "sdf"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Drive sdf added to stripe 0 successfully"
}
```

---

## 🔍 **MANUAL API TESTING**

### **Test 1: Add Stripe**

```bash
curl -X POST http://localhost:8000/api/v1/storage/array/stripes \
  -H "Content-Type: application/json" \
  -d '{"stripe_number": 0}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Stripe 0 added successfully"
}
```

---

### **Test 2: Add Drive to Stripe**

```bash
curl -X POST http://localhost:8000/api/v1/storage/array/stripes/0/drives \
  -H "Content-Type: application/json" \
  -d '{"device": "sdf"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Drive sdf added to stripe 0 successfully"
}
```

---

### **Test 3: Get Array Status**

```bash
curl http://localhost:8000/api/v1/storage/array/status
```

**Expected Response:**
```json
{
  "exists": false,
  "health": "offline",
  "type": "N/A",
  "devices": [],
  "capacity": {
    "total_gb": 0,
    "used_gb": 0,
    "available_gb": 0,
    "reserved_gb": 0,
    "reserved_percent": 0
  },
  "breakdown": {
    "system_images_gb": 0,
    "game_images_gb": 0,
    "writebacks_gb": 0,
    "snapshots_gb": 0
  }
}
```

---

## 🐛 **TROUBLESHOOTING**

### **Issue 1: Configure Button Not Visible**

**Problem:** Configure button doesn't appear on Storage page

**Solution:**
1. Check browser console for errors
2. Verify frontend build is up to date
3. Clear browser cache and reload
4. Check if `arrayStatus.exists === false` in React DevTools

---

### **Issue 2: API Endpoints Not Working**

**Problem:** Frontend can't connect to backend

**Solution:**
1. Verify backend is running on port 8000
2. Check CORS settings in backend
3. Check network tab in browser DevTools
4. Verify API endpoint URLs in frontend code

---

### **Issue 3: Dropdown Not Opening**

**Problem:** Configure dropdown doesn't open

**Solution:**
1. Check browser console for JavaScript errors
2. Verify state management in React DevTools
3. Check if `showConfigureMenu` state is updating
4. Verify click event handlers are bound correctly

---

### **Issue 4: Dialog Not Opening**

**Problem:** Add Stripe dialog doesn't open

**Solution:**
1. Check browser console for errors
2. Verify `showAddStripeDialog` state is updating
3. Check if dialog component is rendered
4. Verify z-index and positioning

---

## 📊 **TEST RESULTS**

### **Frontend Tests:**

| Test | Status | Notes |
|------|--------|-------|
| Storage Page Loads | ⏳ Pending | Test in browser |
| Configure Button Visible | ⏳ Pending | Test in browser |
| Dropdown Opens | ⏳ Pending | Test in browser |
| Add Stripe Dialog Opens | ⏳ Pending | Test in browser |
| Add Drive Dialog Opens | ⏳ Pending | Test in browser |

### **Backend Tests:**

| Test | Status | Notes |
|------|--------|-------|
| POST /array/stripes | ⏳ Pending | Test with curl |
| POST /array/stripes/{stripe}/drives | ⏳ Pending | Test with curl |
| GET /array/status | ⏳ Pending | Test with curl |

---

## ✅ **SUCCESS CRITERIA**

### **Frontend:**
- ✅ Configure button visible on Storage page
- ✅ Dropdown menu opens and closes correctly
- ✅ Add Stripe dialog opens with stripe number dropdown
- ✅ Add Drive dialog opens with drive dropdown
- ✅ Success messages appear after operations
- ✅ Dark mode support working

### **Backend:**
- ✅ POST /array/stripes returns success
- ✅ POST /array/stripes/{stripe}/drives returns success
- ✅ GET /array/status returns correct data
- ✅ Error handling works correctly
- ✅ Logging works correctly

---

## 🎯 **NEXT STEPS AFTER TESTING**

1. **If Tests Pass:**
   - Implement actual ZFS/MD RAID stripe creation logic
   - Implement actual drive-to-stripe addition logic
   - Add validation for drive capacity
   - Add error handling for edge cases

2. **If Tests Fail:**
   - Debug frontend issues
   - Debug backend issues
   - Fix API endpoint problems
   - Fix UI/UX issues

---

## 📝 **TESTING CHECKLIST**

### **Frontend:**
- [ ] Open Storage page
- [ ] Verify Configure button visible
- [ ] Click Configure button
- [ ] Verify dropdown opens
- [ ] Click Add Stripe
- [ ] Verify dialog opens
- [ ] Select stripe number
- [ ] Click Add Stripe
- [ ] Verify success message
- [ ] Test dark mode

### **Backend:**
- [ ] Test POST /array/stripes with curl
- [ ] Test POST /array/stripes/{stripe}/drives with curl
- [ ] Test GET /array/status with curl
- [ ] Verify error handling
- [ ] Verify logging

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0  
**Status:** 🧪 Ready for Testing

