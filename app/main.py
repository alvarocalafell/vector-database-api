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
    logger.info("Starting to create the app")
    
    settings = get_settings()
    
    app = FastAPI(
        title="Vector Database API",
        description="API for managing and searching vector embeddings",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info(f"Initializing VectorDatabase with {settings.INDEXING_ALGORITHM} algorithm")
    vector_db = VectorDatabase(indexing_algorithm=settings.INDEXING_ALGORITHM)
    app.state.vector_db = vector_db

    # Include v1 routers directly in the main app
    app.include_router(libraries.router, prefix="/api/v1/libraries", tags=["libraries"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(chunks.router, prefix="/api/v1/chunks", tags=["chunks"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
    
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
                    <li>/api/v1/libraries - Manage libraries</li>
                    <li>/api/v1/documents - Manage documents</li>
                    <li>/api/v1/chunks - Manage chunks</li>
                    <li>/api/v1/search - Perform vector searches</li>
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