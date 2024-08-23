# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import AsyncMock
# from app.main import app
# from app.di_container import Container
# from app.core.services.library_service import LibraryService
# from app.core.entities.chunk import Chunk
# from app.core.entities.document import Document
# from app.core.exceptions import NotFoundError
# from app.utils.embeddings import get_embedding

# @pytest.fixture
# def client(load_env):
#     container = Container()
#     container.config.indexing_algorithm.from_value("kd_tree")
#     container.wire(modules=["app.adapters.api.v1.routes.chunk_routes"])
#     app.container = container
#     return TestClient(app)

# @pytest.fixture
# async def library_service():
#     library_repo = AsyncMock()
#     document_repo = AsyncMock()
#     chunk_repo = AsyncMock()
#     indexing_service = AsyncMock()
#     return LibraryService(library_repo, document_repo, chunk_repo, indexing_service)

# # Service layer tests
# @pytest.mark.asyncio
# async def test_add_chunk_to_document(library_service):
#     document = Document(id="1", chunks=[])
#     chunk_text = "Test chunk"
#     chunk_embedding = get_embedding(chunk_text)
#     chunk = Chunk(id="1", text=chunk_text, embedding=chunk_embedding)
#     library_service.document_repo.get.return_value = document
#     library_service.chunk_repo.create.return_value = chunk
    
#     result = await library_service.add_chunk_to_document("lib1", "1", chunk)
    
#     assert result == chunk
#     assert chunk in document.chunks
#     library_service.document_repo.update.assert_called_once_with(document)

# @pytest.mark.asyncio
# async def test_get_chunk(library_service):
#     chunk_text = "Test chunk"
#     chunk_embedding = get_embedding(chunk_text)
#     chunk = Chunk(id="1", text=chunk_text, embedding=chunk_embedding)
#     library_service.chunk_repo.get.return_value = chunk
    
#     result = await library_service.get_chunk("lib1", "doc1", "1")
    
#     assert result == chunk
#     library_service.chunk_repo.get.assert_called_once_with("1")

# @pytest.mark.asyncio
# async def test_update_chunk(library_service):
#     chunk_text = "Updated test chunk"
#     chunk_embedding = get_embedding(chunk_text)
#     chunk = Chunk(id="1", text=chunk_text, embedding=chunk_embedding)
#     library_service.chunk_repo.get.return_value = chunk
#     library_service.chunk_repo.update.return_value = chunk
    
#     result = await library_service.update_chunk("lib1", "doc1", "1", chunk)
    
#     assert result == chunk
#     library_service.chunk_repo.update.assert_called_once_with(chunk)

# @pytest.mark.asyncio
# async def test_delete_chunk(library_service):
#     await library_service.delete_chunk("lib1", "doc1", "1")
    
#     library_service.chunk_repo.delete.assert_called_once_with("1")

# # API layer tests
# def test_create_chunk(client):
#     # First, create a library and a document
#     client.post("/api/v1/libraries", json={"id": "test_lib", "name": "Test Library"})
#     client.post("/api/v1/libraries/test_lib/documents", json={"id": "test_doc", "chunks": []})

#     # Now, create a chunk
#     chunk_text = "This is a test chunk"
#     chunk_embedding = get_embedding(chunk_text)
#     chunk_data = {
#         "id": "test_chunk",
#         "text": chunk_text,
#         "embedding": chunk_embedding
#     }
#     response = client.post("/api/v1/libraries/test_lib/documents/test_doc/chunks", json=chunk_data)
#     assert response.status_code == 200
#     assert response.json()["id"] == "test_chunk"
#     assert response.json()["text"] == "This is a test chunk"
#     assert "embedding" in response.json()

# def test_get_chunk_api(client):
#     response = client.get("/api/v1/libraries/test_lib/documents/test_doc/chunks/test_chunk")
#     assert response.status_code == 200
#     assert response.json()["id"] == "test_chunk"
#     assert response.json()["text"] == "This is a test chunk"
#     assert "embedding" in response.json()

# def test_update_chunk_api(client):
#     updated_chunk_text = "This is an updated test chunk"
#     updated_chunk_embedding = get_embedding(updated_chunk_text)
#     updated_chunk_data = {
#         "id": "test_chunk",
#         "text": updated_chunk_text,
#         "embedding": updated_chunk_embedding
#     }
#     response = client.put("/api/v1/libraries/test_lib/documents/test_doc/chunks/test_chunk", json=updated_chunk_data)
#     assert response.status_code == 200
#     assert response.json()["text"] == "This is an updated test chunk"
#     assert "embedding" in response.json()

# def test_delete_chunk_api(client):
#     response = client.delete("/api/v1/libraries/test_lib/documents/test_doc/chunks/test_chunk")
#     assert response.status_code == 204

#     # Verify that the chunk is deleted
#     get_response = client.get("/api/v1/libraries/test_lib/documents/test_doc/chunks/test_chunk")
#     assert get_response.status_code == 404