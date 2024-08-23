from typing import Dict, List
from ....ports.repositories.library_repository import LibraryRepository
from ....core.entities.library import Library

class InMemoryLibraryRepository(LibraryRepository):
    def __init__(self):
        self.libraries: Dict[str, Library] = {}

    def save(self, library: Library) -> Library:
        self.libraries[library.id] = library
        return library

    def get(self, library_id: str) -> Library:
        return self.libraries.get(library_id)

    def delete(self, library_id: str) -> None:
        self.libraries.pop(library_id, None)

    def list(self) -> List[Library]:
        return list(self.libraries.values())