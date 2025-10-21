"""
End-to-End Tests for Image Workflow

Test complete image management workflow:
1. Create image
2. Upload image files
3. List images
4. Get image details
5. Update image
6. Delete image
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
    from sqlalchemy import text
    
    async def cleanup():
        async with async_session_maker() as session:
            # Delete all records in order (respecting foreign keys)
            await session.execute(text("DELETE FROM snapshots"))
            await session.execute(text("DELETE FROM writebacks"))
            await session.execute(text("DELETE FROM machines"))
            await session.execute(text("DELETE FROM images"))
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
    """Create test client"""
    return TestClient(app)


class TestImageWorkflow:
    """Test complete image workflow"""
    
    def test_create_and_manage_image(self, client: TestClient):
        """Test complete image lifecycle"""
        
        # Step 1: Create image
        image_data = {
            "name": "test-windows-10",
            "type": "windows",
            "description": "Windows 10 test image",
            "storage_path": "/srv/nfs/ggnet/images/test-windows-10",
            "size_bytes": 1024 * 1024 * 1024 * 20,  # 20GB
            "is_default": False
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        created_image = response.json()
        
        image_id = created_image["image_id"]
        assert created_image["name"] == image_data["name"]
        assert created_image["type"] == image_data["type"]
        assert created_image["description"] == image_data["description"]
        
        # Step 2: Get image details
        response = client.get(f"/api/v1/images/{image_id}")
        assert response.status_code == 200
        image = response.json()
        assert image["name"] == image_data["name"]
        
        # Step 3: List all images
        response = client.get("/api/v1/images")
        assert response.status_code == 200
        images = response.json()
        assert len(images) >= 1
        assert any(img["image_id"] == image_id for img in images)
        
        # Step 4: Update image
        update_data = {
            "description": "Updated Windows 10 test image",
            "is_default": True
        }
        
        response = client.put(f"/api/v1/images/{image_id}", json=update_data)
        assert response.status_code == 200
        updated_image = response.json()
        assert updated_image["description"] == update_data["description"]
        assert updated_image["is_default"] == update_data["is_default"]
        
        # Step 5: Delete image
        response = client.delete(f"/api/v1/images/{image_id}")
        assert response.status_code == 200
        
        # Step 6: Verify deletion
        response = client.get(f"/api/v1/images/{image_id}")
        assert response.status_code == 404
    
    def test_create_multiple_images(self, client: TestClient):
        """Test creating multiple images"""
        
        images_data = [
            {
                "name": "test-windows-10",
                "type": "windows",
                "description": "Windows 10",
                "storage_path": "/srv/nfs/ggnet/images/test-windows-10"
            },
            {
                "name": "test-windows-11",
                "type": "windows",
                "description": "Windows 11",
                "storage_path": "/srv/nfs/ggnet/images/test-windows-11"
            },
            {
                "name": "test-linux-ubuntu",
                "type": "linux",
                "description": "Ubuntu 22.04",
                "storage_path": "/srv/nfs/ggnet/images/test-linux-ubuntu"
            }
        ]
        
        created_images = []
        
        # Create all images
        for img_data in images_data:
            response = client.post("/api/v1/images", json=img_data)
            assert response.status_code == 201
            created_images.append(response.json())
        
        # Verify all images were created
        assert len(created_images) == 3
        
        # List images and verify
        response = client.get("/api/v1/images")
        assert response.status_code == 200
        all_images = response.json()
        assert len(all_images) >= 3
        
        # Verify each image
        for created_img in created_images:
            image_id = created_img["image_id"]
            response = client.get(f"/api/v1/images/{image_id}")
            assert response.status_code == 200
            img = response.json()
            assert img["name"] == created_img["name"]
        
        # Cleanup: Delete all created images
        for created_img in created_images:
            client.delete(f"/api/v1/images/{created_img['image_id']}")
    
    def test_image_filtering(self, client: TestClient):
        """Test filtering images by type"""
        
        # Create different type images
        windows_image = {
            "name": "test-windows-filter",
            "type": "windows",
            "description": "Windows image for filtering",
            "storage_path": "/srv/nfs/ggnet/images/test-windows-filter"
        }
        
        linux_image = {
            "name": "test-linux-filter",
            "type": "linux",
            "description": "Linux image for filtering",
            "storage_path": "/srv/nfs/ggnet/images/test-linux-filter"
        }
        
        # Create images
        response = client.post("/api/v1/images", json=windows_image)
        assert response.status_code == 201
        windows_id = response.json()["image_id"]
        
        response = client.post("/api/v1/images", json=linux_image)
        assert response.status_code == 201
        linux_id = response.json()["image_id"]
        
        # Filter by type
        response = client.get("/api/v1/images?type=windows")
        assert response.status_code == 200
        windows_images = response.json()
        assert all(img["type"] == "windows" for img in windows_images)
        
        response = client.get("/api/v1/images?type=linux")
        assert response.status_code == 200
        linux_images = response.json()
        assert all(img["type"] == "linux" for img in linux_images)
        
        # Cleanup
        client.delete(f"/api/v1/images/{windows_id}")
        client.delete(f"/api/v1/images/{linux_id}")
    
    def test_image_default_flag(self, client: TestClient):
        """Test image default flag behavior"""
        
        # Create first image as default
        image1_data = {
            "name": "test-default-1",
            "type": "windows",
            "description": "First default image",
            "storage_path": "/srv/nfs/ggnet/images/test-default-1",
            "is_default": True
        }
        
        response = client.post("/api/v1/images", json=image1_data)
        assert response.status_code == 201
        image1 = response.json()
        assert image1["is_default"] is True
        
        # Create second image as default (should unset first)
        image2_data = {
            "name": "test-default-2",
            "type": "windows",
            "description": "Second default image",
            "storage_path": "/srv/nfs/ggnet/images/test-default-2",
            "is_default": True
        }
        
        response = client.post("/api/v1/images", json=image2_data)
        assert response.status_code == 201
        image2 = response.json()
        assert image2["is_default"] is True
        
        # Verify first image is no longer default
        response = client.get(f"/api/v1/images/{image1['image_id']}")
        assert response.status_code == 200
        updated_image1 = response.json()
        assert updated_image1["is_default"] is False
        
        # Cleanup
        client.delete(f"/api/v1/images/{image1['image_id']}")
        client.delete(f"/api/v1/images/{image2['image_id']}")
    
    def test_image_validation(self, client: TestClient):
        """Test image validation and error handling"""
        
        # Test missing required fields
        invalid_image = {
            "name": "test-invalid"
            # Missing required fields
        }
        
        response = client.post("/api/v1/images", json=invalid_image)
        assert response.status_code == 422  # Validation error
        
        # Test duplicate name
        image_data = {
            "name": "test-duplicate",
            "type": "windows",
            "description": "Test duplicate",
            "storage_path": "/srv/nfs/ggnet/images/test-duplicate"
        }
        
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 201
        image_id = response.json()["image_id"]
        
        # Try to create duplicate
        response = client.post("/api/v1/images", json=image_data)
        assert response.status_code == 400  # Duplicate error
        
        # Cleanup
        client.delete(f"/api/v1/images/{image_id}")
        
        # Test invalid image type
        invalid_type_image = {
            "name": "test-invalid-type",
            "type": "invalid_type",
            "description": "Test invalid type",
            "storage_path": "/srv/nfs/ggnet/images/test-invalid-type"
        }
        
        response = client.post("/api/v1/images", json=invalid_type_image)
        assert response.status_code == 422  # Validation error

