import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import VectorDatabase
from app.api.v1 import libraries, documents, chunks, search
from app.core.exceptions import VectorDatabaseException
from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    logger.info("Starting to create the app")
    
    # Load configuration
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="Vector Database API",
        description="API for managing and searching vector embeddings",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
        {"name": "libraries", "description": "Operations with libraries"},
        {"name": "documents", "description": "Operations with documents"},
        {"name": "chunks", "description": "Operations with chunks"},
        {"name": "search", "description": "Search operations"},
    ]
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize VectorDatabase
    logger.info(f"Initializing VectorDatabase with {settings.INDEXING_ALGORITHM} algorithm")
    vector_db = VectorDatabase(indexing_algorithm=settings.INDEXING_ALGORITHM)
    app.state.vector_db = vector_db
    
    # API v1
    v1 = FastAPI(openapi_prefix="/api/v1")
    v1.state.main_app = app  # Store reference to main app
    v1.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
    v1.include_router(documents.router, prefix="/documents", tags=["documents"])
    v1.include_router(chunks.router, prefix="/chunks", tags=["chunks"])
    v1.include_router(search.router, prefix="/search", tags=["search"])

    app.mount("/api/v1", v1)
    
    # For future versions:
    # v2 = FastAPI(openapi_prefix="/api/v2")
    # app.mount("/api/v2", v2)
    
    # # Include routers
    # logger.info("Including API routers")
    # app.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
    # app.include_router(documents.router, prefix="/documents", tags=["documents"])
    # app.include_router(chunks.router, prefix="/chunks", tags=["chunks"])
    # app.include_router(search.router, prefix="/search", tags=["search"])
    
    # Add exception handlers
    @app.exception_handler(VectorDatabaseException)
    async def vector_database_exception_handler(request: Request, exc: VectorDatabaseException):
        logger.error(f"VectorDatabaseException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )
    
    # Add root endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root():
        logger.info("Serving root endpoint")
        return """
        <html>
            <head>
                <title>Vector Database API</title>
            </head>
            <body>
                <h1>Welcome to the Vector Database API</h1>
                <p>This API provides functionality for managing and searching vector embeddings.</p>
                <h2>Available Endpoints:</h2>
                <ul>
                    <li><a href="/docs">/docs</a> - Interactive API documentation</li>
                    <li><a href="/redoc">/redoc</a> - Alternative API documentation</li>
                    <li>/libraries - Manage libraries</li>
                    <li>/documents - Manage documents</li>
                    <li>/chunks - Manage chunks</li>
                    <li>/search - Perform vector searches</li>
                </ul>
            </body>
        </html>
        """
    
    logger.info("App creation completed")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)