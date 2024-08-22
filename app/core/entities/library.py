from pydantic import BaseModel
from typing import List, Dict, Any
from .document import Document

class Library(BaseModel):
    id: str
    documents: List[Document]
    metadata: Dict[str, Any]
