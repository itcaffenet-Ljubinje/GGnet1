"""
Integration Tests for Storage API Endpoints

Tests FastAPI storage endpoints with mocked storage manager.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from core.storage_manager import ArrayType, DriveStatus, DriveInfo, ArrayCapacity, ArrayBreakdown, ArrayStatus


@pytest.fixture
def mock_db():
    """Create mock database session"""
    db = MagicMock()
    return db


@pytest.fixture
def storage_client(mock_db):
    """Create test client with mocked dependencies for storage API tests"""
    from main import app
    from db.base import get_db
    
    # Override database dependency
    async def override_get_db():
        yield mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    test_client = TestClient(app)
    
    yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_storage_manager():
    """Create mock storage manager"""
    manager = Mock()
    
    # Mock array status
    manager.get_array_status.return_value = ArrayStatus(
        exists=True,
        health="online",
        type="ZFS",
        devices=[
            DriveInfo(
                device="sda",
                serial="TEST123",
                model="Samsung SSD",
                capacity_gb=1800,
                status=DriveStatus.ONLINE,
                position=0,
                health="healthy"
            ),
            DriveInfo(
                device="sdb",
                serial="TEST456",
                model="Samsung SSD",
                capacity_gb=1800,
                status=DriveStatus.ONLINE,
                position=1,
                health="healthy"
            )
        ],
        capacity=ArrayCapacity(
            total_gb=3600,
            used_gb=1000,
            available_gb=2600,
            reserved_gb=540,
            reserved_percent=15.0
        ),
        breakdown=ArrayBreakdown(
            system_images_gb=500,
            game_images_gb=300,
            writebacks_gb=150,
            snapshots_gb=50
        ),
        array_type=ArrayType.ZFS
    )
    
    # Mock available drives
    manager.get_available_drives.return_value = [
        {
            'device': 'sdc',
            'size': '1.8T',
            'model': 'Samsung SSD',
            'serial': 'TEST789',
            'capacity_gb': 1800
        },
        {
            'device': 'sdd',
            'size': '1.8T',
            'model': 'Samsung SSD',
            'serial': 'TEST012',
            'capacity_gb': 1800
        }
    ]
    
    # Mock drive operations
    manager.add_drive.return_value = True
    manager.remove_drive.return_value = True
    manager.replace_drive.return_value = True
    manager.bring_drive_offline.return_value = True
    manager.bring_drive_online.return_value = True
    manager.add_stripe.return_value = True
    manager.add_drive_to_stripe.return_value = True
    
    return manager


class TestStorageAPI:
    """Test Storage API endpoints"""
    
    @patch('api.v1.storage.get_storage_manager')
    def test_get_array_status(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test GET /api/v1/storage/array/status"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.get("/api/v1/storage/array/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['exists'] is True
        assert data['health'] == "online"
        assert data['type'] == "ZFS"
        assert len(data['devices']) == 2
        assert data['devices'][0]['device'] == "sda"
        assert data['capacity']['total_gb'] == 3600
        assert data['breakdown']['system_images_gb'] == 500
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_drive(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/add"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/drives/add",
            json={"device": "sdc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "added successfully" in data['message']
        mock_storage_manager.add_drive.assert_called_once_with("sdc")
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_drive_invalid_device(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/add with invalid device"""
        mock_storage_manager.add_drive.return_value = False
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/drives/add",
            json={"device": "invalid"}
        )
        
        # Storage manager returns False for invalid device, API returns 400
        assert response.status_code == 400
        detail = response.json()['detail'].lower()
        assert "failed" in detail or "invalid" in detail
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_drive_failure(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/add failure"""
        mock_storage_manager.add_drive.return_value = False
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/drives/add",
            json={"device": "sdc"}
        )
        
        assert response.status_code == 400
        assert "Failed to add drive" in response.json()['detail']
    
    @patch('api.v1.storage.get_storage_manager')
    def test_remove_drive(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/remove"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/drives/remove",
            json={"device": "sdc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "removed successfully" in data['message']
        mock_storage_manager.remove_drive.assert_called_once_with("sdc")
    
    @patch('api.v1.storage.get_storage_manager')
    def test_replace_drive(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/replace"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/drives/replace",
            json={"old_device": "sda", "new_device": "sdc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "replaced" in data['message'].lower() and "successfully" in data['message'].lower()
        mock_storage_manager.replace_drive.assert_called_once_with("sda", "sdc")
    
    @patch('api.v1.storage.get_storage_manager')
    def test_bring_drive_offline(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/{device}/offline"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post("/api/v1/storage/array/drives/sda/offline")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "brought offline successfully" in data['message']
        mock_storage_manager.bring_drive_offline.assert_called_once_with("sda")
    
    @patch('api.v1.storage.get_storage_manager')
    def test_bring_drive_online(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/drives/{device}/online"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post("/api/v1/storage/array/drives/sda/online")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "brought online successfully" in data['message']
        mock_storage_manager.bring_drive_online.assert_called_once_with("sda")
    
    @patch('api.v1.storage.get_safety_validator')
    @patch('api.v1.storage.get_storage_manager')
    def test_add_stripe(self, mock_get_manager, mock_get_validator, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/stripes"""
        mock_get_manager.return_value = mock_storage_manager
        
        # Mock safety validator to return True for all checks
        mock_validator = Mock()
        mock_validator.validate_stripe_number.return_value = (True, "OK")
        mock_validator.validate_raid_type.return_value = (True, "OK")
        mock_validator.validate_devices.return_value = (True, "OK")
        mock_get_validator.return_value = mock_validator
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes",
            json={
                "stripe_number": 0,
                "raid_type": "mirror",
                "devices": ["sdc", "sdd"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "Stripe 0 added successfully" in data['message']
        mock_storage_manager.add_stripe.assert_called_once_with(0, "mirror", ["sdc", "sdd"])
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_stripe_invalid_stripe_number(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/stripes with invalid stripe number"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes",
            json={
                "stripe_number": 15,
                "raid_type": "mirror",
                "devices": ["sdc", "sdd"]
            }
        )
        
        assert response.status_code == 400
        assert "must be between 0 and 10" in response.json()['detail']
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_stripe_invalid_raid_type(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/stripes with invalid RAID type"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes",
            json={
                "stripe_number": 0,
                "raid_type": "invalid",
                "devices": ["sdc", "sdd"]
            }
        )
        
        assert response.status_code == 400
        assert "Invalid RAID type" in response.json()['detail']
    
    @patch('api.v1.storage.get_safety_validator')
    @patch('api.v1.storage.get_storage_manager')
    def test_add_stripe_no_devices(self, mock_get_manager, mock_get_validator, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/stripes without devices"""
        mock_get_manager.return_value = mock_storage_manager
        
        # Mock safety validator to fail on empty devices
        mock_validator = Mock()
        mock_validator.validate_stripe_number.return_value = (True, "OK")
        mock_validator.validate_raid_type.return_value = (False, "mirror requires minimum 2 devices (got 0)")
        mock_validator.validate_devices.return_value = (False, "No devices provided")
        mock_get_validator.return_value = mock_validator
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes",
            json={
                "stripe_number": 0,
                "raid_type": "mirror",
                "devices": []
            }
        )
        
        assert response.status_code == 400
        detail = response.json()['detail'].lower()
        assert "device" in detail or "require" in detail
    
    @patch('api.v1.storage.get_storage_manager')
    def test_get_available_drives(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test GET /api/v1/storage/array/available-drives"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.get("/api/v1/storage/array/available-drives")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        assert data[0]['device'] == 'sdc'
        assert data[0]['capacity_gb'] == 1800
        assert data[1]['device'] == 'sdd'
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_drive_to_stripe(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/stripes/{stripe}/drives"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes/0/drives",
            json={"device": "sdc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert "Drive sdc added to stripe 0 successfully" in data['message']
        mock_storage_manager.add_drive_to_stripe.assert_called_once_with("0", "sdc")
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_drive_to_stripe_invalid_device(self, mock_get_manager, storage_client, mock_storage_manager):
        """Test POST /api/v1/storage/array/stripes/{stripe}/drives with invalid device"""
        mock_get_manager.return_value = mock_storage_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes/0/drives",
            json={"device": "invalid"}
        )
        
        assert response.status_code == 400
        detail = response.json()['detail'].lower()
        assert "must start with" in detail and "sd" in detail


class TestStorageAPIErrors:
    """Test Storage API error handling"""
    
    @patch('api.v1.storage.get_storage_manager')
    def test_get_array_status_exception(self, mock_get_manager, storage_client):
        """Test GET /api/v1/storage/array/status exception handling"""
        mock_manager = Mock()
        mock_manager.get_array_status.side_effect = Exception("Test error")
        mock_get_manager.return_value = mock_manager
        
        response = storage_client.get("/api/v1/storage/array/status")
        
        assert response.status_code == 500
        detail = response.json()['detail'].lower()
        assert "failed" in detail or "error" in detail
    
    @patch('api.v1.storage.get_storage_manager')
    def test_add_drive_exception(self, mock_get_manager, storage_client):
        """Test POST /api/v1/storage/array/drives/add exception handling"""
        mock_manager = Mock()
        mock_manager.add_drive.side_effect = Exception("Test error")
        mock_get_manager.return_value = mock_manager
        
        response = storage_client.post(
            "/api/v1/storage/array/drives/add",
            json={"device": "sdc"}
        )
        
        assert response.status_code == 500
        assert "Error adding drive" in response.json()['detail']
    
    @patch('api.v1.storage.get_safety_validator')
    @patch('api.v1.storage.get_storage_manager')
    def test_add_stripe_exception(self, mock_get_manager, mock_get_validator, storage_client):
        """Test POST /api/v1/storage/array/stripes exception handling"""
        mock_manager = Mock()
        mock_manager.add_stripe.side_effect = Exception("Test error")
        mock_get_manager.return_value = mock_manager
        
        # Mock safety validator to pass
        mock_validator = Mock()
        mock_validator.validate_stripe_number.return_value = (True, "OK")
        mock_validator.validate_raid_type.return_value = (True, "OK")
        mock_validator.validate_devices.return_value = (True, "OK")
        mock_get_validator.return_value = mock_validator
        
        response = storage_client.post(
            "/api/v1/storage/array/stripes",
            json={
                "stripe_number": 0,
                "raid_type": "mirror",
                "devices": ["sdc", "sdd"]
            }
        )
        
        assert response.status_code == 500
        assert "Error adding stripe" in response.json()['detail']


class TestStorageAPIValidation:
    """Test Storage API input validation"""
    
    def test_add_drive_missing_device(self, storage_client):
        """Test POST /api/v1/storage/array/drives/add with missing device"""
        response = storage_client.post(
            "/api/v1/storage/array/drives/add",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_replace_drive_missing_fields(self, storage_client):
        """Test POST /api/v1/storage/array/drives/replace with missing fields"""
        response = storage_client.post(
            "/api/v1/storage/array/drives/replace",
            json={"old_device": "sda"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_add_stripe_invalid_json(self, storage_client):
        """Test POST /api/v1/storage/array/stripes with invalid JSON"""
        response = storage_client.post(
            "/api/v1/storage/array/stripes",
            data="invalid json"
        )
        
        assert response.status_code == 422  # Validation error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

