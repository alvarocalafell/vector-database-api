from pydantic import BaseModel, Field
from typing import List, Optional

class Chunk(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="The content of the chunk")
    embedding: Optional[List[float]] = Field(..., description="Vector embedding of the chunk")
