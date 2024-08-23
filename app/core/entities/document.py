from pydantic import BaseModel, Field
from typing import List
from .chunk import Chunk

class Document(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    chunks: List["Chunk"] = Field(default_factory=list, description="List of chunks that make up the document")