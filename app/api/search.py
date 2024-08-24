from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from app.models.data_models import Chunk
from app.core.database import VectorDatabase
from app.api.dependencies import get_vector_db

router = APIRouter()

class SearchQuery(BaseModel):
    query_vector: List[float]
    k: int

class SearchResult(BaseModel):
    chunk: Chunk
    distance: float

@router.post("/{library_id}", response_model=List[SearchResult])
async def knn_search(library_id: str, search_query: SearchQuery, vector_db: VectorDatabase = Depends(get_vector_db)):
    try:
        results = vector_db.knn_search(library_id, search_query.query_vector, search_query.k)
        return [SearchResult(chunk=chunk, distance=distance) for chunk, distance in results]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))