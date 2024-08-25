from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.data_models import SearchQuery, SearchResult
from app.core.database import VectorDatabase
from app.api.v1.dependencies import get_vector_db
from app.core.exceptions import LibraryNotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{library_id}", response_model=List[SearchResult])
async def knn_search(
    library_id: str,
    search_query: SearchQuery,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> List[SearchResult]:
    """
    Perform a k-nearest neighbor search in the specified library.

    This endpoint searches for the k nearest neighbors to the provided query vector
    within the specified library.

    Args:
        library_id (str): The ID of the library to search in.
        search_query (SearchQuery): The search parameters, including the query vector and k.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        List[SearchResult]: A list of search results, each containing a chunk and its distance to the query vector.

    Raises:
        HTTPException: If the library is not found or if there's an error during the search process.
    """
    try:
        results = vector_db.knn_search(library_id, search_query.query_vector, search_query.k)
        logger.info(f"Performed kNN search in library {library_id} with k={search_query.k}")
        return [SearchResult(chunk=chunk, distance=distance) for chunk, distance in results]
    except LibraryNotFoundException as e:
        logger.error(f"Library not found during kNN search: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid input for kNN search: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during kNN search: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the search")

# Optional: Add an endpoint for cosine similarity search if needed
@router.post("/{library_id}/cosine", response_model=List[SearchResult])
async def cosine_similarity_search(
    library_id: str,
    search_query: SearchQuery,
    vector_db: VectorDatabase = Depends(get_vector_db())
) -> List[SearchResult]:
    """
    Perform a cosine similarity search in the specified library.

    This endpoint searches for the k most similar vectors using cosine similarity
    within the specified library.

    Args:
        library_id (str): The ID of the library to search in.
        search_query (SearchQuery): The search parameters, including the query vector and k.
        vector_db (VectorDatabase): The vector database instance (injected dependency).

    Returns:
        List[SearchResult]: A list of search results, each containing a chunk and its cosine similarity to the query vector.

    Raises:
        HTTPException: If the library is not found or if there's an error during the search process.
    """
    try:
        # Assuming vector_db has a cosine_similarity_search method
        results = vector_db.cosine_similarity_search(library_id, search_query.query_vector, search_query.k)
        logger.info(f"Performed cosine similarity search in library {library_id} with k={search_query.k}")
        return [SearchResult(chunk=chunk, distance=1 - similarity) for chunk, similarity in results]
    except LibraryNotFoundException as e:
        logger.error(f"Library not found during cosine similarity search: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid input for cosine similarity search: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during cosine similarity search: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the search")