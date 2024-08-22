from typing import Dict
from ....ports.repositories.library_repository import LibraryRepository
from ....core.entities.library import Library

class LibraryRepositoryInMemory(LibraryRepository):
    def __init__(self):
        self.libraries: Dict[str, Library] = {}

    def create(self, library: Library) -> Library:
        self.libraries[library.id] = library
        return library

    def get(self, library_id: str) -> Library:
        return self.libraries.get(library_id)

    def update(self, library: Library) -> Library:
        if library.id in self.libraries:
            self.libraries[library.id] = library
            return library
        return None

    def delete(self, library_id: str):
        self.libraries.pop(library_id, None)