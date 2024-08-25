import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.database import VectorDatabase
from app.api.v1.dependencies import get_vector_db

class VersionedAPIClient:
    def __init__(self, client, version):
        self.client = client
        self.base_url = f"/api/{version}"

    def request(self, method, url, *args, **kwargs):
        return getattr(self.client, method)(f"{self.base_url}{url}", *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self.request('get', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request('post', url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self.request('put', url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.request('delete', url, *args, **kwargs)

@pytest.fixture(params=['kdtree', 'balltree', 'bruteforce'])
def vector_db(request):
    return VectorDatabase(indexing_algorithm=request.param)

@pytest.fixture
def test_app(vector_db):
    app = create_app()
    app.state.vector_db = vector_db
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

@pytest.fixture(params=['v1'])  # Add 'v2' here when v2 is implemented
def api_client(request, client):
    return VersionedAPIClient(client, request.param)

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

@pytest.fixture
def sample_chunk():
    return {
        "id": "test-chunk",
        "text": "This is a test chunk",
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        "metadata": {"position": 1}
    }