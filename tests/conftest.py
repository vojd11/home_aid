"""
Shared test fixtures and configuration for the Home Aid Kit Manager test suite.
"""

import asyncio
import os
import sys
from typing import Generator, AsyncGenerator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.models.household import Household
from app.models.medication import Medication


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing API endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    # Use test database URL
    test_db_url = settings.DATABASE_URL.replace("home_aid", "home_aid_test")
    
    engine = create_async_engine(test_db_url, echo=False)
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_household_data():
    """Sample household data for testing."""
    return {
        "name": "Test Household",
        "description": "A test household for testing purposes"
    }


@pytest.fixture
def test_medication_data():
    """Sample medication data for testing."""
    return {
        "name": "Test Medication",
        "quantity": 10,
        "unit": "tablets",
        "description": "A test medication",
        "location": "Medicine cabinet"
    }


@pytest.fixture
def mock_api_base_url():
    """Base URL for API tests."""
    return "http://localhost:8000"


@pytest.fixture
def auth_headers():
    """Helper to create authorization headers."""
    def _auth_headers(token: str):
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers


# Mark tests by category
pytest_plugins = []
