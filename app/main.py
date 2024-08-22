import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .adapters.api.v1.routes import library_routes, document_routes
from .di_container import Container
from .core.exceptions import VectorDBException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create and configure the dependency injection container
container = Container()
# Set a default value for the indexing algorithm
container.config.indexing_algorithm.from_value("kd_tree") # Options are ['linear_search', 'kd_tree']

app = FastAPI(title="Vector Database API")

# Dependency injection
app.container = container

# Wire up the container to the API routes
container.wire(modules=[library_routes, document_routes])

# Include routers
app.include_router(library_routes.router, prefix="/api/v1", tags=["libraries"])
app.include_router(document_routes.router, prefix="/api/v1", tags=["documents"])

@app.exception_handler(VectorDBException)
async def vector_db_exception_handler(request: Request, exc: VectorDBException):
    logger.error(f"VectorDBException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)