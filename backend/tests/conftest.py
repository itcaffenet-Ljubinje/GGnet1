"""
Shared pytest fixtures for all tests
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_db():
    """Create mock database session with async support"""
    from datetime import datetime
    import uuid
    
    db = MagicMock()
    
    # Make async methods actually awaitable
    db.commit = AsyncMock()
    db.execute = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    
    # Mock refresh to populate database-generated fields
    async def mock_refresh(obj):
        """Simulate database refresh by populating generated fields"""
        if hasattr(obj, 'image_id') and obj.image_id is None:
            obj.image_id = str(uuid.uuid4())
        if hasattr(obj, 'version') and obj.version is None:
            obj.version = 1
        if hasattr(obj, 'creation_date') and obj.creation_date is None:
            obj.creation_date = datetime.now()
    
    db.refresh = AsyncMock(side_effect=mock_refresh)
    
    return db


@pytest.fixture
def client(mock_db):
    """
    Create test client with mocked dependencies
    
    This fixture is shared across all tests that need FastAPI TestClient
    """
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

