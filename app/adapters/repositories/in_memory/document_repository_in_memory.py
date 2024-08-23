from typing import Dict, List
from ....ports.repositories.document_repository import DocumentRepository
from ....core.entities.document import Document
        
class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self):
        self.documents: Dict[str, Document] = {}

    def save(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    def get(self, document_id: str) -> Document:
        return self.documents.get(document_id)

    def delete(self, document_id: str) -> None:
        self.documents.pop(document_id, None)

    def list(self, library_id: str) -> List[Document]:
        return [doc for doc in self.documents.values() if doc.library_id == library_id]