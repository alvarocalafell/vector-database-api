import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.di_container import Container

@pytest.fixture
def client():
    container = Container()
    # Set the indexing algorithm for tests
    container.config.indexing_algorithm.from_value("kd_tree")
    container.wire(modules=["app.adapters.api.v1.routes.library_routes"])
    
    app.container = container
    return TestClient(app)

def test_create_library(client):
    response = client.post(
        "/api/v1/libraries",
        json={"id": "1", "name": "Test Library"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": "1", "name": "Test Library", "documents": [], "metadata": {}}

def test_get_library(client):
    # First, create a library
    client.post("/api/v1/libraries", json={"id": "1", "name": "Test Library"})
    
    # Then, get the library
    response = client.get("/api/v1/libraries/1")
    assert response.status_code == 200
    assert response.json() == {"id": "1", "name": "Test Library", "documents": [], "metadata": {}}

def test_update_library(client):
    # First, create a library
    client.post("/api/v1/libraries", json={"id": "1", "name": "Test Library"})
    
    # Then, update the library
    response = client.put(
        "/api/v1/libraries/1",
        json={"id": "1", "name": "Updated Test Library"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": "1", "name": "Updated Test Library", "documents": [], "metadata": {}}

def test_delete_library(client):
    # First, create a library
    client.post("/api/v1/libraries", json={"id": "1", "name": "Test Library"})
    
    # Then, delete the library
    response = client.delete("/api/v1/libraries/1")
    assert response.status_code == 204
    
    # Verify that the library is deleted
    response = client.get("/api/v1/libraries/1")
    assert response.status_code == 404