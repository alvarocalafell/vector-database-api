from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel, Field, constr
from app.models.data_models import Library
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException, DuplicateLibraryException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class LibraryCreate(BaseModel):
    """
    Pydantic model for library creation request.
    """
    id: constr(min_length=1, max_length=100) = Field(..., description="Unique identifier for the library") # type: ignore
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the library")

class LibraryUpdate(BaseModel):
    """
    Pydantic model for library update request.
    """
    metadata: Dict[str, Any] = Field(..., description="Updated metadata for the library")

@router.post("/", response_model=Library, status_code=201)
async def create_library(
    library: LibraryCreate,
    vector_db: VectorDatabase = Depends(get_vector_db)
) -> Library:
    """
    Create a new library in the vector database.

    Args:
        library (LibraryCreate): The library data to be created.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Library: The created library object.

    Raises:
        HTTPException: If there's an error creating the library.
    """
    try:
        new_library = Library(id=library.id, documents=[], metadata=library.metadata)
        vector_db.create_library(new_library)
        logger.info(f"Library created successfully: {new_library.id}")
        return new_library
    except DuplicateLibraryException as e:
        logger.error(f"Failed to create library: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while creating library: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the library")

@router.get("/{library_id}", response_model=Library)
async def get_library(
    library_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db)
) -> Library:
    """
    Retrieve a library from the vector database.

    Args:
        library_id (str): The ID of the library to retrieve.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Library: The requested library object.

    Raises:
        HTTPException: If the library is not found or there's an error retrieving it.
    """
    try:
        library = vector_db.get_library(library_id)
        logger.info(f"Retrieved library: {library_id}")
        return library
    except LibraryNotFoundException as e:
        logger.error(f"Failed to retrieve library: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while retrieving library: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the library")

@router.put("/{library_id}", response_model=Library)
async def update_library(
    library_id: str,
    library_update: LibraryUpdate,
    vector_db: VectorDatabase = Depends(get_vector_db)
) -> Library:
    """
    Update an existing library in the vector database.

    Args:
        library_id (str): The ID of the library to update.
        library_update (LibraryUpdate): The updated library data.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Library: The updated library object.

    Raises:
        HTTPException: If the library is not found or there's an error updating it.
    """
    try:
        existing_library = vector_db.get_library(library_id)
        existing_library.metadata = library_update.metadata
        updated = vector_db.update_library(existing_library)
        logger.info(f"Library updated successfully: {library_id}")
        return updated
    except LibraryNotFoundException as e:
        logger.error(f"Failed to update library: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while updating library: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the library")

@router.delete("/{library_id}")
async def delete_library(
    library_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db)
) -> Dict[str, str]:
    """
    Delete a library from the vector database.

    Args:
        library_id (str): The ID of the library to delete.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        HTTPException: If the library is not found or there's an error deleting it.
    """
    try:
        vector_db.delete_library(library_id)
        logger.info(f"Library deleted successfully: {library_id}")
        return {"message": f"Library {library_id} deleted successfully"}
    except LibraryNotFoundException as e:
        logger.error(f"Failed to delete library: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while deleting library: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the library")