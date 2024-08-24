import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import VectorDatabase
from .utils import get_cohere_embedding
import logging

logger = logging.getLogger(__name__)

client = TestClient(app)

@pytest.fixture
def vector_db():
    return VectorDatabase()

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

def test_add_and_search_with_cohere_embeddings(client, vector_db, sample_library):
    logger.debug("Starting test_add_and_search_with_cohere_embeddings")
    
    # Create a library
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"
    
    # Create documents with Cohere embeddings
    texts = ["The quick brown fox jumps over the lazy dog",
             "A journey of a thousand miles begins with a single step",
             "To be or not to be, that is the question"]
    
    for i, text in enumerate(texts):
        embedding = get_cohere_embedding(text)
        document = {
            "id": f"doc-{i}",
            "chunks": [{
                "id": f"chunk-{i}",
                "text": text,
                "embedding": embedding,
                "metadata": {"position": i}
            }]
        }
        response = client.post(f"/documents/{sample_library['id']}", json=document)
        assert response.status_code == 200, f"Failed to add document: {response.json()}"
    
    # Perform a search
    search_text = "What is the meaning of life?"
    search_embedding = get_cohere_embedding(search_text)
    search_query = {
        "query_vector": search_embedding,
        "k": 2
    }
    
    response = client.post(f"/search/{sample_library['id']}", json=search_query)
    assert response.status_code == 200, f"Search failed: {response.json()}"
    
    results = response.json()
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    logger.debug(f"Search results: {results}")
    
    # Verify that the results are sorted by distance
    assert results[0]['distance'] <= results[1]['distance'], "Results are not sorted by distance"
    
    logger.debug("Finished test_add_and_search_with_cohere_embeddings")

def test_update_document_with_cohere_embeddings(client, vector_db, sample_library):
    logger.debug("Starting test_update_document_with_cohere_embeddings")
    
    # Create a library
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"
    
    # Create a document with Cohere embedding
    original_text = "The sky is blue"
    original_embedding = get_cohere_embedding(original_text)
    document = {
        "id": "doc-1",
        "chunks": [{
            "id": "chunk-1",
            "text": original_text,
            "embedding": original_embedding,
            "metadata": {"position": 1}
        }]
    }
    response = client.post(f"/documents/{sample_library['id']}", json=document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"
    
    # Update the document with a new embedding
    updated_text = "The grass is green"
    updated_embedding = get_cohere_embedding(updated_text)
    updated_document = {
        "id": "doc-1",
        "chunks": [{
            "id": "chunk-1",
            "text": updated_text,
            "embedding": updated_embedding,
            "metadata": {"position": 1}
        }]
    }
    response = client.put(f"/documents/{sample_library['id']}/doc-1", json=updated_document)
    assert response.status_code == 200, f"Failed to update document: {response.json()}"
    
    # Perform a search with the updated text
    search_query = {
        "query_vector": updated_embedding,
        "k": 1
    }
    response = client.post(f"/search/{sample_library['id']}", json=search_query)
    assert response.status_code == 200, f"Search failed: {response.json()}"
    
    results = response.json()
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    assert results[0]['chunk']['text'] == updated_text, f"Unexpected search result: {results[0]}"
    
    logger.debug("Finished test_update_document_with_cohere_embeddings")

def test_delete_document_with_cohere_embeddings(client, vector_db, sample_library):
    logger.debug("Starting test_delete_document_with_cohere_embeddings")
    
    # Create a library
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"
    
    # Create a document with Cohere embedding
    text = "This document will be deleted"
    embedding = get_cohere_embedding(text)
    document = {
        "id": "doc-to-delete",
        "chunks": [{
            "id": "chunk-to-delete",
            "text": text,
            "embedding": embedding,
            "metadata": {"position": 1}
        }]
    }
    response = client.post(f"/documents/{sample_library['id']}", json=document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"
    
    # Delete the document
    response = client.delete(f"/documents/{sample_library['id']}/doc-to-delete")
    assert response.status_code == 200, f"Failed to delete document: {response.json()}"
    
    # Attempt to search for the deleted document
    search_query = {
        "query_vector": embedding,
        "k": 1
    }
    response = client.post(f"/search/{sample_library['id']}", json=search_query)
    assert response.status_code == 200, f"Search failed: {response.json()}"
    
    results = response.json()
    assert len(results) == 0, f"Expected 0 results, got {len(results)}"
    
    logger.debug("Finished test_delete_document_with_cohere_embeddings")