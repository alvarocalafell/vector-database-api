import logging
import pytest
import time

logger = logging.getLogger(__name__)

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

def test_add_document(client, vector_db, sample_library, sample_document):
    logger.debug("Starting test_add_document")
    
    # Create a library first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 201, f"Failed to create library: {response.json()}"
    
    # Add a document to the library
    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 201, f"Failed to add document: {response.json()}"
    assert response.json() == sample_document
    
    logger.debug("Finished test_add_document")

def test_get_document(client, vector_db, sample_library, sample_document):
    logger.debug("Starting test_get_document")
    
    # Create a library
    logger.debug("Creating library")
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 201, f"Failed to create library: {response.json()}"
    logger.debug("Library created successfully")

    # Add a document
    logger.debug("Adding document to library")
    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 201, f"Failed to add document: {response.json()}"
    logger.debug("Document added successfully")

    # Add a small delay
    time.sleep(0.1)

    # Retrieve the document
    logger.debug(f"Attempting to retrieve document {sample_document['id']} from library {sample_library['id']}")
    response = client.get(f"/documents/{sample_library['id']}/{sample_document['id']}")
    logger.debug(f"Received response with status code {response.status_code}")
    assert response.status_code == 200, f"Failed to get document: {response.json()}"
    assert response.json() == sample_document, f"Retrieved document does not match: {response.json()}"
    
    logger.debug("Finished test_get_document")

def test_update_document(client, vector_db, sample_library, sample_document):
    logger.debug("Starting test_update_document")
    
    # Create a library
    logger.debug("Creating library")
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 201, f"Failed to create library: {response.json()}"
    logger.debug("Library created successfully")

    # Add a document
    logger.debug("Adding document to library")
    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 201, f"Failed to add document: {response.json()}"
    logger.debug("Document added successfully")

    # Add a small delay
    time.sleep(0.1)

    # Update the document
    logger.debug(f"Attempting to update document {sample_document['id']} in library {sample_library['id']}")
    updated_document = {**sample_document, "metadata": {"name": "Updated Document"}}
    response = client.put(f"/documents/{sample_library['id']}/{sample_document['id']}", json=updated_document)
    logger.debug(f"Received response with status code {response.status_code}")
    assert response.status_code == 200, f"Failed to update document: {response.json()}"
    assert response.json()["metadata"]["name"] == "Updated Document", f"Document not updated correctly: {response.json()}"
    
    logger.debug("Finished test_update_document")

def test_delete_document(client, vector_db, sample_library, sample_document):
    logger.debug("Starting test_delete_document")
    
    # Create a library
    logger.debug("Creating library")
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 201, f"Failed to create library: {response.json()}"
    logger.debug("Library created successfully")

    # Add a document
    logger.debug("Adding document to library")
    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 201, f"Failed to add document: {response.json()}"
    logger.debug("Document added successfully")

    # Add a small delay
    time.sleep(0.1)

    # Delete the document
    logger.debug(f"Attempting to delete document {sample_document['id']} from library {sample_library['id']}")
    response = client.delete(f"/documents/{sample_library['id']}/{sample_document['id']}")
    logger.debug(f"Received response with status code {response.status_code}")
    assert response.status_code == 200, f"Failed to delete document: {response.json()}"
    
    # Verify the document is deleted
    logger.debug(f"Verifying document {sample_document['id']} is deleted from library {sample_library['id']}")
    response = client.get(f"/documents/{sample_library['id']}/{sample_document['id']}")
    logger.debug(f"Received response with status code {response.status_code}")
    assert response.status_code == 404, f"Document not deleted: {response.json()}"
    
    logger.debug("Finished test_delete_document")

def test_add_document_to_nonexistent_library(client, vector_db, sample_document):
    logger.debug("Starting test_add_document_to_nonexistent_library")
    
    response = client.post("/documents/nonexistent", json=sample_document)
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
    
    logger.debug("Finished test_add_document_to_nonexistent_library")

def test_get_document_from_nonexistent_library(client, vector_db):
    logger.debug("Starting test_get_document_from_nonexistent_library")
    
    response = client.get("/documents/nonexistent/doc_id")
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
    
    logger.debug("Finished test_get_document_from_nonexistent_library")

def test_update_document_in_nonexistent_library(client, vector_db, sample_document):
    logger.debug("Starting test_update_document_in_nonexistent_library")
    
    nonexistent_library_id = "nonexistent-library"
    document_id = sample_document["id"]
    
    logger.debug(f"Attempting to update document {document_id} in nonexistent library {nonexistent_library_id}")
    response = client.put(f"/documents/{nonexistent_library_id}/{document_id}", json=sample_document)
    
    logger.debug(f"Received response with status code {response.status_code}")
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}. Response: {response.json()}"
    assert response.json()["detail"] == f"404: Library with id {nonexistent_library_id} not found", f"Unexpected error message: {response.json()['detail']}"
    
    logger.debug("Finished test_update_document_in_nonexistent_library")

def test_delete_document_from_nonexistent_library(client, vector_db):
    logger.debug("Starting test_delete_document_from_nonexistent_library")
    
    response = client.delete("/documents/nonexistent/doc_id")
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
    
    logger.debug("Finished test_delete_document_from_nonexistent_library")