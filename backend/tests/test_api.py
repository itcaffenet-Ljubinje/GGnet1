"""
API Tests for ggNet Backend

Tests for FastAPI endpoints using TestClient.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import asyncio
from fastapi.testclient import TestClient

from main import app
from db.base import init_db


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Initialize test database once before all tests"""
    # Create event loop
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


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up database after each test"""
    yield
    # Clean up database after each test
    from db.base import async_session_maker
    from db.models import Machine
    from sqlalchemy import text
    
    async def cleanup():
        async with async_session_maker() as session:
            # Delete all machines
            await session.execute(text("DELETE FROM machines"))
            await session.commit()
    
    # Run cleanup synchronously
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(cleanup())


@pytest.fixture
def client():
    """Test client for FastAPI"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "ggNet" in data["message"]


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200


def test_api_status(client):
    """Test API status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    
    # Verify required fields
    assert "app_name" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "db_status" in data
    assert "system" in data
    
    # Verify system metrics
    assert "cpu_percent" in data["system"]
    assert "memory_percent" in data["system"]
    assert "disk_percent" in data["system"]
    
    # Verify values are reasonable
    assert 0 <= data["system"]["cpu_percent"] <= 100
    assert 0 <= data["system"]["memory_percent"] <= 100
    assert 0 <= data["system"]["disk_percent"] <= 100


def test_list_machines(client):
    """Test listing machines"""
    response = client.get("/api/v1/machines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


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
    
    # Verify response
    assert data["name"] == machine_data["name"]
    assert data["mac_address"] == machine_data["mac_address"].upper()
    assert data["ip_address"] == machine_data["ip_address"]
    assert "id" in data
    assert data["status"] == "offline"


def test_create_machine_duplicate_mac(client):
    """Test creating machine with duplicate MAC fails"""
    machine_data = {
        "name": "Test Machine 1",
        "mac_address": "FF:EE:DD:CC:BB:AA"
    }
    
    # Create first machine
    response1 = client.post("/api/v1/machines", json=machine_data)
    assert response1.status_code == 201
    
    # Try to create duplicate
    machine_data["name"] = "Test Machine 2"
    response2 = client.post("/api/v1/machines", json=machine_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


def test_create_machine_invalid_mac(client):
    """Test creating machine with invalid MAC fails"""
    machine_data = {
        "name": "Test Machine",
        "mac_address": "INVALID_MAC"
    }
    
    response = client.post("/api/v1/machines", json=machine_data)
    assert response.status_code == 422  # Pydantic validation error


def test_get_machine(client):
    """Test getting specific machine"""
    # First create a machine
    machine_data = {
        "name": "Get Test Machine",
        "mac_address": "11:22:33:44:55:66"
    }
    
    create_response = client.post("/api/v1/machines", json=machine_data)
    assert create_response.status_code == 201
    machine_id = create_response.json()["id"]
    
    # Get the machine
    response = client.get(f"/api/v1/machines/{machine_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == machine_id
    assert data["name"] == machine_data["name"]


def test_get_nonexistent_machine(client):
    """Test getting nonexistent machine returns 404"""
    response = client.get("/api/v1/machines/99999")
    assert response.status_code == 404


def test_delete_machine(client):
    """Test deleting a machine"""
    # Create machine
    machine_data = {
        "name": "Delete Test Machine",
        "mac_address": "99:88:77:66:55:44"
    }
    
    create_response = client.post("/api/v1/machines", json=machine_data)
    machine_id = create_response.json()["id"]
    
    # Delete machine
    response = client.delete(f"/api/v1/machines/{machine_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/machines/{machine_id}")
    assert get_response.status_code == 404


def test_power_operation(client):
    """Test power operations on machine"""
    # Create machine
    machine_data = {
        "name": "Power Test Machine",
        "mac_address": "AA:11:22:33:44:BB"
    }
    
    create_response = client.post("/api/v1/machines", json=machine_data)
    machine_id = create_response.json()["id"]
    
    # Test start
    response = client.post(f"/api/v1/machines/{machine_id}/power?action=start")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "start"


def test_keep_writeback(client):
    """Test keep writeback toggle"""
    # Create machine
    machine_data = {
        "name": "Writeback Test Machine",
        "mac_address": "CC:DD:EE:FF:00:11"
    }
    
    create_response = client.post("/api/v1/machines", json=machine_data)
    machine_id = create_response.json()["id"]
    
    # Enable keep writeback
    response = client.post(
        f"/api/v1/machines/{machine_id}/keep_writeback?keep=true"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["keep_writeback"] is True


def test_system_metrics(client):
    """Test system metrics endpoint"""
    response = client.get("/api/v1/system/metrics")
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure (response is flattened in system.py)
    assert "total_machines" in data
    assert "online_machines" in data
    assert "offline_machines" in data
    assert "active_sessions" in data
    assert "cpu_usage_avg" in data
    assert "ram_usage_avg" in data
    assert "disk_usage_percent" in data
    assert "cache_hit_rate" in data
    
    # Verify values are reasonable
    assert 0 <= data["cpu_usage_avg"] <= 100
    assert 0 <= data["ram_usage_avg"] <= 100
    assert 0 <= data["disk_usage_percent"] <= 100
    assert 0 <= data["cache_hit_rate"] <= 100


def test_system_logs(client):
    """Test system logs endpoint"""
    response = client.get("/api/v1/system/logs")
    assert response.status_code == 200
    data = response.json()
    
    assert "logs" in data
    assert isinstance(data["logs"], list)
