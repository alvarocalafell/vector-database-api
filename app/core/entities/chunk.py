from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Chunk(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="The content of the chunk")
    embedding: List[float] = Field(..., description="Vector embedding of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk")