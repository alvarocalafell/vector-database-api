from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.core.entities.library import Library
from app.core.services.library_service import LibraryService
from app.di_container import Container
from app.core.exceptions import VectorDBException
from typing import List, Tuple
from app.core.entities.chunk import Chunk

router = APIRouter()

@router.post("/libraries", response_model=Library)
@inject
async def create_library(
    library: Library,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        return library_service.create_library(library)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.get("/libraries/{library_id}", response_model=Library)
@inject
async def get_library(
    library_id: str,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        return library_service.get_library(library_id)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.put("/libraries/{library_id}", response_model=Library)
@inject
async def update_library(
    library_id: str,
    library: Library,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        library.id = library_id
        return library_service.update_library(library)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.delete("/libraries/{library_id}", status_code=204)
@inject
async def delete_library(
    library_id: str,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        library_service.delete_library(library_id)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.post("/libraries/{library_id}/index", status_code=204)
@inject
async def index_library(
    library_id: str,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        library_service.index_library(library_id)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.post("/libraries/{library_id}/search", response_model=List[Tuple[Chunk, float]])
@inject
async def search_library(
    library_id: str,
    query_vector: List[float],
    k: int,
    library_service: LibraryService = Depends(Provide[Container.library_service])
):
    try:
        return library_service.search_library(library_id, query_vector, k)
    except VectorDBException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))