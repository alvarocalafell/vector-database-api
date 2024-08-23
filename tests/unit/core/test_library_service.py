import pytest
from unittest.mock import Mock
from app.core.services.library_service import LibraryService
from app.core.entities.library import Library
from app.core.entities.document import Document
from app.core.entities.chunk import Chunk
from app.core.exceptions import NotFoundError
from app.utils.embeddings import get_embedding

@pytest.fixture
def library_service():
    library_repo = Mock()
    document_repo = Mock()
    chunk_repo = Mock()
    indexing_service = Mock()
    return LibraryService(library_repo, document_repo, chunk_repo, indexing_service)

def test_create_library(library_service):
    library = Library(id="1", name="Test Library")
    library_service.library_repo.create.return_value = library
    
    result = library_service.create_library(library)
    
    assert result == library
    library_service.library_repo.create.assert_called_once_with(library)

def test_get_library(library_service):
    library = Library(id="1", name="Test Library")
    library_service.library_repo.get.return_value = library
    
    result = library_service.get_library("1")
    
    assert result == library
    library_service.library_repo.get.assert_called_once_with("1")

def test_get_library_not_found(library_service):
    library_service.library_repo.get.return_value = None
    
    with pytest.raises(NotFoundError):
        library_service.get_library("1")
def test_search_library(library_service):
    library = Library(id="1", name="Test Library")
    chunk_text = "This is a test chunk"
    chunk_embedding = get_embedding(chunk_text)
    chunk = Chunk(id="1", text=chunk_text, embedding=chunk_embedding)
    library_service.library_repo.get.return_value = library
    library_service.indexing_service.search.return_value = [(chunk, 0.9)]
    
    query_text = "Test query"
    query_embedding = get_embedding(query_text)
    
    result = library_service.search_library("1", query_embedding, 1)
    
    assert result == [(chunk, 0.9)]
    library_service.indexing_service.search.assert_called_once_with(query_embedding, 1)

def test_add_document_to_library_with_chunks(library_service):
    library = Library(id="1", name="Test Library")
    chunk_texts = ["This is chunk 1", "This is chunk 2"]
    chunks = [
        Chunk(id=f"chunk_{i}", text=text, embedding=get_embedding(text))
        for i, text in enumerate(chunk_texts)
    ]
    document = Document(id="1", chunks=chunks)
    library_service.library_repo.get.return_value = library
    library_service.document_repo.create.return_value = document
    
    result = library_service.add_document_to_library("1", document)
    
    assert result == document
    assert document in library.documents
    library_service.library_repo.update.assert_called_once_with(library)
    for chunk in chunks:
        assert isinstance(chunk.embedding, list)
        assert len(chunk.embedding) > 0