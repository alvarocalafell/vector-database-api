from fastapi import HTTPException

class VectorDatabaseException(HTTPException):
    """
    Base exception class for all vector database related exceptions.

    This exception inherits from FastAPI's HTTPException to allow for
    easy integration with the API's error handling.

    Attributes:
        status_code (int): The HTTP status code associated with this exception.
        detail (str): A detailed description of the error.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        """
        Initialize a new VectorDatabaseException.

        Args:
            status_code (int): The HTTP status code to be returned.
            detail (str): A detailed description of the error.
        """
        super().__init__(status_code=status_code, detail=detail)


class LibraryNotFoundException(VectorDatabaseException):
    """
    Exception raised when a requested library is not found in the database.

    Attributes:
        library_id (str): The ID of the library that was not found.
    """

    def __init__(self, library_id: str) -> None:
        """
        Initialize a new LibraryNotFoundException.

        Args:
            library_id (str): The ID of the library that was not found.
        """
        super().__init__(status_code=404, detail=f"Library with id {library_id} not found")


class DocumentNotFoundException(VectorDatabaseException):
    """
    Exception raised when a requested document is not found in a library.

    Attributes:
        document_id (str): The ID of the document that was not found.
        library_id (str): The ID of the library where the document was searched.
    """

    def __init__(self, document_id: str, library_id: str) -> None:
        """
        Initialize a new DocumentNotFoundException.

        Args:
            document_id (str): The ID of the document that was not found.
            library_id (str): The ID of the library where the document was searched.
        """
        super().__init__(status_code=404, detail=f"Document {document_id} not found in library {library_id}")


class ChunkNotFoundException(VectorDatabaseException):
    """
    Exception raised when a requested chunk is not found in a document.

    Attributes:
        chunk_id (str): The ID of the chunk that was not found.
        document_id (str): The ID of the document where the chunk was searched.
    """

    def __init__(self, chunk_id: str, document_id: str) -> None:
        """
        Initialize a new ChunkNotFoundException.

        Args:
            chunk_id (str): The ID of the chunk that was not found.
            document_id (str): The ID of the document where the chunk was searched.
        """
        super().__init__(status_code=404, detail=f"Chunk {chunk_id} not found in document {document_id}")


class DuplicateLibraryException(VectorDatabaseException):
    """
    Exception raised when attempting to create a library with an ID that already exists.

    Attributes:
        library_id (str): The ID of the library that already exists.
    """

    def __init__(self, library_id: str) -> None:
        """
        Initialize a new DuplicateLibraryException.

        Args:
            library_id (str): The ID of the library that already exists.
        """
        super().__init__(status_code=400, detail=f"Library with id {library_id} already exists")


class InvalidEmbeddingDimensionException(VectorDatabaseException):
    """
    Exception raised when an embedding vector has an invalid dimension.

    Attributes:
        expected (int): The expected dimension of the embedding.
        received (int): The actual dimension of the provided embedding.
    """

    def __init__(self, expected: int, received: int) -> None:
        """
        Initialize a new InvalidEmbeddingDimensionException.

        Args:
            expected (int): The expected dimension of the embedding.
            received (int): The actual dimension of the provided embedding.
        """
        super().__init__(status_code=400, detail=f"Invalid embedding dimension. Expected {expected}, but received {received}")