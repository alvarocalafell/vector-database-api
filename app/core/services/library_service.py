import logging
from typing import List, Tuple
from ..entities.library import Library
from ..entities.document import Document
from ..entities.chunk import Chunk
from ...ports.repositories.library_repository import LibraryRepository
from ...ports.repositories.document_repository import DocumentRepository
from ...ports.repositories.chunk_repository import ChunkRepository
from .indexing_service import IndexingService
from ..exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

class LibraryService:
    def __init__(self, library_repo: LibraryRepository, document_repo: DocumentRepository, 
                 chunk_repo: ChunkRepository, indexing_service: IndexingService):
        self.library_repo = library_repo
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.indexing_service = indexing_service

    def create_library(self, library: Library) -> Library:
        logger.info(f"Creating library: {library.name}")
        return self.library_repo.create(library)

    def get_library(self, library_id: str) -> Library:
        logger.info(f"Fetching library: {library_id}")
        library = self.library_repo.get(library_id)
        if not library:
            raise NotFoundError(f"Library with id {library_id} not found")
        return library

    def update_library(self, library: Library) -> Library:
        logger.info(f"Updating library: {library.id}")
        updated_library = self.library_repo.update(library)
        if not updated_library:
            raise NotFoundError(f"Library with id {library.id} not found")
        return updated_library

    def delete_library(self, library_id: str):
        logger.info(f"Deleting library: {library_id}")
        self.library_repo.delete(library_id)

    def add_document_to_library(self, library_id: str, document: Document) -> Document:
        logger.info(f"Adding document to library: {library_id}")
        library = self.get_library(library_id)
        document = self.document_repo.create(document)
        library.documents.append(document)
        self.library_repo.update(library)
        return document

    def index_library(self, library_id: str):
        logger.info(f"Indexing library: {library_id}")
        library = self.get_library(library_id)
        chunks = [chunk for doc in library.documents for chunk in doc.chunks]
        self.indexing_service.index_chunks(chunks)

    def search_library(self, library_id: str, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        logger.info(f"Searching library: {library_id}")
        self.get_library(library_id)  # Ensure library exists
        if k <= 0:
            raise ValidationError("k must be a positive integer")
        return self.indexing_service.search(query_vector, k)