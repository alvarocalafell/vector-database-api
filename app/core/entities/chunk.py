from pydantic import BaseModel
from typing import Dict, Any

class Chunk(BaseModel):
    id: str
    text: str
    embedding: list[float]
    metadata: Dict[str, Any]
