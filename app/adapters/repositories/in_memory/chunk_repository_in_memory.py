import logging
from typing import Dict, List
from app.ports.repositories.chunk_repository import ChunkRepository
from ....core.entities.chunk import Chunk
from ....core.exceptions import NotFoundError

logger = logging.getLogger(__name__)
        
class InMemoryChunkRepository(ChunkRepository):
    def __init__(self):
        self.chunks: Dict[str, Chunk] = {}

    def save(self, chunk: Chunk) -> Chunk:
        logger.info(f"Saving chunk: {chunk.id}")
        self.chunks[chunk.id] = chunk
        return chunk

    def get(self, chunk_id: str) -> Chunk:    
        logger.info(f"Fetching chunk: {chunk_id}")
        chunk = self.chunks.get(chunk_id)
        if not chunk:
            raise NotFoundError(f"Chunk with id {chunk_id} not found")
        return chunk

    def delete(self, chunk_id: str) -> None:
        logger.info(f"Deleting chunk: {chunk_id}")
        if chunk_id not in self.chunks:
            raise NotFoundError(f"Chunk with id {chunk_id} not found")
        self.chunks.pop(chunk_id, None)
        
    def list(self, document_id: str) -> List[Chunk]:
        return [chunk for chunk in self.chunks.values() if chunk.document_id == document_id]