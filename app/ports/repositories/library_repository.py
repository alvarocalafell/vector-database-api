from abc import ABC, abstractmethod
from ...core.entities.library import Library

class LibraryRepository(ABC):
    @abstractmethod
    def create(self, library: Library) -> Library:
        pass

    @abstractmethod
    def get(self, library_id: str) -> Library:
        pass

    @abstractmethod
    def update(self, library: Library) -> Library:
        pass

    @abstractmethod
    def delete(self, library_id: str):
        pass