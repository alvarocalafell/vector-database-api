from typing import Dict, List, Tuple
import threading
from ..models.data_models import Chunk, Document, Library
from ..services.indexing import IndexingAlgorithm, KDTree, BallTree, BruteForce
import numpy as np
from .exceptions import LibraryNotFoundException, DocumentNotFoundException, ChunkNotFoundException, DuplicateLibraryException
import logging
import traceback


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self, indexing_algorithm: str = 'kdtree'):
        self.libraries: Dict[str, Library] = {}
        self.index: Dict[str, IndexingAlgorithm] = {}
        self.lock = threading.RLock()
        self.indexing_algorithm = indexing_algorithm

    def _get_indexing_algorithm(self) -> IndexingAlgorithm:
        if self.indexing_algorithm == 'kdtree':
            return KDTree()
        elif self.indexing_algorithm == 'balltree':
            return BallTree()
        elif self.indexing_algorithm == 'bruteforce':
            return BruteForce()
        else:
            raise ValueError(f"Unknown indexing algorithm: {self.indexing_algorithm}")

    def create_library(self, library: Library) -> None:
        logger.debug(f"Attempting to create library: {library.id}")
        with self.lock:
            if library.id in self.libraries:
                logger.error(f"Duplicate library id: {library.id}")
                raise DuplicateLibraryException(library.id)
            self.libraries[library.id] = library
            self.index[library.id] = self._get_indexing_algorithm()
            logger.info(f"Library created: {library.id}")

    def get_library(self, library_id: str) -> Library:
        logger.debug(f"Attempting to get library: {library_id}")
        with self.lock:
            if library_id not in self.libraries:
                logger.error(f"Library not found: {library_id}")
                raise LibraryNotFoundException(library_id)
            return self.libraries[library_id]
    
    def _rebuild_index(self, library_id: str) -> None:
        logger.debug(f"Entering _rebuild_index method for library {library_id}")
        library = self.libraries[library_id]
        vectors = [chunk.embedding for doc in library.documents for chunk in doc.chunks]
        logger.debug(f"Number of vectors to index: {len(vectors)}")
        
        if library_id not in self.index:
            self.index[library_id] = self._get_indexing_algorithm()
        
        self.index[library_id].build(vectors)
        logger.debug(f"Index rebuilt with {len(vectors)} vectors")


    def update_library(self, library: Library) -> Library:
        logger.debug(f"Attempting to update library: {library.id}")
        with self.lock:
            logger.debug(f"Acquired lock for update_library: {library.id}")
            if library.id not in self.libraries:
                logger.error(f"Library with id {library.id} does not exist")
                raise LibraryNotFoundException(library.id)
            
            # Update the library
            self.libraries[library.id] = library
            
            # Rebuild the index if necessary (e.g., if documents were updated)
            self._rebuild_index(library.id)
            
            logger.debug(f"Library updated: {library.id}")
            return self.libraries[library.id]  # Return the updated library
        logger.debug(f"Released lock for update_library: {library.id}")

    def delete_library(self, library_id: str) -> None:
        with self.lock:
            if library_id not in self.libraries:
                raise LibraryNotFoundException(library_id)
            del self.libraries[library_id]
            del self.index[library_id]
            
    def add_document(self, library_id: str, document: Document) -> None:
        logger.debug(f"Entering add_document method for library {library_id}")
        with self.lock:
            logger.debug(f"Acquired lock for add_document: library {library_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise LibraryNotFoundException(library_id)

                library = self.libraries[library_id]
                library.documents.append(document)
                logger.debug(f"Document appended. Library now has {len(library.documents)} documents")

                # Rebuild the index with all vectors
                all_vectors = [chunk.embedding for doc in library.documents for chunk in doc.chunks]
                if all_vectors:
                    self.index[library_id] = self._get_indexing_algorithm()
                    self.index[library_id].build(all_vectors)
                    logger.debug(f"Index rebuilt with {len(all_vectors)} vectors of dimension {len(all_vectors[0])}")
                else:
                    logger.warning(f"No vectors to index in library {library_id}")

            except Exception as e:
                logger.error(f"Error in add_document: {str(e)}")
                raise 
            finally:
                logger.debug(f"Releasing lock for add_document: library {library_id}")

    def get_document(self, library_id: str, document_id: str) -> Document:
        logger.debug(f"Entering get_document method for library {library_id}, document {document_id}")
        with self.lock:
            logger.debug(f"Acquired lock for get_document: library {library_id}, document {document_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise LibraryNotFoundException(library_id)
                
                library = self.libraries[library_id]
                logger.debug(f"Retrieved library {library_id}")
                
                for doc in library.documents:
                    if doc.id == document_id:
                        logger.debug(f"Found document {document_id} in library {library_id}")
                        return doc
                
                logger.error(f"Document {document_id} not found in library {library_id}")
                raise DocumentNotFoundException(document_id, library_id)
            finally:
                logger.debug(f"Releasing lock for get_document: library {library_id}, document {document_id}")


    def update_document(self, library_id: str, document: Document) -> Document:
        logger.debug(f"Entering update_document method for library {library_id}, document {document.id}")
        with self.lock:
            logger.debug(f"Acquired lock for update_document: library {library_id}, document {document.id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise LibraryNotFoundException(library_id)
                
                library = self.libraries[library_id]
                logger.debug(f"Retrieved library {library_id}")
                
                for i, doc in enumerate(library.documents):
                    if doc.id == document.id:
                        library.documents[i] = document
                        logger.debug(f"Updated document {document.id} in library {library_id}")
                        self._rebuild_index(library_id)
                        return document
                
                logger.error(f"Document {document.id} not found in library {library_id}")
                raise DocumentNotFoundException(document.id, library_id)
            finally:
                logger.debug(f"Releasing lock for update_document: library {library_id}, document {document.id}")

    def delete_document(self, library_id: str, document_id: str) -> None:
        logger.debug(f"Entering delete_document method for library {library_id}, document {document_id}")
        with self.lock:
            logger.debug(f"Acquired lock for delete_document: library {library_id}, document {document_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise LibraryNotFoundException(library_id)
                
                library = self.libraries[library_id]
                logger.debug(f"Retrieved library {library_id}")
                
                original_length = len(library.documents)
                library.documents = [doc for doc in library.documents if doc.id != document_id]
                
                if len(library.documents) == original_length:
                    logger.error(f"Document {document_id} not found in library {library_id}")
                    raise DocumentNotFoundException(document_id, library_id)
                
                logger.debug(f"Deleted document {document_id} from library {library_id}")
                self._rebuild_index(library_id)
            finally:
                logger.debug(f"Releasing lock for delete_document: library {library_id}, document {document_id}")

    def add_chunk(self, library_id: str, document_id: str, chunk: Chunk) -> Chunk:
        with self.lock:
            if library_id not in self.libraries:
                raise LibraryNotFoundException(library_id)
            library = self.libraries[library_id]
            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                raise DocumentNotFoundException(document_id, library_id)
            document.chunks.append(chunk)
            self._rebuild_index(library_id)
            return chunk
        
    def get_chunk(self, library_id: str, document_id: str, chunk_id: str) -> Chunk:
        with self.lock:
            if library_id not in self.libraries:
                raise LibraryNotFoundException(library_id)
            
            library = self.libraries[library_id]
            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                raise DocumentNotFoundException(document_id, library_id)
            
            chunk = next((chunk for chunk in document.chunks if chunk.id == chunk_id), None)
            if not chunk:
                raise ChunkNotFoundException(chunk_id, document_id)
            
            return chunk

    def update_chunk(self, library_id: str, document_id: str, chunk_id: str, updated_chunk: Chunk) -> Chunk:
        logger.info(f"Attempting to update chunk in database: library_id={library_id}, document_id={document_id}, chunk_id={chunk_id}")
        try:
            with self.lock:
                if library_id not in self.libraries:
                    logger.error(f"Library not found: {library_id}")
                    raise LibraryNotFoundException(library_id)
                library = self.libraries[library_id]
                document = next((doc for doc in library.documents if doc.id == document_id), None)
                if not document:
                    logger.error(f"Document not found: {document_id} in library {library_id}")
                    raise DocumentNotFoundException(document_id, library_id)
                for i, chunk in enumerate(document.chunks):
                    if chunk.id == chunk_id:
                        if updated_chunk.id != chunk_id:
                            logger.error(f"Chunk ID mismatch: existing={chunk_id}, update={updated_chunk.id}")
                            raise ValueError(f"Chunk ID in the update data ({updated_chunk.id}) does not match the chunk ID in the path ({chunk_id})")
                        document.chunks[i] = updated_chunk
                        self._rebuild_index(library_id)
                        logger.info(f"Successfully updated chunk: {chunk_id}")
                        return updated_chunk
                logger.error(f"Chunk not found: {chunk_id} in document {document_id}")
                raise ChunkNotFoundException(chunk_id, document_id)
        except Exception as e:
            logger.error(f"Error in update_chunk: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def delete_chunk(self, library_id: str, document_id: str, chunk_id: str) -> None:
        with self.lock:
            if library_id not in self.libraries:
                raise LibraryNotFoundException(library_id)
            library = self.libraries[library_id]
            document = next((doc for doc in library.documents if doc.id == document_id), None)
            if not document:
                raise DocumentNotFoundException(document_id, library_id)
            original_length = len(document.chunks)
            document.chunks = [chunk for chunk in document.chunks if chunk.id != chunk_id]
            if len(document.chunks) == original_length:
                raise ChunkNotFoundException(chunk_id, document_id)
            self._rebuild_index(library_id)
    
    def knn_search(self, library_id: str, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        logger.debug(f"Entering knn_search method for library {library_id}")
        with self.lock:
            logger.debug(f"Acquired lock for knn_search: library {library_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise ValueError(f"Library with id {library_id} does not exist")
                
                library = self.libraries[library_id]
                chunks = [chunk for doc in library.documents for chunk in doc.chunks]
                
                if not chunks:
                    logger.warning(f"Library {library_id} has no chunks")
                    return []
                
                if library_id not in self.index:
                    logger.warning(f"No index for library {library_id}, rebuilding")
                    self._rebuild_index(library_id)
                
                results = self.index[library_id].search(np.array(query_vector), k)
                
                logger.debug(f"KNN search completed for library {library_id}")
                return [(chunks[idx], dist) for idx, dist in results]
            finally:
                logger.debug(f"Releasing lock for knn_search: library {library_id}")


    
    def library_exists(self, library_id: str) -> bool:
        logger.debug(f"Checking if library {library_id} exists")
        with self.lock:
            return library_id in self.libraries