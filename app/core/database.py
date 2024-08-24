from typing import Dict, List, Tuple
import threading
from ..models.data_models import Chunk, Document, Library
from ..services.indexing import VectorIndex, KDTree
import numpy as np
import logging
import time


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self):
        self.libraries: Dict[str, Library] = {}
        self.index: Dict[str, VectorIndex] = {}
        self.lock = threading.Lock()

    def get_library(self, library_id: str) -> Library:
        logger.debug(f"Entering get_library method for library {library_id}")
        with self.lock:
            logger.debug(f"Acquired lock for get_library: {library_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library with id {library_id} does not exist")
                    raise ValueError(f"Library with id {library_id} does not exist")
                logger.debug(f"Retrieved library: {library_id}")
                return self.libraries[library_id]
            finally:
                logger.debug(f"Releasing lock for get_library: {library_id}")

    def create_library(self, library: Library) -> None:
        logger.debug(f"Entering create_library method for library {library.id}")
        with self.lock:
            logger.debug("Acquired lock in create_library method")
            if library.id in self.libraries:
                logger.error(f"Library with id {library.id} already exists")
                raise ValueError(f"Library with id {library.id} already exists")
            self.libraries[library.id] = library
            self.index[library.id] = KDTree()
            logger.debug(f"Created library: {library}")

    def add_document(self, library_id: str, document: Document) -> None:
        logger.debug(f"Entering add_document method for library {library_id}")
        with self.lock:
            logger.debug(f"Acquired lock for add_document: library {library_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise ValueError(f"Library with id {library_id} does not exist")

                library = self.libraries[library_id]
                library.documents.append(document)
                logger.debug(f"Document appended. Library now has {len(library.documents)} documents")

                # Rebuild the index with all vectors
                all_vectors = [chunk.embedding for doc in library.documents for chunk in doc.chunks]
                if all_vectors:
                    self.index[library_id] = KDTree()
                    self.index[library_id].build(all_vectors)
                    logger.debug(f"Index rebuilt with {len(all_vectors)} vectors of dimension {len(all_vectors[0])}")
                else:
                    logger.warning(f"No vectors to index in library {library_id}")

            except Exception as e:
                logger.error(f"Error in add_document: {str(e)}")
                raise
            finally:
                logger.debug(f"Releasing lock for add_document: library {library_id}")


    def _rebuild_index(self, library_id: str) -> None:
        logger.debug(f"Entering _rebuild_index method for library {library_id}")
        library = self.libraries[library_id]
        logger.debug(f"Retrieved library for indexing: {library}")
        vectors = [chunk.embedding for doc in library.documents for chunk in doc.chunks]
        logger.debug(f"Number of vectors to index: {len(vectors)}")
        start_time = time.time()
        if library_id not in self.index:
            logger.debug(f"Creating new KDTree for library {library_id}")
            self.index[library_id] = KDTree()
        logger.debug("Building index")
        self.index[library_id].build(vectors)
        logger.debug(f"Time to build index: {time.time() - start_time:.2f} seconds")

    def update_library(self, library: Library) -> Library:
        logger.debug(f"Attempting to update library: {library.id}")
        with self.lock:
            logger.debug(f"Acquired lock for update_library: {library.id}")
            if library.id not in self.libraries:
                logger.error(f"Library with id {library.id} does not exist")
                raise ValueError(f"Library with id {library.id} does not exist")
            
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
                raise ValueError(f"Library with id {library_id} does not exist")
            del self.libraries[library_id]
            del self.index[library_id]

    def get_document(self, library_id: str, document_id: str) -> Document:
        logger.debug(f"Entering get_document method for library {library_id}, document {document_id}")
        with self.lock:
            logger.debug(f"Acquired lock for get_document: library {library_id}, document {document_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise ValueError(f"Library with id {library_id} does not exist")
                
                library = self.libraries[library_id]
                logger.debug(f"Retrieved library {library_id}")
                
                for doc in library.documents:
                    if doc.id == document_id:
                        logger.debug(f"Found document {document_id} in library {library_id}")
                        return doc
                
                logger.error(f"Document {document_id} not found in library {library_id}")
                raise ValueError(f"Document with id {document_id} does not exist in library {library_id}")
            finally:
                logger.debug(f"Releasing lock for get_document: library {library_id}, document {document_id}")


    def update_document(self, library_id: str, document: Document) -> Document:
        logger.debug(f"Entering update_document method for library {library_id}, document {document.id}")
        with self.lock:
            logger.debug(f"Acquired lock for update_document: library {library_id}, document {document.id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise ValueError(f"Library with id {library_id} does not exist")
                
                library = self.libraries[library_id]
                logger.debug(f"Retrieved library {library_id}")
                
                for i, doc in enumerate(library.documents):
                    if doc.id == document.id:
                        library.documents[i] = document
                        logger.debug(f"Updated document {document.id} in library {library_id}")
                        self._rebuild_index(library_id)
                        return document
                
                logger.error(f"Document {document.id} not found in library {library_id}")
                raise ValueError(f"Document with id {document.id} does not exist in library {library_id}")
            finally:
                logger.debug(f"Releasing lock for update_document: library {library_id}, document {document.id}")

    def delete_document(self, library_id: str, document_id: str) -> None:
        logger.debug(f"Entering delete_document method for library {library_id}, document {document_id}")
        with self.lock:
            logger.debug(f"Acquired lock for delete_document: library {library_id}, document {document_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise ValueError(f"Library with id {library_id} does not exist")
                
                library = self.libraries[library_id]
                logger.debug(f"Retrieved library {library_id}")
                
                original_length = len(library.documents)
                library.documents = [doc for doc in library.documents if doc.id != document_id]
                
                if len(library.documents) == original_length:
                    logger.error(f"Document {document_id} not found in library {library_id}")
                    raise ValueError(f"Document with id {document_id} does not exist in library {library_id}")
                
                logger.debug(f"Deleted document {document_id} from library {library_id}")
                self._rebuild_index(library_id)
            finally:
                logger.debug(f"Releasing lock for delete_document: library {library_id}, document {document_id}")


    def _rebuild_index(self, library_id: str) -> None:
        library = self.libraries[library_id]
        vectors = [chunk.embedding for doc in library.documents for chunk in doc.chunks]
        self.index[library_id].build(vectors)

    def knn_search(self, library_id: str, query_vector: List[float], k: int) -> List[Tuple[Chunk, float]]:
        logger.debug(f"Entering knn_search method for library {library_id}")
        with self.lock:
            logger.debug(f"Acquired lock for knn_search: library {library_id}")
            try:
                if library_id not in self.libraries:
                    logger.error(f"Library {library_id} not found")
                    raise ValueError(f"Library with id {library_id} does not exist")
                
                if library_id not in self.index:
                    logger.error(f"Index for library {library_id} not found")
                    raise ValueError(f"Index for library with id {library_id} does not exist")
                
                library = self.libraries[library_id]
                chunks = [chunk for doc in library.documents for chunk in doc.chunks]
                
                if not chunks:
                    logger.warning(f"Library {library_id} has no chunks")
                    return []
                
                # Ensure query vector has the same dimension as the indexed vectors
                indexed_dim = len(chunks[0].embedding)
                if len(query_vector) != indexed_dim:
                    logger.error(f"Query vector dimension ({len(query_vector)}) does not match indexed vectors dimension ({indexed_dim})")
                    raise ValueError(f"Query vector dimension ({len(query_vector)}) does not match indexed vectors dimension ({indexed_dim})")
                
                results = self.index[library_id].search(np.array(query_vector), k)
                
                logger.debug(f"KNN search completed for library {library_id}")
                return [(chunks[idx], dist) for idx, dist in results]
            finally:
                logger.debug(f"Releasing lock for knn_search: library {library_id}")

    
    def library_exists(self, library_id: str) -> bool:
        logger.debug(f"Checking if library {library_id} exists")
        with self.lock:
            return library_id in self.libraries