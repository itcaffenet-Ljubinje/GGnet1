# 🔍 **Testiranje - Problemi i Rešenja**

**Datum:** 20. oktobar 2025  
**Status:** ⚠️ Testovi ne prolaze - potrebno rešenje

---

## 📊 **Trenutno Stanje Testova**

```
Total Tests: 14
✅ PASSED:  0 (0%)
❌ FAILED:  14 (100%)
```

---

## 🔴 **GLAVNI PROBLEM: Database Initialization**

### **Greška:**
```
RuntimeError: Database not initialized. Call init_db() first.
```

### **Uzrok:**
- `async_session_maker` je `None` kada se poziva `get_db()` dependency
- `init_db()` se poziva u `test_db` fixture, ali `TestClient` ne čeka da se završi
- Async context manager ne radi kako treba sa pytest-asyncio

---

## 🛠️ **REŠENJA**

### **Rešenje 1: Koristiti TestClient umesto AsyncClient** ✅ PREPORUČENO

**Prednosti:**
- Jednostavnije
- Nema problema sa async context manager-ima
- Brže

**Implementacija:**

```python
# backend/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from main import app
from db.base import init_db

# Initialize database before tests
@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Initialize test database once before all tests"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run init_db synchronously
    loop.run_until_complete(init_db())
    
    yield
    
    # Cleanup
    loop.close()


@pytest.fixture
def client():
    """Test client for FastAPI"""
    return TestClient(app)


def test_create_machine(client):
    """Test creating a machine"""
    machine_data = {
        "name": "Test Machine",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.99"
    }
    
    response = client.post("/api/v1/machines", json=machine_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["name"] == machine_data["name"]
    assert data["mac_address"] == machine_data["mac_address"].upper()
    assert "id" in data
```

---

### **Rešenje 2: Koristiti AsyncClient sa pravilnim fixture-ima**

**Implementacija:**

```python
# backend/tests/test_api.py

import pytest
from httpx import AsyncClient
from main import app
from db.base import init_db

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def init_test_db():
    """Initialize test database"""
    await init_db()
    yield
    # Cleanup


@pytest.fixture
async def client():
    """Async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_machine(client):
    """Test creating a machine"""
    machine_data = {
        "name": "Test Machine",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.99"
    }
    
    response = await client.post("/api/v1/machines", json=machine_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["name"] == machine_data["name"]
    assert data["mac_address"] == machine_data["mac_address"].upper()
    assert "id" in data
```

---

## 📋 **PLAN AKCIJE**

### **Korak 1: Implementirati Rešenje 1** (15 min)
- [ ] Kreirati novi `test_api.py` sa `TestClient`
- [ ] Dodati `init_test_db` fixture
- [ ] Pokrenuti testove

### **Korak 2: Registrovati Ostale Routers** (15 min)
- [ ] Dodati `images` router u `main.py`
- [ ] Dodati `writebacks` router u `main.py`
- [ ] Dodati `snapshots` router u `main.py`
- [ ] Dodati `network` router u `main.py`
- [ ] Dodati `system` router u `main.py`

### **Korak 3: Re-test** (10 min)
- [ ] Pokrenuti sve testove
- [ ] Proveriti da li sve prolazi
- [ ] Dokumentovati rezultate

---

## 🎯 **EXPECTED RESULTS**

Nakon implementacije, očekujemo:

```
Total Tests: 14
✅ PASSED:  14 (100%)
❌ FAILED:  0 (0%)
```

---

## 📝 **NAPOMENA**

**TestClient vs AsyncClient:**
- `TestClient` je **preporučen** za većinu testova
- `AsyncClient` je potreban samo za testiranje WebSocket-a ili async middleware-a
- `TestClient` je **brži** i **jednostavniji**

---

## 🚀 **SLEDEĆI KORACI**

1. **Implementirati Rešenje 1** (15 min)
2. **Registrovati routers** (15 min)
3. **Re-test** (10 min)
4. **Implementirati core features** (DHCP, TFTP, NFS) (2+ sata)

**Ukupno vreme:** ~40 minuta za testiranje + 2+ sata za core features

---

**Status:** 🟡 **U RAZVOJU - ČEKA IMPLEMENTACIJU**

