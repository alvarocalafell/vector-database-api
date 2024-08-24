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
