import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database import engine
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def async_session_factory():
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def test_recipe():
    return {
        "name": "Test Recipe",
        "cooking_time": "PT30M",
        "ingredients": json.dumps({"flour": "2 cups", "sugar": "1 cup"}),
        "description": "Test description",
        "views": 10,
    }
