from dependency_injector import containers, providers
from .core.services.indexing_service import IndexingService, LinearSearch, KDTree
from .core.services.library_service import LibraryService
from .adapters.repositories.in_memory.chunk_repository_in_memory import ChunkRepositoryInMemory
from .adapters.repositories.in_memory.document_repository_in_memory import DocumentRepositoryInMemory
from .adapters.repositories.in_memory.library_repository_in_memory import LibraryRepositoryInMemory

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    chunk_repository = providers.Singleton(ChunkRepositoryInMemory)
    document_repository = providers.Singleton(DocumentRepositoryInMemory)
    library_repository = providers.Singleton(LibraryRepositoryInMemory)

    indexing_algorithm = providers.Selector(
        config.indexing_algorithm,
        linear_search=providers.Factory(LinearSearch),
        kd_tree=providers.Factory(KDTree),
    )

    indexing_service = providers.Factory(
        IndexingService,
        algorithm=indexing_algorithm,
    )

    library_service = providers.Factory(
        LibraryService,
        library_repo=library_repository,
        document_repo=document_repository,
        chunk_repo=chunk_repository,
        indexing_service=indexing_service,
    )