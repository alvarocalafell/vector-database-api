import logging

logger = logging.getLogger(__name__)

# def test_index_rebuilt_on_document_operations(client, vector_db, sample_library, sample_document):
#     client.post("/libraries/", json=sample_library)
    
#     # Add document
#     client.post(f"/documents/{sample_library['id']}", json=sample_document)
#     assert vector_db.index[sample_library['id']] is not None
    
#     # Update document
#     updated_document = {**sample_document, "chunks": [{"id": "chunk-2", "text": "New chunk", "embedding": [0.5, 0.4, 0.3, 0.2, 0.1]}]}
#     client.put(f"/documents/{sample_library['id']}/{sample_document['id']}", json=updated_document)
#     assert vector_db.index[sample_library['id']] is not None
    
#     # Delete document
#     client.delete(f"/documents/{sample_library['id']}/{sample_document['id']}")
#     assert vector_db.index[sample_library['id']] is not None

def test_index_rebuilt_on_document_operations(client, vector_db, sample_library, sample_document):
    # Create the library first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"
    
    # Add document
    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"
    assert vector_db.index[sample_library['id']] is not None
    
    # Update document
    updated_document = {**sample_document, "chunks": [{"id": "chunk-2", "text": "New chunk", "embedding": [0.5, 0.4, 0.3, 0.2, 0.1]}]}
    response = client.put(f"/documents/{sample_library['id']}/{sample_document['id']}", json=updated_document)
    assert response.status_code == 200, f"Failed to update document: {response.json()}"
    assert vector_db.index[sample_library['id']] is not None
    
    # Delete document
    response = client.delete(f"/documents/{sample_library['id']}/{sample_document['id']}")
    assert response.status_code == 200, f"Failed to delete document: {response.json()}"
    assert vector_db.index[sample_library['id']] is not None

def test_knn_search_various_k(client, vector_db, sample_library, sample_document):
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    
    for k in [1, 3, 5]:
        search_query = {
            "query_vector": [0.1, 0.2, 0.3, 0.4, 0.5],
            "k": k
        }
        response = client.post(f"/search/{sample_library['id']}", json=search_query)
        assert response.status_code == 200
        assert len(response.json()) <= k
    
def test_search_results_order(client, vector_db, sample_library):
    client.post("/libraries/", json=sample_library)

    documents = [
        {"id": "doc1", "chunks": [{"id": "chunk1", "text": "Chunk 1", "embedding": [0.1, 0.1]}]},
        {"id": "doc2", "chunks": [{"id": "chunk2", "text": "Chunk 2", "embedding": [0.2, 0.2]}]},
        {"id": "doc3", "chunks": [{"id": "chunk3", "text": "Chunk 3", "embedding": [0.3, 0.3]}]}
    ]

    for doc in documents:
        response = client.post(f"/documents/{sample_library['id']}", json=doc)
        assert response.status_code == 200, f"Failed to add document: {response.json()}"

    search_query = {
        "query_vector": [0.15, 0.15],
        "k": 3
    }
    response = client.post(f"/search/{sample_library['id']}", json=search_query)
    assert response.status_code == 200
    results = response.json()
    print(f"Search results: {results}")
    
    assert len(results) > 0, "No results returned from search"

    # Check if results are sorted by distance
    distances = [result['distance'] for result in results]
    assert distances == sorted(distances), "Results are not sorted by distance"

    # Check if all returned chunks are in the expected set
    chunk_ids = [result['chunk']['id'] for result in results]
    assert set(chunk_ids).issubset({'chunk1', 'chunk2', 'chunk3'}), f"Unexpected chunks in results: {set(chunk_ids)}"

    print(f"Using indexing algorithm: {vector_db.indexing_algorithm}")

