"""
End-to-End Tests for Machine Workflow

Test complete machine management workflow:
1. Create machine
2. Assign image to machine
3. Configure machine
4. Power operations
5. Writeback management
6. Delete machine
"""

import pytest
from fastapi.testclient import TestClient


class TestMachineWorkflow:
    """Test complete machine workflow"""
    
    def test_create_and_manage_machine(self, client: TestClient):
        """Test complete machine lifecycle"""
        
        # Step 1: Create image first
        image_data = {
            "name": "test-image-for-machine",
            "type": "windows",
            "description": "Image for machine testing",
            "storage_path": "/srv/nfs/ggnet/images/test-image-for-machine"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image = response.json()
        image_id = image["image_id"]
        
        # Step 2: Create machine
        machine_data = {
            "name": "test-machine-01",
            "mac_address": "AA:BB:CC:DD:EE:01",
            "ip_address": "192.168.1.101",
            "image_id": image_id,
            "description": "Test machine 01"
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        created_machine = response.json()
        
        machine_id = created_machine["id"]
        assert created_machine["name"] == machine_data["name"]
        assert created_machine["mac_address"] == machine_data["mac_address"]
        assert created_machine["ip_address"] == machine_data["ip_address"]
        
        # Step 3: Get machine details
        response = client.get(f"/api/v1/machines/{machine_id}")
        assert response.status_code == 200
        machine = response.json()
        assert machine["name"] == machine_data["name"]
        
        # Step 4: List all machines
        response = client.get("/api/v1/machines")
        assert response.status_code == 200
        machines = response.json()
        assert len(machines) >= 1
        assert any(m["id"] == machine_id for m in machines)
        
        # Step 5: Update machine
        update_data = {
            "description": "Updated test machine 01",
            "keep_writeback": True
        }
        
        response = client.put(f"/api/v1/machines/{machine_id}", json=update_data)
        assert response.status_code == 200
        updated_machine = response.json()
        assert updated_machine["description"] == update_data["description"]
        assert updated_machine["keep_writeback"] == update_data["keep_writeback"]
        
        # Step 6: Power operations
        # Power on
        response = client.post(
            f"/api/v1/machines/{machine_id}/power",
            json={"operation": "power_on"}
        )
        assert response.status_code == 200
        
        # Power off
        response = client.post(
            f"/api/v1/machines/{machine_id}/power",
            json={"operation": "power_off"}
        )
        assert response.status_code == 200
        
        # Reboot
        response = client.post(
            f"/api/v1/machines/{machine_id}/power",
            json={"operation": "reboot"}
        )
        assert response.status_code == 200
        
        # Step 7: Set keep writeback
        response = client.post(
            f"/api/v1/machines/{machine_id}/writeback",
            json={"keep_writeback": True}
        )
        assert response.status_code == 200
        
        # Step 8: Delete machine
        response = client.delete(f"/api/v1/machines/{machine_id}")
        assert response.status_code == 200
        
        # Step 9: Verify deletion
        response = client.get(f"/api/v1/machines/{machine_id}")
        assert response.status_code == 404
        
        # Cleanup: Delete image
        client.delete(f"/api/v1/images/{image_id}")
    
    def test_create_multiple_machines(self, client: TestClient):
        """Test creating multiple machines"""
        
        # Create image
        image_data = {
            "name": "test-image-multi",
            "type": "windows",
            "description": "Image for multiple machines",
            "storage_path": "/srv/nfs/ggnet/images/test-image-multi"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Create multiple machines
        machines_data = [
            {
                "name": "test-machine-01",
                "mac_address": "AA:BB:CC:DD:EE:01",
                "ip_address": "192.168.1.101",
                "image_id": image_id
            },
            {
                "name": "test-machine-02",
                "mac_address": "AA:BB:CC:DD:EE:02",
                "ip_address": "192.168.1.102",
                "image_id": image_id
            },
            {
                "name": "test-machine-03",
                "mac_address": "AA:BB:CC:DD:EE:03",
                "ip_address": "192.168.1.103",
                "image_id": image_id
            }
        ]
        
        created_machines = []
        
        # Create all machines
        for machine_data in machines_data:
            response = client.post("/api/v1/machines", json=machine_data)
            assert response.status_code == 201
            created_machines.append(response.json())
        
        # Verify all machines were created
        assert len(created_machines) == 3
        
        # List machines and verify
        response = client.get("/api/v1/machines")
        assert response.status_code == 200
        all_machines = response.json()
        assert len(all_machines) >= 3
        
        # Verify each machine
        for created_machine in created_machines:
            machine_id = created_machine["id"]
            response = client.get(f"/api/v1/machines/{machine_id}")
            assert response.status_code == 200
            machine = response.json()
            assert machine["name"] == created_machine["name"]
        
        # Cleanup: Delete all machines
        for created_machine in created_machines:
            client.delete(f"/api/v1/machines/{created_machine['id']}")
        
        # Delete image
        client.delete(f"/api/v1/images/{image_id}")
    
    def test_machine_image_assignment(self, client: TestClient):
        """Test assigning different images to machines"""
        
        # Create multiple images
        images_data = [
            {
                "name": "test-image-windows",
                "type": "windows",
                "description": "Windows image",
                "storage_path": "/srv/nfs/ggnet/images/test-image-windows"
            },
            {
                "name": "test-image-linux",
                "type": "linux",
                "description": "Linux image",
                "storage_path": "/srv/nfs/ggnet/images/test-image-linux"
            }
        ]
        
        image_ids = []
        for img_data in images_data:
            response = client.post("/api/v1/images", json=img_data)
            assert response.status_code == 201
            image_ids.append(response.json()["image_id"])
        
        # Create machines with different images
        machine1_data = {
            "name": "test-machine-windows",
            "mac_address": "AA:BB:CC:DD:EE:10",
            "ip_address": "192.168.1.110",
            "image_id": image_ids[0]
        }
        
        machine2_data = {
            "name": "test-machine-linux",
            "mac_address": "AA:BB:CC:DD:EE:11",
            "ip_address": "192.168.1.111",
            "image_id": image_ids[1]
        }
        
        response = client.post("/api/v1/machines", json=machine1_data)
        assert response.status_code == 201
        machine1_id = response.json()["id"]
        
        response = client.post("/api/v1/machines", json=machine2_data)
        assert response.status_code == 201
        machine2_id = response.json()["id"]
        
        # Verify image assignments
        response = client.get(f"/api/v1/machines/{machine1_id}")
        assert response.status_code == 200
        machine1 = response.json()
        assert machine1["image_id"] == image_ids[0]
        
        response = client.get(f"/api/v1/machines/{machine2_id}")
        assert response.status_code == 200
        machine2 = response.json()
        assert machine2["image_id"] == image_ids[1]
        
        # Cleanup
        client.delete(f"/api/v1/machines/{machine1_id}")
        client.delete(f"/api/v1/machines/{machine2_id}")
        for img_id in image_ids:
            client.delete(f"/api/v1/images/{img_id}")
    
    def test_machine_validation(self, client: TestClient):
        """Test machine validation and error handling"""
        
        # Create image first
        image_data = {
            "name": "test-image-validation",
            "type": "windows",
            "description": "Image for validation",
            "storage_path": "/srv/nfs/ggnet/images/test-image-validation"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Test missing required fields
        invalid_machine = {
            "name": "test-invalid"
            # Missing required fields
        }
        
        response = client.post("/api/v1/machines", json=invalid_machine)
        assert response.status_code == 422  # Validation error
        
        # Test duplicate MAC address
        machine_data = {
            "name": "test-duplicate-mac",
            "mac_address": "AA:BB:CC:DD:EE:99",
            "ip_address": "192.168.1.199",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        machine_id = response.json()["id"]
        
        # Try to create duplicate
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 400  # Duplicate error
        
        # Cleanup
        client.delete(f"/api/v1/machines/{machine_id}")
        client.delete(f"/api/v1/images/{image_id}")
        
        # Test invalid MAC address format
        invalid_mac_machine = {
            "name": "test-invalid-mac",
            "mac_address": "INVALID:MAC:ADDRESS",
            "ip_address": "192.168.1.200",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=invalid_mac_machine)
        assert response.status_code in [400, 422]  # Invalid MAC format (Pydantic returns 422)
    
    def test_machine_status_tracking(self, client: TestClient):
        """Test machine status tracking"""
        
        # Create image
        image_data = {
            "name": "test-image-status",
            "type": "windows",
            "description": "Image for status tracking",
            "storage_path": "/srv/nfs/ggnet/images/test-image-status"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Create machine
        machine_data = {
            "name": "test-machine-status",
            "mac_address": "AA:BB:CC:DD:EE:88",
            "ip_address": "192.168.1.188",
            "image_id": image_id
        }
        
        response = client.post("/api/v1/machines", json=machine_data)
        assert response.status_code == 201
        machine_id = response.json()["id"]
        
        # Check initial status
        response = client.get(f"/api/v1/machines/{machine_id}")
        assert response.status_code == 200
        machine = response.json()
        assert machine["status"] == "offline"  # Default status
        
        # Update status
        update_data = {"status": "online"}
        response = client.put(f"/api/v1/machines/{machine_id}", json=update_data)
        assert response.status_code == 200
        updated_machine = response.json()
        assert updated_machine["status"] == "online"
        
        # Cleanup
        client.delete(f"/api/v1/machines/{machine_id}")
        client.delete(f"/api/v1/images/{image_id}")

