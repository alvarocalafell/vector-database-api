from fastapi import APIRouter, Depends, HTTPException
from app.models.data_models import Chunk
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{library_id}/{document_id}", response_model=Chunk)
async def create_chunk(library_id: str, document_id: str, chunk: Chunk, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        created_chunk = vector_db.add_chunk(library_id, document_id, chunk)
        return created_chunk
    except LibraryNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{library_id}/{document_id}/{chunk_id}", response_model=Chunk)
async def get_chunk(library_id: str, document_id: str, chunk_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        chunk = vector_db.get_chunk(library_id, document_id, chunk_id)
        return chunk
    except (LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/{library_id}/{document_id}/{chunk_id}", response_model=Chunk)
async def update_chunk(library_id: str, document_id: str, chunk_id: str, chunk: Chunk, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Attempting to update chunk: library_id={library_id}, document_id={document_id}, chunk_id={chunk_id}")
    try:
        # First, check if the chunk exists
        vector_db.get_chunk(library_id, document_id, chunk_id)
        
        # If we get here, the chunk exists, so now we can check the ID match
        if chunk.id != chunk_id:
            logger.warning(f"Chunk ID mismatch: path={chunk_id}, body={chunk.id}")
            raise HTTPException(status_code=400, detail=f"Chunk ID in path ({chunk_id}) does not match chunk ID in body ({chunk.id})")
        
        updated_chunk = vector_db.update_chunk(library_id, document_id, chunk_id, chunk)
        logger.info(f"Successfully updated chunk: {chunk_id}")
        return updated_chunk
    except LibraryNotFoundException as e:
        logger.error(f"Library not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DocumentNotFoundException as e:
        logger.error(f"Document not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ChunkNotFoundException as e:
        logger.error(f"Chunk not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as e:
        logger.error(f"HTTP exception: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error occurred while updating chunk: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



@router.delete("/{library_id}/{document_id}/{chunk_id}")
async def delete_chunk(library_id: str, document_id: str, chunk_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        vector_db.delete_chunk(library_id, document_id, chunk_id)
        return {"message": f"Chunk {chunk_id} deleted successfully"}
    except (LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))