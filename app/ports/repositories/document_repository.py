from abc import ABC, abstractmethod
from ...core.entities.document import Document

class DocumentRepository(ABC):
    @abstractmethod
    def create(self, document: Document) -> Document:
        pass

    @abstractmethod
    def get(self, document_id: str) -> Document:
        pass

    @abstractmethod
    def update(self, document: Document) -> Document:
        pass

    @abstractmethod
    def delete(self, document_id: str):
        pass