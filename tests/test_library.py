import logging
from app.models.data_models import Library

logger = logging.getLogger(__name__)

def test_create_library(client, vector_db, sample_library):
    logger.debug("Starting test_create_library")
    response = client.post("/libraries/", json=sample_library)
    logger.debug(f"Response status code: {response.status_code}")
    assert response.status_code == 201
    assert response.json() == sample_library
    logger.debug("Finished test_create_library")

def test_get_library(client, vector_db, sample_library):
    client.post("/libraries/", json=sample_library)
    response = client.get(f"/libraries/{sample_library['id']}")
    assert response.status_code == 200
    assert response.json() == sample_library


def test_update_library_metadata(client, vector_db, sample_library):
    logger.debug("Starting test_update_library_metadata")
    
    # Create the library
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 201, f"Failed to create library: {response.json()}"
    
    # Update only the metadata
    updated_metadata = {"name": "Updated Library", "description": "Updated description"}
    updated_library = {**sample_library, "metadata": updated_metadata}
    
    response = client.put(f"/libraries/{sample_library['id']}", json=updated_library)
    assert response.status_code == 200, f"Failed to update library: {response.json()}"
    
    updated_response = response.json()
    assert updated_response["metadata"] == updated_metadata, f"Metadata not updated correctly: {updated_response}"
    assert updated_response["documents"] == sample_library["documents"], "Documents should remain unchanged"
        
    logger.debug("Finished test_update_library_metadata")

def test_delete_library(client, vector_db, sample_library):
    client.post("/libraries/", json=sample_library)
    response = client.delete(f"/libraries/{sample_library['id']}")
    assert response.status_code == 200
    response = client.get(f"/libraries/{sample_library['id']}")
    assert response.status_code == 404

def test_create_existing_library(client, vector_db, sample_library):
    client.post("/libraries/", json=sample_library)
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 400

def test_get_nonexistent_library(client, vector_db):
    response = client.get("/libraries/nonexistent")
    assert response.status_code == 404

def test_update_nonexistent_library(client, vector_db, sample_library):
    # Test updating a non-existent library
    nonexistent_id = "nonexistent"
    updated_library = {
        "metadata": sample_library["metadata"]
    }
    response = client.put(f"/libraries/{nonexistent_id}", json=updated_library)
    
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response headers: {response.headers}")
    logger.info(f"Response body: {response.json()}")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.json()}"
    
    error_detail = response.json()["detail"]
    logger.info(f"Error detail: {error_detail}")
    
    #expected_message = f"Library with id {nonexistent_id} not found"
    expected_message = f"404: Library with id {nonexistent_id} not found"
    assert error_detail == expected_message, f"Expected '{expected_message}', got '{error_detail}'"


    # Test with mismatched IDs
    existing_library_id = "existing_library"
    vector_db.create_library(Library(id=existing_library_id, documents=[], metadata={}))
    mismatched_library = {
        "metadata": sample_library["metadata"]
    }
    response = client.put(f"/libraries/{existing_library_id}", json=mismatched_library)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    
    # Verify that the library was actually updated
    updated_library = vector_db.get_library(existing_library_id)
    assert updated_library.metadata == sample_library["metadata"]
    
def test_delete_nonexistent_library(client, vector_db):
    response = client.delete("/libraries/nonexistent")
    assert response.status_code == 404