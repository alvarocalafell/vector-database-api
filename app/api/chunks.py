from fastapi import APIRouter, HTTPException, Depends
from app.models.data_models import Chunk
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db

router = APIRouter()

@router.post("/{library_id}/{document_id}", response_model=Chunk)
async def create_chunk(library_id: str, document_id: str, chunk: Chunk, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        return vector_db.add_chunk(library_id, document_id, chunk)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{library_id}/{document_id}/{chunk_id}", response_model=Chunk)
async def get_chunk(library_id: str, document_id: str, chunk_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        return vector_db.get_chunk(library_id, document_id, chunk_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{library_id}/{document_id}/{chunk_id}", response_model=Chunk)
async def update_chunk(library_id: str, document_id: str, chunk_id: str, chunk: Chunk, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        return vector_db.update_chunk(library_id, document_id, chunk_id, chunk)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{library_id}/{document_id}/{chunk_id}")
async def delete_chunk(library_id: str, document_id: str, chunk_id: str, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        vector_db.delete_chunk(library_id, document_id, chunk_id)
        return {"message": f"Chunk {chunk_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))