from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Chunk(BaseModel):
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Document(BaseModel):
    id: str
    chunks: List[Chunk]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Library(BaseModel):
    id: str
    documents: List[Document]
    metadata: Dict[str, Any] = Field(default_factory=dict)
