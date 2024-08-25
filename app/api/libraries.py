from fastapi import APIRouter, Depends, HTTPException
from app.models.data_models import Library
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException, DuplicateLibraryException, VectorDatabaseException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=Library)
async def create_library(library: Library, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to create library with id: {library.id}")
    try:
        vector_db.create_library(library)
        logger.info(f"Library created successfully: {library.id}")
        return library
    except DuplicateLibraryException as e:
        logger.error(f"Failed to create library: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while creating library: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while creating the library")

@router.get("/{library_id}", response_model=Library)
async def get_library(library_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to get library with id: {library_id}")
    try:
        library = vector_db.get_library(library_id)
        logger.info(f"Retrieved library: {library_id}")
        return library
    except LibraryNotFoundException as e:
        logger.error(f"Failed to retrieve library: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving library: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while retrieving the library")

@router.put("/{library_id}", response_model=Library)
async def update_library(library_id: str, updated_library: Library, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to update library with id: {library_id}")
    try:
        if updated_library.id != library_id:
            logger.error(f"Library ID mismatch: path {library_id}, body {updated_library.id}")
            raise HTTPException(status_code=400, detail="Library ID in path does not match library ID in body")
        
        existing_library = vector_db.get_library(library_id)
        
        # Update only the metadata, keeping the existing documents
        existing_library.metadata = updated_library.metadata
        
        updated = vector_db.update_library(existing_library)
        logger.info(f"Library updated successfully: {library_id}")
        return updated
    except LibraryNotFoundException as e:
        logger.error(f"Failed to update library: {str(e)}")
        raise e
    except HTTPException as e:
        logger.error(f"Bad request while updating library: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while updating library: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while updating the library")

@router.delete("/{library_id}")
async def delete_library(library_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to delete library with id: {library_id}")
    try:
        vector_db.delete_library(library_id)
        logger.info(f"Library deleted successfully: {library_id}")
        return {"message": f"Library {library_id} deleted successfully"}
    except LibraryNotFoundException as e:
        logger.error(f"Failed to delete library: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while deleting library: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while deleting the library")