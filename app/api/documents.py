# from fastapi import APIRouter, HTTPException, Depends
# from app.models.data_models import Document
# from app.core.database import VectorDatabase
# from app.api.dependencies import get_vector_db


# router = APIRouter()

# @router.post("/{library_id}", response_model=Document)
# async def add_document(library_id: str, document: Document, vector_db: VectorDatabase = Depends(get_vector_db)):
#     logger.debug(f"Received request to add document to library {library_id}")
#     logger.debug(f"Document: {document}")
#     try:
#         vector_db.add_document(library_id, document)
#         logger.debug("Document added successfully")
#         return document
#     except ValueError as e:
#         logger.error(f"Error adding document: {str(e)}")
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         logger.error(f"Unexpected error adding document: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
# @router.get("/{library_id}/{document_id}", response_model=Document)
# async def get_document(library_id: str, document_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
#     try:
#         return vector_db.get_document(library_id, document_id)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))

# @router.put("/{library_id}/{document_id}", response_model=Document)
# async def update_document(library_id: str, document_id: str, document: Document, vector_db: VectorDatabase = Depends(get_vector_db)):
#     try:
#         vector_db.update_document(library_id, document)
#         return document
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))

# @router.delete("/{library_id}/{document_id}")
# async def delete_document(library_id: str, document_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
#     try:
#         vector_db.delete_document(library_id, document_id)
#         return {"message": f"Document {document_id} deleted successfully from library {library_id}"}
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
    
from fastapi import APIRouter, HTTPException, Depends
from app.models.data_models import Document
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{library_id}", response_model=Document)
async def add_document(library_id: str, document: Document, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        vector_db.add_document(library_id, document)
        return document
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{library_id}/{document_id}", response_model=Document)
async def get_document(library_id: str, document_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.debug(f"Entering get_document endpoint for library {library_id}, document {document_id}")
    try:
        document = vector_db.get_document(library_id, document_id)
        logger.debug(f"Retrieved document {document_id} from library {library_id}")
        return document
    except ValueError as e:
        logger.error(f"Error in get_document endpoint: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        logger.debug(f"Exiting get_document endpoint for library {library_id}, document {document_id}")

@router.put("/{library_id}/{document_id}", response_model=Document)
async def update_document(library_id: str, document_id: str, document: Document, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.debug(f"Entering update_document endpoint for library {library_id}, document {document_id}")
    try:
        # Check if the library exists
        if not vector_db.library_exists(library_id):
            logger.error(f"Library {library_id} not found")
            raise HTTPException(status_code=404, detail=f"Library with id {library_id} does not exist")
        
        if document.id != document_id:
            logger.error(f"Document ID mismatch: URL {document_id}, payload {document.id}")
            raise HTTPException(status_code=400, detail="Document ID in URL does not match payload")
        
        updated_document = vector_db.update_document(library_id, document)
        logger.debug(f"Document {document_id} updated successfully in library {library_id}")
        return updated_document
    except ValueError as e:
        logger.error(f"Error in update_document endpoint: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        logger.debug(f"Exiting update_document endpoint for library {library_id}, document {document_id}")
        
@router.delete("/{library_id}/{document_id}")
async def delete_document(library_id: str, document_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    logger.debug(f"Entering delete_document endpoint for library {library_id}, document {document_id}")
    try:
        vector_db.delete_document(library_id, document_id)
        logger.debug(f"Document {document_id} deleted successfully from library {library_id}")
        return {"message": f"Document {document_id} deleted successfully from library {library_id}"}
    except ValueError as e:
        logger.error(f"Error in delete_document endpoint: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_document endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        logger.debug(f"Exiting delete_document endpoint for library {library_id}, document {document_id}")