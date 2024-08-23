import uuid
import logging
from typing import List
from app.core.entities import Document, Chunk
from app.core.exceptions import NotFoundError, ValidationError
from app.adapters.repositories.in_memory.document_repository_in_memory import InMemoryDocumentRepository

logger = logging.getLogger(__name__)

class DocumentService():
    def __init__(self, repository: InMemoryDocumentRepository):
        self.repository = repository

    def create_document(self, library_id: str) -> Document:
        """
        Create a new document in the specified library.

        Args:
            library_id (str): The ID of the library to create the document in.

        Returns:
            Document: The created document.

        Raises:
            ValidationError: If the library_id is invalid.
        """
        if not library_id or not library_id.strip():
            raise ValidationError("Invalid library ID")

        document_id = str(uuid.uuid4())
        document = Document(id=document_id, library_id=library_id, chunks=[])
        logger.info(f"Creating new document in library {library_id}: {document}")
        return self.repository.save(document)

    def get_document(self, document_id: str) -> Document:
        """
        Retrieve a document by its ID.

        Args:
            document_id (str): The ID of the document to retrieve.

        Returns:
            Document: The retrieved document.

        Raises:
            NotFoundError: If the document is not found.
        """
        document = self.repository.get(document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            raise NotFoundError(f"Document with id {document_id} not found")
        return document

    def update_document(self, document: Document) -> Document:
        """
        Update an existing document.

        Args:
            document (Document): The document with updated information.

        Returns:
            Document: The updated document.

        Raises:
            NotFoundError: If the document is not found.
            ValidationError: If the document data is invalid.
        """
        if not document.id or not document.library_id:
            raise ValidationError("Invalid document data")

        existing_document = self.get_document(document.id)
        existing_document.library_id = document.library_id
        existing_document.chunks = document.chunks
        logger.info(f"Updating document: {existing_document}")
        return self.repository.save(existing_document)

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document by its ID.

        Args:
            document_id (str): The ID of the document to delete.

        Raises:
            NotFoundError: If the document is not found.
        """
        self.get_document(document_id)  # Ensure document exists
        logger.info(f"Deleting document: {document_id}")
        self.repository.delete(document_id)

    def list_documents(self, library_id: str) -> List[Document]:
        """
        List all documents in a specific library.

        Args:
            library_id (str): The ID of the library to list documents from.

        Returns:
            List[Document]: A list of all documents in the specified library.
        """
        return self.repository.list(library_id)

    def add_chunk_to_document(self, document_id: str, chunk: Chunk) -> Document:
        """
        Add a chunk to a document.

        Args:
            document_id (str): The ID of the document to add the chunk to.
            chunk (Chunk): The chunk to add.

        Returns:
            Document: The updated document.

        Raises:
            NotFoundError: If the document is not found.
            ValidationError: If the chunk is invalid.
        """
        if not chunk.id or not chunk.text:
            raise ValidationError("Invalid chunk data")

        document = self.get_document(document_id)
        document.chunks.append(chunk)
        logger.info(f"Adding chunk {chunk.id} to document {document_id}")
        return self.repository.save(document)

    def remove_chunk_from_document(self, document_id: str, chunk_id: str) -> Document:
        """
        Remove a chunk from a document.

        Args:
            document_id (str): The ID of the document to remove the chunk from.
            chunk_id (str): The ID of the chunk to remove.

        Returns:
            Document: The updated document.

        Raises:
            NotFoundError: If the document or chunk is not found.
        """
        document = self.get_document(document_id)
        document.chunks = [chunk for chunk in document.chunks if chunk.id != chunk_id]
        logger.info(f"Removing chunk {chunk_id} from document {document_id}")
        return self.repository.save(document)