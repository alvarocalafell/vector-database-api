def test_create_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library and document first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"

    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"
    
    response = client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    assert response.status_code == 200, f"Failed to create chunk: {response.json()}"
    assert response.json() == sample_chunk

def test_get_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"

    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"

    response = client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    assert response.status_code == 200, f"Failed to create chunk: {response.json()}"
    
    response = client.get(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}")
    assert response.status_code == 200, f"Failed to get chunk: {response.json()}"
    assert response.json() == sample_chunk

def test_update_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"

    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"

    response = client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    assert response.status_code == 200, f"Failed to create chunk: {response.json()}"
    
    updated_chunk = sample_chunk.copy()
    updated_chunk['text'] = "Updated chunk text"
    response = client.put(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}", json=updated_chunk)
    assert response.status_code == 200, f"Failed to update chunk: {response.json()}"
    assert response.json()['text'] == "Updated chunk text"

def test_delete_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"

    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"

    response = client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    assert response.status_code == 200, f"Failed to create chunk: {response.json()}"
    
    response = client.delete(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}")
    assert response.status_code == 200, f"Failed to delete chunk: {response.json()}"
    assert response.json()['message'] == f"Chunk {sample_chunk['id']} deleted successfully"

def test_create_chunk_nonexistent_document(client, vector_db, sample_library, sample_chunk):
    # Create library but not document
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"
    
    response = client.post(f"/chunks/{sample_library['id']}/nonexistent-doc", json=sample_chunk)
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}"

def test_update_chunk_mismatched_id(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library, document, and chunk first
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"

    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"

    response = client.post(f"/chunks/{sample_library['id']}/{sample_document['id']}", json=sample_chunk)
    assert response.status_code == 200, f"Failed to create chunk: {response.json()}"
 
    mismatched_chunk = sample_chunk.copy()
    mismatched_chunk['id'] = 'mismatched-id'
    response = client.put(f"/chunks/{sample_library['id']}/{sample_document['id']}/{sample_chunk['id']}", json=mismatched_chunk)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    print(f"Response headers: {response.headers}")
    assert response.status_code == 400, f"Expected 400, got: {response.status_code}"
    assert "chunk id" in response.json()['detail'].lower(), f"Unexpected error message: {response.json()['detail']}"



def test_update_nonexistent_chunk(client, vector_db, sample_library, sample_document, sample_chunk):
    # Create library and document but not chunk
    response = client.post("/libraries/", json=sample_library)
    assert response.status_code == 200, f"Failed to create library: {response.json()}"

    response = client.post(f"/documents/{sample_library['id']}", json=sample_document)
    assert response.status_code == 200, f"Failed to add document: {response.json()}"
    
    response = client.put(f"/chunks/{sample_library['id']}/{sample_document['id']}/nonexistent-chunk", json=sample_chunk)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    print(f"Response headers: {response.headers}")
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
    assert "not found" in response.json()['detail'].lower(), f"Unexpected error message: {response.json()['detail']}"