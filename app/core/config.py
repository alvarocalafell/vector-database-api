from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    INDEXING_ALGORITHM: str = "kdtree"
    ALLOWED_ORIGINS: list = ["http://localhost", "http://localhost:8080"]
    COHERE_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "allow" 

def get_settings() -> Settings:
    return Settings()