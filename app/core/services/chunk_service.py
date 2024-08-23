import uuid
import logging
from typing import List
from app.core.entities import Chunk
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.embeddings import get_embedding  # You'll need to implement this
from app.adapters.repositories.in_memory.chunk_repository_in_memory import InMemoryChunkRepository


logger = logging.getLogger(__name__)

class ChunkService():
    def __init__(self, repository: InMemoryChunkRepository):
        self.repository = repository

    def create_chunk(self, document_id: str, text: str) -> Chunk:
        """
        Create a new chunk in the specified document and generate its embedding.

        Args:
            document_id (str): The ID of the document to create the chunk in.
            text (str): The text content of the chunk.

        Returns:
            Chunk: The created chunk with generated embedding.

        Raises:
            ValidationError: If the document_id is invalid or text is empty.
            EmbeddingError: If there's an error generating the embedding.
        """
        if not document_id or not document_id.strip():
            raise ValidationError("Invalid document ID")
        if not text or not text.strip():
            raise ValidationError("Chunk text cannot be empty")

        chunk_id = str(uuid.uuid4())
        chunk = Chunk(id=chunk_id, document_id=document_id, text=text, embedding=None)
        
        try:
            chunk.embedding = get_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding for chunk {chunk_id}: {str(e)}")
            #raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

        logger.info(f"Creating new chunk in document {document_id}: {chunk}")
        return self.repository.save(chunk)

    def get_chunk(self, chunk_id: str) -> Chunk:
        """
        Retrieve a chunk by its ID.

        Args:
            chunk_id (str): The ID of the chunk to retrieve.

        Returns:
            Chunk: The retrieved chunk.

        Raises:
            NotFoundError: If the chunk is not found.
        """
        chunk = self.repository.get(chunk_id)
        if not chunk:
            logger.error(f"Chunk not found: {chunk_id}")
            raise NotFoundError(f"Chunk with id {chunk_id} not found")
        return chunk

    def update_chunk(self, chunk: Chunk) -> Chunk:
        """
        Update an existing chunk and regenerate its embedding if the text has changed.

        Args:
            chunk (Chunk): The chunk with updated information.

        Returns:
            Chunk: The updated chunk.

        Raises:
            NotFoundError: If the chunk is not found.
            ValidationError: If the chunk data is invalid.
            EmbeddingError: If there's an error generating the new embedding.
        """
        if not chunk.id or not chunk.document_id or not chunk.text:
            raise ValidationError("Invalid chunk data")

        existing_chunk = self.get_chunk(chunk.id)
        
        if existing_chunk.text != chunk.text:
            try:
                chunk.embedding = get_embedding(chunk.text)
            except Exception as e:
                logger.error(f"Error regenerating embedding for chunk {chunk.id}: {str(e)}")
                #raise EmbeddingError(f"Failed to regenerate embedding: {str(e)}")

        logger.info(f"Updating chunk: {chunk}")
        return self.repository.save(chunk)

    def delete_chunk(self, chunk_id: str) -> None:
        """
        Delete a chunk by its ID.

        Args:
            chunk_id (str): The ID of the chunk to delete.

        Raises:
            NotFoundError: If the chunk is not found.
        """
        self.get_chunk(chunk_id)  # Ensure chunk exists
        logger.info(f"Deleting chunk: {chunk_id}")
        self.repository.delete(chunk_id)

    def list_chunks(self, document_id: str) -> List[Chunk]:
        """
        List all chunks in a specific document.

        Args:
            document_id (str): The ID of the document to list chunks from.

        Returns:
            List[Chunk]: A list of all chunks in the specified document.
        """
        return self.repository.list(document_id)

    def generate_embedding(self, chunk: Chunk) -> Chunk:
        """
        Generate or regenerate the embedding for a chunk.

        Args:
            chunk (Chunk): The chunk to generate the embedding for.

        Returns:
            Chunk: The chunk with the updated embedding.

        Raises:
            ValidationError: If the chunk data is invalid.
            EmbeddingError: If there's an error generating the embedding.
        """
        if not chunk.id or not chunk.text:
            raise ValidationError("Invalid chunk data")

        try:
            chunk.embedding = get_embedding(chunk.text)
            logger.info(f"Generated embedding for chunk: {chunk.id}")
        except Exception as e:
            logger.error(f"Error generating embedding for chunk {chunk.id}: {str(e)}")
            #raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

        return self.repository.save(chunk)