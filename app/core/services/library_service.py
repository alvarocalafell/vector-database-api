import uuid
import logging
from typing import List
from app.core.entities import Library, Document
from app.core.exceptions import NotFoundError, ValidationError
from app.adapters.repositories.in_memory.library_repository_in_memory import InMemoryLibraryRepository

logger = logging.getLogger(__name__)

class LibraryService():
    def __init__(self, repository: InMemoryLibraryRepository): #Check if should be LibraryRepository
        self.repository = repository

    def create_library(self, name: str) -> Library:
        """
        Create a new library with the given name.

        Args:
            name (str): The name of the library.

        Returns:
            Library: The created library.

        Raises:
            ValidationError: If the name is empty or invalid.
        """
        if not name or not name.strip():
            raise ValidationError("Library name cannot be empty")

        library_id = str(uuid.uuid4())
        library = Library(id=library_id, name=name, documents=[])
        logger.info(f"Creating new library: {library}")
        return self.repository.save(library)

    def get_library(self, library_id: str) -> Library:
        """
        Retrieve a library by its ID.

        Args:
            library_id (str): The ID of the library to retrieve.

        Returns:
            Library: The retrieved library.

        Raises:
            NotFoundError: If the library is not found.
        """
        library = self.repository.get(library_id)
        if not library:
            logger.error(f"Library not found: {library_id}")
            raise NotFoundError(f"Library with id {library_id} not found")
        return library

    def update_library(self, library: Library) -> Library:
        """
        Update an existing library.

        Args:
            library (Library): The library with updated information.

        Returns:
            Library: The updated library.

        Raises:
            NotFoundError: If the library is not found.
            ValidationError: If the library data is invalid.
        """
        if not library.id or not library.name.strip():
            raise ValidationError("Invalid library data")

        existing_library = self.get_library(library.id)
        existing_library.name = library.name
        logger.info(f"Updating library: {existing_library}")
        return self.repository.save(existing_library)

    def delete_library(self, library_id: str) -> None:
        """
        Delete a library by its ID.

        Args:
            library_id (str): The ID of the library to delete.

        Raises:
            NotFoundError: If the library is not found.
        """
        self.get_library(library_id)  # Ensure library exists
        logger.info(f"Deleting library: {library_id}")
        self.repository.delete(library_id)

    def list_libraries(self) -> List[Library]:
        """
        List all libraries.

        Returns:
            List[Library]: A list of all libraries.
        """
        return self.repository.list()

    def add_document_to_library(self, library_id: str, document: Document) -> Library:
        """
        Add a document to a library.

        Args:
            library_id (str): The ID of the library to add the document to.
            document (Document): The document to add.

        Returns:
            Library: The updated library.

        Raises:
            NotFoundError: If the library is not found.
            ValidationError: If the document is invalid.
        """
        if not document.id:
            raise ValidationError("Invalid document data")

        library = self.get_library(library_id)
        library.documents.append(document)
        logger.info(f"Adding document {document.id} to library {library_id}")
        return self.repository.save(library)

    def remove_document_from_library(self, library_id: str, document_id: str) -> Library:
        """
        Remove a document from a library.

        Args:
            library_id (str): The ID of the library to remove the document from.
            document_id (str): The ID of the document to remove.

        Returns:
            Library: The updated library.

        Raises:
            NotFoundError: If the library or document is not found.
        """
        library = self.get_library(library_id)
        library.documents = [doc for doc in library.documents if doc.id != document_id]
        logger.info(f"Removing document {document_id} from library {library_id}")
        return self.repository.save(library)