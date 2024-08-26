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
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vector Database API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h1 {
                    font-size: 2.5em;
                    color: #1a1a1a;
                    margin-bottom: 20px;
                }
                h2 {
                    font-size: 1.8em;
                    color: #4a4a4a;
                    margin-top: 30px;
                }
                p {
                    margin-bottom: 20px;
                }
                .highlight {
                    color: #4758FF;
                    font-weight: bold;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin-bottom: 10px;
                }
                a {
                    color: #4758FF;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .cta-button {
                    display: inline-block;
                    background-color: #4758FF;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 20px;
                }
                .cta-button:hover {
                    background-color: #3a46cc;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to the <span class="highlight">Vector Database API</span></h1>
            <p>Augment your applications with powerful vector search capabilities. Automate data operations and make your organization smarter.</p>
            
            <h2>Key Features:</h2>
            <ul>
                <li>🚀 High-performance vector indexing and search</li>
                <li>📚 Efficient document and chunk management</li>
                <li>🔍 Advanced similarity search algorithms</li>
                <li>🔧 Flexible API for seamless integration</li>
            </ul>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/docs">/docs</a> - Interactive API documentation</li>
                <li><a href="/redoc">/redoc</a> - Alternative API documentation</li>
                <li><a href="/api/v1/libraries">/api/v1/libraries</a> - Manage libraries</li>
                <li><a href="/api/v1/documents">/api/v1/documents</a> - Manage documents</li>
                <li><a href="/api/v1/chunks">/api/v1/chunks</a> - Manage chunks</li>
                <li><a href="/api/v1/search">/api/v1/search</a> - Perform vector searches</li>
            </ul>
            
            <a href="/docs" class="cta-button">Get Started</a>
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