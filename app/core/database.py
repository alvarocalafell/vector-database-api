from typing import Dict, List, Tuple
from ..models.data_models import Chunk, Document, Library
from ..services.indexing import IndexingAlgorithm, KDTree, BallTree, BruteForce
import numpy as np
from .exceptions import (
    LibraryNotFoundException,
    DocumentNotFoundException,
    ChunkNotFoundException,
    DuplicateLibraryException,
)
import logging
import threading

logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    A vector database for efficient storage and retrieval of vector embeddings.

    This class provides methods for managing libraries, documents, and chunks,
    as well as performing k-nearest neighbor searches on the stored vectors.

    Attributes:
        libraries (Dict[str, Library]): A dictionary of libraries, keyed by library ID.
        index (Dict[str, IndexingAlgorithm]): A dictionary of indexing algorithms, keyed by library ID.
        lock (threading.RLock): A reentrant lock for thread-safe operations.
        indexing_algorithm (str): The name of the indexing algorithm to use.
    """

    def __init__(self, indexing_algorithm: str = 'kdtree') -> None:
        """
        Initialize a new VectorDatabase instance.

        Args:
            indexing_algorithm (str): The name of the indexing algorithm to use. 
                                      Options are 'kdtree', 'balltree', or 'bruteforce'.
        """
        self.libraries: Dict[str, Library] = {}
        self.index: Dict[str, IndexingAlgorithm] = {}
        self.lock: threading.RLock = threading.RLock()
        self.indexing_algorithm: str = indexing_algorithm

    def create_library(self, library: Library) -> None:
        """
        Create a new library in the database.

        Args:
            library (Library): The library to create.

        Raises:
            DuplicateLibraryException: If a library with the same ID already exists.
        """
        with self.lock:
            if library.id in self.libraries:
                logger.error(f"Attempt to create duplicate library: {library.id}")
                raise DuplicateLibraryException(library.id)
            self.libraries[library.id] = library
            self.index[library.id] = self._get_indexing_algorithm()
            logger.info(f"Created new library: {library.id}")

    def get_library(self, library_id: str) -> Library:
        """
        Retrieve a library from the database.

        Args:
            library_id (str): The ID of the library to retrieve.

        Returns:
            Library: The requested library.

        Raises:
            LibraryNotFoundException: If the library does not exist.
        """
        with self.lock:
            if library_id not in self.libraries:
                logger.error(f"Attempt to access non-existent library: {library_id}")
                raise LibraryNotFoundException(library_id)
            logger.info(f"Retrieved library: {library_id}")
            return self.libraries[library_id]

    def update_library(self, library: Library) -> Library:
        """
        Update an existing library in the database.

        Args:
            library (Library): The updated library data.

        Returns:
            Library: The updated library.

        Raises:
            LibraryNotFoundException: If the library does not exist.
        """
        with self.lock:
            if library.id not in self.libraries:
                logger.error(f"Attempt to update non-existent library: {library.id}")
                raise LibraryNotFoundException(library.id)
            self.libraries[library.id] = library
            self._rebuild_index(library.id)
            logger.info(f"Updated library: {library.id}")
            return self.libraries[library.id]

    def delete_library(self, library_id: str) -> None:
        """
        Delete a library from the database.

        Args:
            library_id (str): The ID of the library to delete.

        Raises:
            LibraryNotFoundException: If the library does not exist.
        """
        with self.lock:
            if library_id not in self.libraries:
                logger.error(f"Attempt to delete non-existent library: {library_id}")
                raise LibraryNotFoundException(library_id)
            del self.libraries[library_id]
            del self.index[library_id]
            logger.info(f"Deleted library: {library_id}")

    def add_document(self, library_id: str, document: Document) -> None:
        """
        Add a document to a library.

        Args:
            library_id (str): The ID of the library to add the document to.
            document (Document): The document to add.

        Raises:
            LibraryNotFoundException: If the library does not exist.
        """
        with self.lock:
            library = self.get_library(library_id)
            library.documents.append(document)
            self._rebuild_index(library_id)
            logger.info(f"Added document {document.id} to library {library_id}")

    def get_document(self, library_id: str, document_id: str) -> Document:
        """
        Retrieve a document from a library.

        Args:
            library_id (str): The ID of the library containing the document.
            document_id (str): The ID of the document to retrieve.

        Returns:
            Document: The requested document.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
        """
        with self.lock:
            library = self.get_library(library_id)
            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                logger.error(f"Document {document_id} not found in library {library_id}")
                raise DocumentNotFoundException(document_id, library_id)
            logger.info(f"Retrieved document {document_id} from library {library_id}")
            return document

    def update_document(self, library_id: str, document: Document) -> Document:
        """
        Update an existing document in a library.

        Args:
            library_id (str): The ID of the library containing the document.
            document (Document): The updated document data.

        Returns:
            Document: The updated document.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
        """
        with self.lock:
            library = self.get_library(library_id)
            for i, doc in enumerate(library.documents):
                if doc.id == document.id:
                    library.documents[i] = document
                    self._rebuild_index(library_id)
                    logger.info(f"Updated document {document.id} in library {library_id}")
                    return document
            logger.error(f"Document {document.id} not found in library {library_id}")
            raise DocumentNotFoundException(document.id, library_id)

    def delete_document(self, library_id: str, document_id: str) -> None:
        """
        Delete a document from a library.

        Args:
            library_id (str): The ID of the library containing the document.
            document_id (str): The ID of the document to delete.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
        """
        with self.lock:
            library = self.get_library(library_id)
            original_length = len(library.documents)
            library.documents = [doc for doc in library.documents if doc.id != document_id]
            if len(library.documents) == original_length:
                logger.error(f"Document {document_id} not found in library {library_id}")
                raise DocumentNotFoundException(document_id, library_id)
            self._rebuild_index(library_id)
            logger.info(f"Deleted document {document_id} from library {library_id}")

    def add_chunk(self, library_id: str, document_id: str, chunk: Chunk) -> Chunk:
        """
        Add a chunk to a document in a library.

        Args:
            library_id (str): The ID of the library containing the document.
            document_id (str): The ID of the document to add the chunk to.
            chunk (Chunk): The chunk to add.

        Returns:
            Chunk: The added chunk.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
        """
        with self.lock:
            document = self.get_document(library_id, document_id)
            document.chunks.append(chunk)
            self._rebuild_index(library_id)
            logger.info(f"Added chunk {chunk.id} to document {document_id} in library {library_id}")
            return chunk

    def get_chunk(self, library_id: str, document_id: str, chunk_id: str) -> Chunk:
        """
        Retrieve a chunk from a document in a library.

        Args:
            library_id (str): The ID of the library containing the document.
            document_id (str): The ID of the document containing the chunk.
            chunk_id (str): The ID of the chunk to retrieve.

        Returns:
            Chunk: The requested chunk.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
            ChunkNotFoundException: If the chunk does not exist in the document.
        """
        with self.lock:
            document = self.get_document(library_id, document_id)
            chunk = next((chunk for chunk in document.chunks if chunk.id == chunk_id), None)
            if not chunk:
                logger.error(f"Chunk {chunk_id} not found in document {document_id}")
                raise ChunkNotFoundException(chunk_id, document_id)
            logger.info(f"Retrieved chunk {chunk_id} from document {document_id} in library {library_id}")
            return chunk

    def update_chunk(self, library_id: str, document_id: str, chunk_id: str, updated_chunk: Chunk) -> Chunk:
        """
        Update an existing chunk in a document.

        Args:
            library_id (str): The ID of the library containing the document.
            document_id (str): The ID of the document containing the chunk.
            chunk_id (str): The ID of the chunk to update.
            updated_chunk (Chunk): The updated chunk data.

        Returns:
            Chunk: The updated chunk.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
            ChunkNotFoundException: If the chunk does not exist in the document.
            ValueError: If the chunk ID in the update data doesn't match the chunk_id parameter.
        """
        with self.lock:
            document = self.get_document(library_id, document_id)
            for i, chunk in enumerate(document.chunks):
                if chunk.id == chunk_id:
                    if updated_chunk.id != chunk_id:
                        logger.error(f"Chunk ID mismatch: existing={chunk_id}, update={updated_chunk.id}")
                        raise ValueError(f"Chunk ID mismatch: existing={chunk_id}, update={updated_chunk.id}")
                    document.chunks[i] = updated_chunk
                    self._rebuild_index(library_id)
                    logger.info(f"Updated chunk {chunk_id} in document {document_id} in library {library_id}")
                    return updated_chunk
            logger.error(f"Chunk {chunk_id} not found in document {document_id}")
            raise ChunkNotFoundException(chunk_id, document_id)

    def delete_chunk(self, library_id: str, document_id: str, chunk_id: str) -> None:
        """
        Delete a chunk from a document in a library.

        Args:
            library_id (str): The ID of the library containing the document.
            document_id (str): The ID of the document containing the chunk.
            chunk_id (str): The ID of the chunk to delete.

        Raises:
            LibraryNotFoundException: If the library does not exist.
            DocumentNotFoundException: If the document does not exist in the library.
            ChunkNotFoundException: If the chunk does not exist in the document.
        """
        with self.lock:
            document = self.get_document(library_id, document_id)
            original_length = len(document.chunks)
            document.chunks = [chunk for chunk in document.chunks if chunk.id != chunk_id]
            if len(document.chunks) == original_length:
                logger.error(f"Chunk {chunk_id} not found in document {document_id}")
                raise ChunkNotFoundException(chunk_id, document_id)
            self._rebuild_index(library_id)
            logger.info(f"Deleted chunk {chunk_id} from document {document_id} in library {library_id}")

    def knn_search(self, library_id: str, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        """
        Perform a k-nearest neighbor search in the specified library.

        Args:
            library_id (str): The ID of the library to search in.
            query_vector (List[float]): The query vector to search for.
            k (int): The number of nearest neighbors to return.

        Returns:
            List[Tuple[Chunk, float]]: A list of tuples containing the k nearest chunks and their distances.

        Raises:
            LibraryNotFoundException: If the library does not exist.
        """
        with self.lock:
            library = self.get_library(library_id)
            chunks = [chunk for doc in library.documents for chunk in doc.chunks]
            if not chunks:
                logger.warning(f"No chunks found in library {library_id} for knn search")
                return []
            if library_id not in self.index:
                self._rebuild_index(library_id)
            results = self.index[library_id].search(np.array(query_vector), k)
            logger.info(f"Performed knn search in library {library_id} with k={k}")
            return [(chunks[idx], dist) for idx, dist in results]

    def _rebuild_index(self, library_id: str) -> None:
        """
        Rebuild the index for the specified library.

        This method is called internally whenever the library contents change.

        Args:
            library_id (str): The ID of the library whose index needs to be rebuilt.
        """
        library = self.libraries[library_id]
        vectors = [chunk.embedding for doc in library.documents for chunk in doc.chunks]
        if library_id not in self.index:
            self.index[library_id] = self._get_indexing_algorithm()
        self.index[library_id].build(vectors)
        logger.info(f"Rebuilt index for library {library_id}")

    def _get_indexing_algorithm(self) -> IndexingAlgorithm:
        """
        Get the appropriate indexing algorithm based on the database configuration.

        Returns:
            IndexingAlgorithm: An instance of the configured indexing algorithm.

        Raises:
            ValueError: If an unknown indexing algorithm is specified.
        """
        if self.indexing_algorithm == 'kdtree':
            return KDTree()
        elif self.indexing_algorithm == 'balltree':
            return BallTree()
        elif self.indexing_algorithm == 'bruteforce':
            return BruteForce()
        else:
            logger.error(f"Unknown indexing algorithm: {self.indexing_algorithm}")
            raise ValueError
    
def library_exists(self, library_id: str) -> bool:
        """
        Check if a library with the given ID exists in the database.

        This method is thread-safe and can be used to verify the existence of a library
        without raising an exception.

        Args:
            library_id (str): The ID of the library to check.

        Returns:
            bool: True if the library exists, False otherwise.
        """
        logger.debug(f"Checking if library {library_id} exists")
        with self.lock:
            exists = library_id in self.libraries
            logger.debug(f"Library {library_id} {'exists' if exists else 'does not exist'}")
            return exists