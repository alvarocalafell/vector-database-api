import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.database import VectorDatabase
from app.api import libraries, documents, chunks, search

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    logger.debug("Starting to create the app")
    app = FastAPI(title="Vector Database API")
    
    logger.debug("Initializing the database")
    vector_db = VectorDatabase()
    
    logger.debug("Making vector_db available to all routes")
    app.state.vector_db = vector_db
    
    logger.debug("Including routers")
    app.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
    app.include_router(documents.router, prefix="/documents", tags=["documents"])
    app.include_router(chunks.router, prefix="/chunks", tags=["chunks"])  # Add this line
    app.include_router(search.router, prefix="/search", tags=["search"])
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        logger.debug("Serving root endpoint")
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
                    <li>/search - Perform vector searches</li>
                </ul>
            </body>
        </html>
        """
    
    logger.debug("App creation completed")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.debug("Starting the server")
    uvicorn.run(app, host="0.0.0.0", port=8000)