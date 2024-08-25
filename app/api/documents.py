from fastapi import APIRouter, Depends, HTTPException
from app.models.data_models import Document
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException, DocumentNotFoundException, VectorDatabaseException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{library_id}", response_model=Document)
async def add_document(library_id: str, document: Document, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to add document to library: {library_id}")
    try:
        vector_db.add_document(library_id, document)
        logger.info(f"Document {document.id} added successfully to library: {library_id}")
        return document
    except LibraryNotFoundException as e:
        logger.error(f"Failed to add document: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while adding document: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while adding the document")

@router.get("/{library_id}/{document_id}", response_model=Document)
async def get_document(library_id: str, document_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to get document: {document_id} from library: {library_id}")
    try:
        document = vector_db.get_document(library_id, document_id)
        logger.info(f"Retrieved document: {document_id} from library: {library_id}")
        return document
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to retrieve document: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving document: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while retrieving the document")

@router.put("/{library_id}/{document_id}", response_model=Document)
async def update_document(library_id: str, document_id: str, document: Document, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to update document: {document_id} in library: {library_id}")
    try:
        if document.id != document_id:
            raise HTTPException(status_code=400, detail="Document ID in URL does not match payload")
        updated_document = vector_db.update_document(library_id, document)
        logger.info(f"Document {document_id} updated successfully in library: {library_id}")
        return updated_document
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to update document: {str(e)}")
        raise e
    except HTTPException as e:
        logger.error(f"Bad request while updating document: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while updating document: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while updating the document")

@router.delete("/{library_id}/{document_id}")
async def delete_document(library_id: str, document_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.info(f"Received request to delete document: {document_id} from library: {library_id}")
    try:
        vector_db.delete_document(library_id, document_id)
        logger.info(f"Document {document_id} deleted successfully from library: {library_id}")
        return {"message": f"Document {document_id} deleted successfully from library {library_id}"}
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while deleting document: {str(e)}")
        raise VectorDatabaseException(status_code=500, detail="An unexpected error occurred while deleting the document")