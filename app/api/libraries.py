from fastapi import APIRouter, HTTPException, Depends
from app.models.data_models import Library
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Library)
async def create_library(library: Library, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.debug(f"Received request to create library with id: {library.id}")
    try:
        vector_db.create_library(library)
        logger.debug(f"Library created successfully: {library}")
        return library
    except ValueError as e:
        logger.error(f"Error creating library: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{library_id}", response_model=Library)
async def get_library(library_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.debug(f"Received request to get library with id: {library_id}")
    try:
        library = vector_db.get_library(library_id)
        logger.debug(f"Retrieved library: {library}")
        return library
    except ValueError as e:
        logger.error(f"Error retrieving library: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{library_id}", response_model=Library)
async def update_library(library_id: str, updated_library: Library, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        existing_library = vector_db.get_library(library_id)
        
        # Update only the metadata, keeping the existing documents
        existing_library.metadata = updated_library.metadata
        
        # Use the update_library method of VectorDatabase
        updated = vector_db.update_library(existing_library)
        
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{library_id}")
async def delete_library(library_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        vector_db.delete_library(library_id)
        return {"message": f"Library {library_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
