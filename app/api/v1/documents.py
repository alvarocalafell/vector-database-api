from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.models.data_models import Document, Chunk
from app.core.database import VectorDatabase
from app.api.v1.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException, DocumentNotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChunkCreate(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="Text content of the chunk")
    embedding: List[float] = Field(..., description="Vector embedding of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk")

class DocumentCreate(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    chunks: List[ChunkCreate] = Field(..., description="List of chunks in the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the document")

class DocumentUpdate(BaseModel):
    chunks: List[ChunkCreate] = Field(..., description="Updated list of chunks in the document")
    metadata: Dict[str, Any] = Field(..., description="Updated metadata for the document")
    
@router.get("/{library_id}", response_model=List[Document])
async def list_documents(
    library_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> List[Document]:
    """
    List all documents in a library.

    Args:
        library_id (str): The ID of the library to list documents from.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        List[Document]: A list of all documents in the specified library.

    Raises:
        HTTPException: If the library is not found or there's an error retrieving the documents.
    """
    try:
        documents = vector_db.list_documents(library_id)
        logger.info(f"Retrieved {len(documents)} documents from library: {library_id}")
        return documents
    except LibraryNotFoundException as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the documents")


@router.post("/{library_id}", response_model=Document, status_code=201)
async def add_document(
    library_id: str,
    document: DocumentCreate = Body(
        {
        "id": "test-document",
        "chunks": [
            {
                "id": "chunk-1",
                "text": "This is a test chunk",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "metadata": {"position": 1}
            }
        ],
        "metadata": {
            "name": "Test Document",
            "author": "Test Author"
        }
    }),
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Document:
    """
    Add a new document to a library in the vector database.

    Args:
        library_id (str): The ID of the library to add the document to.
        document (DocumentCreate): The document data to be added.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Document: The created document object.

    Raises:
        HTTPException: If the library is not found or there's an error adding the document.
    """
    try:
        new_document = Document(
            id=document.id,
            chunks=[Chunk(**chunk.dict()) for chunk in document.chunks],
            metadata=document.metadata
        )
        vector_db.add_document(library_id, new_document)
        logger.info(f"Document added successfully: {document.id} to library: {library_id}")
        return new_document
    except LibraryNotFoundException as e:
        logger.error(f"Failed to add document: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while adding document: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while adding the document")

@router.get("/{library_id}/{document_id}", response_model=Document)
async def get_document(
    library_id: str,
    document_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Document:
    """
    Retrieve a document from a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document to retrieve.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Document: The requested document object.

    Raises:
        HTTPException: If the library or document is not found.
    """
    try:
        document = vector_db.get_document(library_id, document_id)
        logger.info(f"Retrieved document: {document_id} from library: {library_id}")
        return document
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to retrieve document: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the document")

@router.put("/{library_id}/{document_id}", response_model=Document)
async def update_document(
    library_id: str,
    document_id: str,
    document_update: DocumentUpdate = Body(
            {
        "id": "test-document",
        "chunks": [
            {
                "id": "chunk-1",
                "text": "This is an updated test chunk",
                "embedding": [
                    0.1,
                    0.2,
                    0.3,
                    0.4,
                    0.5
                ],
                "metadata": {
                    "position": 1
                }
            }
        ],
        "metadata": {
            "author": "Updated Test Author"
        }
    }),
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Document:
    """
    Update an existing document in a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document to update.
        document_update (DocumentUpdate): The updated document data.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Document: The updated document object.

    Raises:
        HTTPException: If the library or document is not found, or there's an error updating the document.
    """
    try:
        existing_document = vector_db.get_document(library_id, document_id)
        updated_document = Document(
            id=document_id,
            chunks=[Chunk(**chunk.dict()) for chunk in document_update.chunks],
            metadata=document_update.metadata
        )
        updated = vector_db.update_document(library_id, updated_document)
        logger.info(f"Document updated successfully: {document_id} in library: {library_id}")
        return updated
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to update document: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while updating document: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the document")

@router.delete("/{library_id}/{document_id}")
async def delete_document(
    library_id: str,
    document_id: str,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> Dict[str, str]:
    """
    Delete a document from a library in the vector database.

    Args:
        library_id (str): The ID of the library containing the document.
        document_id (str): The ID of the document to delete.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        HTTPException: If the library or document is not found, or there's an error deleting the document.
    """
    try:
        vector_db.delete_document(library_id, document_id)
        logger.info(f"Document deleted successfully: {document_id} from library: {library_id}")
        return {"message": f"Document {document_id} deleted successfully from library {library_id}"}
    except (LibraryNotFoundException, DocumentNotFoundException) as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the document")