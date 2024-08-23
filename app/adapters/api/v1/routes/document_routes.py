from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.core.entities.document import Document
from app.core.services.library_service import LibraryService
from app.di_container import Container
from app.core.exceptions import VectorDBException

router = APIRouter()

@router.post("/libraries/{library_id}/documents", response_model=Document)
@inject
async def add_document_to_library(
    library_id: str,
    document: Document,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        return library_service.add_document_to_library(library_id, document)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))