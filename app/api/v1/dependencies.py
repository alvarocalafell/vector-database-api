from fastapi import Request
from typing import Callable
from app.core.database import VectorDatabase

def get_vector_db() -> Callable[[Request], VectorDatabase]:
    """
    Dependency function to retrieve the VectorDatabase instance from the FastAPI app state.

    This function is used as a dependency in FastAPI route functions to inject
    the VectorDatabase instance. It ensures that all routes have access to the
    same VectorDatabase instance, which is stored in the app's state.

    Returns:
        Callable[[Request], VectorDatabase]: A callable that takes a FastAPI Request
        object and returns the VectorDatabase instance.

    Usage:
        @app.get("/some-route")
        async def some_route(vector_db: VectorDatabase = Depends(get_vector_db)):
            # Use vector_db here
    """
    def get_db_from_request(request: Request) -> VectorDatabase:
        """
        Retrieves the VectorDatabase instance from the FastAPI app state.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            VectorDatabase: The VectorDatabase instance stored in the app state.

        Raises:
            AttributeError: If the VectorDatabase instance is not found in the app state.
        """
        db = request.app.state.main_app.state.vector_db
        if not isinstance(db, VectorDatabase):
            raise AttributeError("VectorDatabase instance not found in app state")
        return db

    return get_db_from_request