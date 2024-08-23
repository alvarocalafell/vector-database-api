from pydantic import BaseModel, Field
from typing import List
from .document import Document

class Library(BaseModel):
    id: str = Field(..., description="Unique identifier for the library")
    name: str = Field(..., description="Name of the library")
    documents: List["Document"] = Field(default_factory=list, description="List of documents in the library")