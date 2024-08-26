from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.models.data_models import Chunk
from app.core.database import VectorDatabase
from app.api.v1.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChunkCreate(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="Text content of the chunk")
    embedding: List[float] = Field(..., description="Vector embedding of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk")

class ChunkUpdate(BaseModel):
    id: str = Field(..., description="ID of the chunk")
    text: str = Field(..., description="Updated text content of the chunk")
    embedding: List[float] = Field(..., description="Updated vector embedding of the chunk")
    metadata: Dict[str, Any] = Field(..., description="Updated metadata for the chunk")
    
@router.get("/{library_id}/{document_id}", response_model=List[Chunk])
async def list_chunks(
    library_id: str,
    document_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> List[Chunk]:
    """
    List all chunks in a document.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document to list chunks from.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        List[Chunk]: A list of all chunks in the specified document.

    Raises:
        HTTPException: If the library or document is not found, or there's an error retrieving the chunks.
    """
    try:
        chunks = vector_db.list_chunks(library_id, document_id)
        logger.info(f"Retrieved {len(chunks)} chunks from document: {document_id} in library: {library_id}")
        return chunks
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to list chunks: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while listing chunks: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the chunks")


@router.post("/{library_id}/{document_id}", response_model=Chunk, status_code=201)
async def create_chunk(
    library_id: str,
    document_id: str,
    chunk: ChunkCreate = Body(
            {
        "id": "chunk-2",
        "text": "This is another test chunk",
        "embedding": [
            0.6,
            0.7,
            0.8,
            0.9,
            1.0
        ],
        "metadata": {
            "position": 2
        }
    }),
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Chunk:
    """
    Create a new chunk in a document within a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document to add the chunk to.
        chunk (ChunkCreate): The chunk data to be added.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Chunk: The created chunk object.

    Raises:
        HTTPException: If the library or document is not found, or there's an error creating the chunk.
    """
    try:
        new_chunk = Chunk(**chunk.dict())
        created_chunk = vector_db.add_chunk(library_id, document_id, new_chunk)
        logger.info(f"Chunk created successfully: {chunk.id} in document: {document_id}, library: {library_id}")
        return created_chunk
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to create chunk: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while creating chunk: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the chunk")

@router.get("/{library_id}/{document_id}/{chunk_id}", response_model=Chunk)
async def get_chunk(
    library_id: str,
    document_id: str,
    chunk_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Chunk:
    """
    Retrieve a chunk from a document within a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document containing the chunk.
        chunk_id (str): The ID of the chunk to retrieve.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Chunk: The requested chunk object.

    Raises:
        HTTPException: If the library, document, or chunk is not found.
    """
    try:
        chunk = vector_db.get_chunk(library_id, document_id, chunk_id)
        logger.info(f"Retrieved chunk: {chunk_id} from document: {document_id}, library: {library_id}")
        return chunk
    except (LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException) as e:
        logger.error(f"Failed to retrieve chunk: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while retrieving chunk: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the chunk")

@router.put("/{library_id}/{document_id}/{chunk_id}", response_model=Chunk)
async def update_chunk(
    library_id: str,
    document_id: str,
    chunk_id: str,
    chunk_update: ChunkUpdate = Body(
            {
        "id": "chunk-2",
        "text": "This is an updated test chunk",
        "embedding": [
            0.6,
            0.7,
            0.8,
            0.9,
            1.0
        ],
        "metadata": {
            "position": 2
        }
    }),
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Chunk:
    """
    Update an existing chunk in a document within a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document containing the chunk.
        chunk_id (str): The ID of the chunk to update.
        chunk_update (ChunkUpdate): The updated chunk data.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Chunk: The updated chunk object.

    Raises:
        HTTPException: If the library, document, or chunk is not found, if there's an ID mismatch, or if there's an error updating the chunk.
    """
    try:
        # First, check if the chunk exists
        existing_chunk = vector_db.get_chunk(library_id, document_id, chunk_id)
        
        # If we get here, the chunk exists, so now we can check the ID match
        if chunk_id != chunk_update.id:
            logger.error(f"Chunk ID mismatch: URL {chunk_id} != body {chunk_update.id}")
            raise HTTPException(status_code=400, detail=f"Chunk ID in URL ({chunk_id}) does not match chunk ID in body ({chunk_update.id})")

        updated_chunk = Chunk(**chunk_update.dict())
        result = vector_db.update_chunk(library_id, document_id, chunk_id, updated_chunk)
        logger.info(f"Chunk updated successfully: {chunk_id} in document: {document_id}, library: {library_id}")
        return result
    except HTTPException as e:
        # Re-raise HTTP exceptions (including our 400 for ID mismatch) without modifying them
        raise e
    except (LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException) as e:
        logger.error(f"Failed to update chunk: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid input for chunk update: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while updating chunk: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the chunk")

@router.delete("/{library_id}/{document_id}/{chunk_id}")
async def delete_chunk(
    library_id: str,
    document_id: str,
    chunk_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Dict[str, str]:
    """
    Delete a chunk from a document within a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document containing the chunk.
        chunk_id (str): The ID of the chunk to delete.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        HTTPException: If the library, document, or chunk is not found, or there's an error deleting the chunk.
    """
    try:
        vector_db.delete_chunk(library_id, document_id, chunk_id)
        logger.info(f"Chunk deleted successfully: {chunk_id} from document: {document_id}, library: {library_id}")
        return {"message": f"Chunk {chunk_id} deleted successfully"}
    except (LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException) as e:
        logger.error(f"Failed to delete chunk: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while deleting chunk: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the chunk")