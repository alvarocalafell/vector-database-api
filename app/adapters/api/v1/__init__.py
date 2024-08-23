from fastapi import FastAPI
from .routes import library_routes

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(library_routes.router, prefix="/api/v1")
    return app
