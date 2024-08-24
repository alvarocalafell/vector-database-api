def test_chunks_stored_correctly(client, vector_db, sample_library, sample_document):
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    response = client.get(f"/documents/{sample_library['id']}/{sample_document['id']}")
    assert response.status_code == 200
    assert response.json()["chunks"] == sample_document["chunks"]

def test_chunk_embeddings_handled_properly(client, vector_db, sample_library, sample_document):
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    response = client.get(f"/documents/{sample_library['id']}/{sample_document['id']}")
    assert response.status_code == 200
    assert response.json()["chunks"][0]["embedding"] == sample_document["chunks"][0]["embedding"]

def test_create_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library and document
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    
    # Create chunk
    response = client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    assert response.status_code == 200
    assert response.json() == sample_chunk

def test_get_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    
    # Get chunk
    response = client.get(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}")
    assert response.status_code == 200
    assert response.json() == sample_chunk

def test_update_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    
    # Update chunk
    updated_chunk = sample_chunk.copy()
    updated_chunk["text"] = "This is an updated test chunk"
    response = client.put(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}", json=updated_chunk)
    assert response.status_code == 200
    assert response.json() == updated_chunk

def test_delete_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    
    # Delete chunk
    response = client.delete(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}")
    assert response.status_code == 200
    
    # Verify chunk is deleted
    response = client.get(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}")
    assert response.status_code == 404

def test_create_chunk_nonexistent_document(client, vector_db, sample_library, sample_chunk):
    # Create library
    client.post("/libraries/", json=sample_library)
    
    # Attempt to create chunk in non-existent document
    response = client.post(f"/chunks/{sample_library['id']}/nonexistent-doc", json=sample_chunk)
    assert response.status_code == 404

def test_update_nonexistent_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library and document
    client.post("/libraries/", json=sample_library)
    client.post(f"/documents/{sample_library['id']}", json=sample_document)
    
    # Attempt to update non-existent chunk
    response = client.put(f"/chunks/{sample_library['id']}/{sample_document['id']}/nonexistent-chunk", json=sample_chunk)
    assert response.status_code == 404
