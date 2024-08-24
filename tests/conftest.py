import logging
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.database import VectorDatabase


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def test_app():
    app = create_app()
    return app

@pytest.fixture(scope="function")
def client(test_app):
    return TestClient(test_app)

@pytest.fixture(scope="function")
def vector_db(test_app):
    # Reset the VectorDatabase before each test
    test_app.state.vector_db = VectorDatabase()
    return test_app.state.vector_db

@pytest.fixture
def sample_library():
    return {
        "id": "test-library",
        "documents": [],
        "metadata": {
            "name": "Test Library",
            "description": "A library for testing purposes"
        }
    }

@pytest.fixture
def sample_document():
    return {
        "id": "test-document",
        "chunks": [
            {
                "id": "chunk-1",
                "text": "This is a test chunk",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "metadata": {"position": 1}
            }
        ],
        "metadata": {
            "name": "Test Document",
            "author": "Test Author"
        }
    }