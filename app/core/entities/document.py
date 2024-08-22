from pydantic import BaseModel
from typing import List, Dict, Any
from .chunk import Chunk

class Document(BaseModel):
    id: str
    chunks: List[Chunk]
    metadata: Dict[str, Any]
