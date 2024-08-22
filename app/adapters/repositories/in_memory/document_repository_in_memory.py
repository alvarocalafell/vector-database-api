from typing import Dict
from ....ports.repositories.document_repository import DocumentRepository
from ....core.entities.document import Document

class DocumentRepositoryInMemory(DocumentRepository):
    def __init__(self):
        self.documents: Dict[str, Document] = {}

    def create(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    def get(self, document_id: str) -> Document:
        return self.documents.get(document_id)

    def update(self, document: Document) -> Document:
        if document.id in self.documents:
            self.documents[document.id] = document
            return document
        return None

    def delete(self, document_id: str):
        self.documents.pop(document_id, None)