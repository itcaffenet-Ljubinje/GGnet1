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
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    
    # Mock execute to return a mock result with scalars()
    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none = MagicMock(return_value=None)
        result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        return result
    
    db.execute = AsyncMock(side_effect=mock_execute)
    db.delete = MagicMock()  # Synchronous delete
    
    # Mock refresh to populate database-generated fields
    async def mock_refresh(obj):
        """Simulate database refresh by populating generated fields"""
        # Image fields
        if hasattr(obj, 'image_id') and obj.image_id is None:
            obj.image_id = str(uuid.uuid4())
        if hasattr(obj, 'version') and obj.version is None:
            obj.version = 1
        if hasattr(obj, 'creation_date') and obj.creation_date is None:
            obj.creation_date = datetime.now()
        
        # Machine fields
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = 1
        if hasattr(obj, 'writeback_size') and obj.writeback_size is None:
            obj.writeback_size = 0
        if hasattr(obj, 'keep_writeback') and obj.keep_writeback is None:
            obj.keep_writeback = False
        
        # Snapshot fields
        if hasattr(obj, 'snapshot_id') and obj.snapshot_id is None:
            obj.snapshot_id = str(uuid.uuid4())
        if hasattr(obj, 'date_created') and obj.date_created is None:
            obj.date_created = datetime.now()
        
        # Writeback fields
        if hasattr(obj, 'writeback_id') and obj.writeback_id is None:
            obj.writeback_id = str(uuid.uuid4())
        if hasattr(obj, 'created_at') and obj.created_at is None:
            obj.created_at = datetime.now()
    
    db.refresh = AsyncMock(side_effect=mock_refresh)
    
    return db


@pytest.fixture
def mock_client(mock_db):
    """
    Create test client with mocked database for unit/integration tests
    
    Use this for tests that don't need real database.
    E2E tests should define their own 'client' fixture with real DB.
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

