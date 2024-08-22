import logging
from typing import Dict
from ....ports.repositories.chunk_repository import ChunkRepository
from ....core.entities.chunk import Chunk
from ....core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

class ChunkRepositoryInMemory(ChunkRepository):
    def __init__(self):
        self.chunks: Dict[str, Chunk] = {}

    def create(self, chunk: Chunk) -> Chunk:
        logger.info(f"Creating chunk: {chunk.id}")
        self.chunks[chunk.id] = chunk
        return chunk

    def get(self, chunk_id: str) -> Chunk:
        logger.info(f"Fetching chunk: {chunk_id}")
        chunk = self.chunks.get(chunk_id)
        if not chunk:
            raise NotFoundError(f"Chunk with id {chunk_id} not found")
        return chunk

    def update(self, chunk: Chunk) -> Chunk:
        logger.info(f"Updating chunk: {chunk.id}")
        if chunk.id not in self.chunks:
            raise NotFoundError(f"Chunk with id {chunk.id} not found")
        self.chunks[chunk.id] = chunk
        return chunk

    def delete(self, chunk_id: str):
        logger.info(f"Deleting chunk: {chunk_id}")
        if chunk_id not in self.chunks:
            raise NotFoundError(f"Chunk with id {chunk_id} not found")
        del self.chunks[chunk_id]