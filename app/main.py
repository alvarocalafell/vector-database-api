import logging
from fastapi import FastAPI
from app.core.database import VectorDatabase
from app.api import libraries, documents, search

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
    app.include_router(search.router, prefix="/search", tags=["search"])
    
    logger.debug("App creation completed")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)