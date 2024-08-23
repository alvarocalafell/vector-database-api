# from fastapi import APIRouter, Depends, HTTPException
# from dependency_injector.wiring import inject, Provide
# from app.core.entities.chunk import Chunk
# from app.core.services.library_service import LibraryService
# from app.di_container import Container
# from app.core.exceptions import VectorDBException

# router = APIRouter()

# @router.post("/libraries/{library_id}/documents/{document_id}/chunks", response_model=Chunk)
# @inject
# async def create_chunk(
#     library_id: str,
#     document_id: str,
#     chunk: Chunk,
#     library_service: LibraryService = Depends(Provide[Container.library_service])
# ):
#     """
#     Create a new chunk within a document in a library.

#     Parameters:
#     - library_id: ID of the library
#     - document_id: ID of the document
#     - chunk: Chunk object to be created

#     Returns:
#     - Created Chunk object
#     """
#     try:
#         return await library_service.add_chunk_to_document(library_id, document_id, chunk)
#     except VectorDBException as e:
#         raise HTTPException(status_code=e.status_code, detail=str(e))

# @router.get("/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}", response_model=Chunk)
# @inject
# async def get_chunk(
#     library_id: str,
#     document_id: str,
#     chunk_id: str,
#     library_service: LibraryService = Depends(Provide[Container.library_service])
# ):
#     """
#     Retrieve a specific chunk from a document in a library.

#     Parameters:
#     - library_id: ID of the library
#     - document_id: ID of the document
#     - chunk_id: ID of the chunk

#     Returns:
#     - Chunk object
#     """
#     try:
#         return await library_service.get_chunk(library_id, document_id, chunk_id)
#     except VectorDBException as e:
#         raise HTTPException(status_code=e.status_code, detail=str(e))

# @router.put("/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}", response_model=Chunk)
# @inject
# async def update_chunk(
#     library_id: str,
#     document_id: str,
#     chunk_id: str,
#     chunk: Chunk,
#     library_service: LibraryService = Depends(Provide[Container.library_service])
# ):
#     """
#     Update a specific chunk in a document in a library.

#     Parameters:
#     - library_id: ID of the library
#     - document_id: ID of the document
#     - chunk_id: ID of the chunk
#     - chunk: Updated Chunk object

#     Returns:
#     - Updated Chunk object
#     """
#     try:
#         return await library_service.update_chunk(library_id, document_id, chunk_id, chunk)
#     except VectorDBException as e:
#         raise HTTPException(status_code=e.status_code, detail=str(e))

# @router.delete("/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}", status_code=204)
# @inject
# async def delete_chunk(
#     library_id: str,
#     document_id: str,
#     chunk_id: str,
#     library_service: LibraryService = Depends(Provide[Container.library_service])
# ):
#     """
#     Delete a specific chunk from a document in a library.

#     Parameters:
#     - library_id: ID of the library
#     - document_id: ID of the document
#     - chunk_id: ID of the chunk
#     """
#     try:
#         await library_service.delete_chunk(library_id, document_id, chunk_id)
#     except VectorDBException as e:
#         raise HTTPException(status_code=e.status_code, detail=str(e))