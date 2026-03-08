from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Groq Configuration
    GROQ_API_KEY: str
    
    # Paths
    UPLOAD_DIR: str = "uploads"
    VECTOR_DB_PATH: str = "vector_db"
    
    # Text Splitting Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Model Configuration
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a single instance to use throughout the app
settings = Settings()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.VECTOR_DB_PATH).mkdir(exist_ok=True)
