from abc import ABC, abstractmethod
from ...core.entities.chunk import Chunk

class ChunkRepository(ABC):
    @abstractmethod
    def create(self, chunk: Chunk) -> Chunk:
        pass

    @abstractmethod
    def get(self, chunk_id: str) -> Chunk:
        pass

    @abstractmethod
    def update(self, chunk: Chunk) -> Chunk:
        pass

    @abstractmethod
    def delete(self, chunk_id: str):
        pass