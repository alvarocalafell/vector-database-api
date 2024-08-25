from pydantic import BaseModel, Field, conlist
from typing import List, Dict, Any
import uuid

class Chunk(BaseModel):
    """
    Represents a chunk of text with its embedding and metadata.

    Attributes:
        id (str): Unique identifier for the chunk.
        text (str): The text content of the chunk.
        embedding (List[float]): The vector embedding of the chunk.
        metadata (Dict[str, Any]): Additional metadata associated with the chunk.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the chunk")
    text: str = Field(..., description="The text content of the chunk")
    embedding: conlist(float, min_length=1) = Field(..., description="The vector embedding of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk")

    class Config:
        schema_extra = {
            "example": {
                "id": "chunk-1",
                "text": "This is a sample chunk of text.",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "metadata": {"position": 1, "source": "document1"}
            }
        }

class Document(BaseModel):
    """
    Represents a document containing multiple chunks and metadata.

    Attributes:
        id (str): Unique identifier for the document.
        chunks (List[Chunk]): List of chunks that make up the document.
        metadata (Dict[str, Any]): Additional metadata associated with the document.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the document")
    chunks: List[Chunk] = Field(default_factory=list, description="List of chunks in the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the document")

    class Config:
        schema_extra = {
            "example": {
                "id": "doc-1",
                "chunks": [
                    {
                        "id": "chunk-1",
                        "text": "First chunk of the document.",
                        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                        "metadata": {"position": 1}
                    },
                    {
                        "id": "chunk-2",
                        "text": "Second chunk of the document.",
                        "embedding": [0.6, 0.7, 0.8, 0.9, 1.0],
                        "metadata": {"position": 2}
                    }
                ],
                "metadata": {"author": "John Doe", "date": "2024-08-25"}
            }
        }

class Library(BaseModel):
    """
    Represents a library containing multiple documents and metadata.

    Attributes:
        id (str): Unique identifier for the library.
        documents (List[Document]): List of documents in the library.
        metadata (Dict[str, Any]): Additional metadata associated with the library.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the library")
    documents: List[Document] = Field(default_factory=list, description="List of documents in the library")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the library")

    class Config:
        schema_extra = {
            "example": {
                "id": "lib-1",
                "documents": [
                    {
                        "id": "doc-1",
                        "chunks": [
                            {
                                "id": "chunk-1",
                                "text": "Sample text in document 1.",
                                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                                "metadata": {"position": 1}
                            }
                        ],
                        "metadata": {"author": "Jane Doe"}
                    }
                ],
                "metadata": {"name": "Sample Library", "created_at": "2024-08-25"}
            }
        }

class SearchQuery(BaseModel):
    """
    Represents a search query for the vector database.

    Attributes:
        query_vector (List[float]): The query vector to search for.
        k (int): The number of nearest neighbors to return.
    """
    query_vector: conlist(float, min_length=1) = Field(..., description="The query vector to search for")
    k: int = Field(..., gt=0, description="The number of nearest neighbors to return")

    class Config:
        schema_extra = {
            "example": {
                "query_vector": [0.1, 0.2, 0.3, 0.4, 0.5],
                "k": 5
            }
        }

class SearchResult(BaseModel):
    """
    Represents a search result from the vector database.

    Attributes:
        chunk (Chunk): The chunk that matches the search query.
        distance (float): The distance between the query vector and the chunk's embedding.
    """
    chunk: Chunk
    distance: float

    class Config:
        schema_extra = {
            "example": {
                "chunk": {
                    "id": "chunk-1",
                    "text": "This is a matching chunk.",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "metadata": {"position": 1}
                },
                "distance": 0.15
            }
        }