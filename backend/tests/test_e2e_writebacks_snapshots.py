"""
End-to-End Tests for Writeback and Snapshot Workflow

Test complete writeback and snapshot management:
1. Create writeback
2. Apply writeback
3. Discard writeback
4. Create snapshot from writeback
5. Restore snapshot
6. Delete snapshot
"""

import pytest
from fastapi.testclient import TestClient


class TestWritebackWorkflow:
    """Test complete writeback workflow"""
    
    def test_create_and_manage_writeback(self, client: TestClient):
        """Test complete writeback lifecycle"""
        
        # Step 1: Create image
        image_data = {
            "name": "test-image-writeback",
            "type": "windows",
            "description": "Image for writeback testing",
            "storage_path": "/srv/nfs/ggnet/images/test-image-writeback"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Step 2: Create machine
        machine_data = {
            "name": "test-machine-writeback",
            "mac_address": "AA:BB:CC:DD:EE:50",
            "ip_address": "192.168.1.150",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        machine_id = response.json()["id"]
        
        # Step 3: Create writeback
        writeback_data = {
            "attached_client_id": str(machine_id),
            "base_image_id": image_id,
            "size_of_changes": 1024 * 1024 * 100  # 100MB
        }
        
        response = client.post("/api/v1/writebacks", json=writeback_data)
        assert response.status_code == 201
        created_writeback = response.json()
        
        writeback_id = created_writeback["writeback_id"]
        assert created_writeback["attached_client_id"] == str(machine_id)
        assert created_writeback["base_image_id"] == image_id
        
        # Step 4: Get writeback details
        response = client.get(f"/api/v1/writebacks/{writeback_id}")
        assert response.status_code == 200
        writeback = response.json()
        assert writeback["writeback_id"] == writeback_id
        
        # Step 5: List all writebacks
        response = client.get("/api/v1/writebacks")
        assert response.status_code == 200
        writebacks = response.json()
        assert len(writebacks) >= 1
        assert any(wb["writeback_id"] == writeback_id for wb in writebacks)
        
        # Step 6: Apply writeback
        response = client.post(f"/api/v1/writebacks/{writeback_id}/apply")
        assert response.status_code == 200
        applied_writeback = response.json()
        assert applied_writeback["status"] == "applied"
        
        # Cleanup
        client.delete(f"/api/v1/machines/{machine_id}")
        client.delete(f"/api/v1/images/{image_id}")
    
    def test_discard_writeback(self, client: TestClient):
        """Test discarding writeback"""
        
        # Create image
        image_data = {
            "name": "test-image-discard",
            "type": "windows",
            "description": "Image for discard testing",
            "storage_path": "/srv/nfs/ggnet/images/test-image-discard"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Create machine
        machine_data = {
            "name": "test-machine-discard",
            "mac_address": "AA:BB:CC:DD:EE:51",
            "ip_address": "192.168.1.151",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        machine_id = response.json()["id"]
        
        # Create writeback
        writeback_data = {
            "attached_client_id": str(machine_id),
            "base_image_id": image_id,
            "size_of_changes": 1024 * 1024 * 50  # 50MB
        }
        
        response = client.post("/api/v1/writebacks", json=writeback_data)
        assert response.status_code == 201
        writeback_id = response.json()["writeback_id"]
        
        # Discard writeback
        response = client.post(f"/api/v1/writebacks/{writeback_id}/discard")
        assert response.status_code == 200
        discarded_writeback = response.json()
        assert discarded_writeback["status"] == "discarded"
        
        # Cleanup
        client.delete(f"/api/v1/machines/{machine_id}")
        client.delete(f"/api/v1/images/{image_id}")


class TestSnapshotWorkflow:
    """Test complete snapshot workflow"""
    
    def test_create_and_manage_snapshot(self, client: TestClient):
        """Test complete snapshot lifecycle"""
        
        # Step 1: Create image
        image_data = {
            "name": "test-image-snapshot",
            "type": "windows",
            "description": "Image for snapshot testing",
            "storage_path": "/srv/nfs/ggnet/images/test-image-snapshot"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Step 2: Create snapshot
        snapshot_data = {
            "name": "test-snapshot-01",
            "base_image_id": image_id,
            "description": "Test snapshot 01",
            "size_bytes": 1024 * 1024 * 500  # 500MB
        }
        
        response = client.post("/api/v1/snapshots", json=snapshot_data)
        assert response.status_code == 201
        created_snapshot = response.json()
        
        snapshot_id = created_snapshot["snapshot_id"]
        assert created_snapshot["name"] == snapshot_data["name"]
        assert created_snapshot["base_image_id"] == image_id
        
        # Step 3: Get snapshot details
        response = client.get(f"/api/v1/snapshots/{snapshot_id}")
        assert response.status_code == 200
        snapshot = response.json()
        assert snapshot["snapshot_id"] == snapshot_id
        
        # Step 4: List all snapshots
        response = client.get("/api/v1/snapshots")
        assert response.status_code == 200
        snapshots = response.json()
        assert len(snapshots) >= 1
        assert any(sn["snapshot_id"] == snapshot_id for sn in snapshots)
        
        # Step 5: Restore snapshot
        response = client.post(f"/api/v1/snapshots/{snapshot_id}/restore")
        assert response.status_code == 200
        restored_snapshot = response.json()
        assert restored_snapshot["status"] == "restored"
        
        # Step 6: Delete snapshot
        response = client.delete(f"/api/v1/snapshots/{snapshot_id}")
        assert response.status_code == 200
        
        # Step 7: Verify deletion
        response = client.get(f"/api/v1/snapshots/{snapshot_id}")
        assert response.status_code == 404
        
        # Cleanup
        client.delete(f"/api/v1/images/{image_id}")
    
    def test_create_snapshot_from_writeback(self, client: TestClient):
        """Test creating snapshot from writeback"""
        
        # Create image
        image_data = {
            "name": "test-image-snapshot-writeback",
            "type": "windows",
            "description": "Image for snapshot from writeback",
            "storage_path": "/srv/nfs/ggnet/images/test-image-snapshot-writeback"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Create machine
        machine_data = {
            "name": "test-machine-snapshot-writeback",
            "mac_address": "AA:BB:CC:DD:EE:60",
            "ip_address": "192.168.1.160",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        machine_id = response.json()["id"]
        
        # Create writeback
        writeback_data = {
            "attached_client_id": str(machine_id),
            "base_image_id": image_id,
            "size_of_changes": 1024 * 1024 * 75  # 75MB
        }
        
        response = client.post("/api/v1/writebacks", json=writeback_data)
        assert response.status_code == 201
        writeback_id = response.json()["writeback_id"]
        
        # Create snapshot from writeback
        snapshot_data = {
            "name": "test-snapshot-from-writeback",
            "base_image_id": image_id,
            "source_writeback_id": writeback_id,
            "description": "Snapshot from writeback",
            "size_bytes": 1024 * 1024 * 100  # 100MB
        }
        
        response = client.post("/api/v1/snapshots", json=snapshot_data)
        assert response.status_code == 201
        snapshot = response.json()
        
        assert snapshot["name"] == snapshot_data["name"]
        assert snapshot["source_writeback_id"] == writeback_id
        
        # Cleanup
        client.delete(f"/api/v1/snapshots/{snapshot['snapshot_id']}")
        client.delete(f"/api/v1/machines/{machine_id}")
        client.delete(f"/api/v1/images/{image_id}")
    
    def test_snapshot_protection(self, client: TestClient):
        """Test snapshot protection"""
        
        # Create image
        image_data = {
            "name": "test-image-protected",
            "type": "windows",
            "description": "Image for protected snapshot",
            "storage_path": "/srv/nfs/ggnet/images/test-image-protected"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Create protected snapshot
        snapshot_data = {
            "name": "test-protected-snapshot",
            "base_image_id": image_id,
            "description": "Protected snapshot",
            "protected": True,
            "size_bytes": 1024 * 1024 * 200  # 200MB
        }
        
        response = client.post("/api/v1/snapshots", json=snapshot_data)
        assert response.status_code == 201
        snapshot = response.json()
        
        assert snapshot["protected"] is True
        
        # Try to delete protected snapshot (should fail)
        response = client.delete(f"/api/v1/snapshots/{snapshot['snapshot_id']}")
        assert response.status_code == 400  # Cannot delete protected snapshot
        
        # Update snapshot to unprotected
        update_data = {"protected": False}
        response = client.put(f"/api/v1/snapshots/{snapshot['snapshot_id']}", json=update_data)
        assert response.status_code == 200
        updated_snapshot = response.json()
        assert updated_snapshot["protected"] is False
        
        # Now delete should work
        response = client.delete(f"/api/v1/snapshots/{snapshot['snapshot_id']}")
        assert response.status_code == 200
        
        # Cleanup
        client.delete(f"/api/v1/images/{image_id}")


class TestIntegratedWorkflow:
    """Test integrated writeback and snapshot workflow"""
    
    def test_complete_workflow(self, client: TestClient):
        """Test complete workflow: image → machine → writeback → snapshot → restore"""
        
        # Step 1: Create image
        image_data = {
            "name": "test-image-complete",
            "type": "windows",
            "description": "Image for complete workflow",
            "storage_path": "/srv/nfs/ggnet/images/test-image-complete"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Step 2: Create machine
        machine_data = {
            "name": "test-machine-complete",
            "mac_address": "AA:BB:CC:DD:EE:70",
            "ip_address": "192.168.1.170",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        machine_id = response.json()["id"]
        
        # Step 3: Create writeback
        writeback_data = {
            "attached_client_id": str(machine_id),
            "base_image_id": image_id,
            "size_of_changes": 1024 * 1024 * 150  # 150MB
        }
        
        response = client.post("/api/v1/writebacks", json=writeback_data)
        assert response.status_code == 201
        writeback_id = response.json()["writeback_id"]
        
        # Step 4: Create snapshot from writeback
        snapshot_data = {
            "name": "test-snapshot-complete",
            "base_image_id": image_id,
            "source_writeback_id": writeback_id,
            "description": "Snapshot from complete workflow",
            "size_bytes": 1024 * 1024 * 200  # 200MB
        }
        
        response = client.post("/api/v1/snapshots", json=snapshot_data)
        assert response.status_code == 201
        snapshot_id = response.json()["snapshot_id"]
        
        # Step 5: Restore snapshot
        response = client.post(f"/api/v1/snapshots/{snapshot_id}/restore")
        assert response.status_code == 200
        
        # Step 6: Apply writeback
        response = client.post(f"/api/v1/writebacks/{writeback_id}/apply")
        assert response.status_code == 200
        
        # Step 7: Cleanup
        client.delete(f"/api/v1/snapshots/{snapshot_id}")
        client.delete(f"/api/v1/machines/{machine_id}")
        client.delete(f"/api/v1/images/{image_id}")

