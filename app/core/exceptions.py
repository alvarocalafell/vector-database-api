from fastapi import HTTPException

class VectorDatabaseException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class LibraryNotFoundException(VectorDatabaseException):
    def __init__(self, library_id: str):
        super().__init__(status_code=404, detail=f"Library with id {library_id} not found")

class DocumentNotFoundException(VectorDatabaseException):
    def __init__(self, document_id: str, library_id: str):
        super().__init__(status_code=404, detail=f"Document {document_id} not found in library {library_id}")

class ChunkNotFoundException(VectorDatabaseException):
    def __init__(self, chunk_id: str, document_id: str):
        super().__init__(status_code=404, detail=f"Chunk {chunk_id} not found in document {document_id}")

class DuplicateLibraryException(VectorDatabaseException):
    def __init__(self, library_id: str):
        super().__init__(status_code=400, detail=f"Library with id {library_id} already exists")

class InvalidEmbeddingDimensionException(VectorDatabaseException):
    def __init__(self, expected: int, received: int):
        super().__init__(status_code=400, detail=f"Invalid embedding dimension. Expected {expected}, but received {received}")