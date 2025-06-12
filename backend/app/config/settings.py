import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB configuration
    MONGO_DB_URL: str = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017")
    
    # JWT configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS configuration
    ALLOWED_ORIGINS: list = ["*"]
    
    # Upload configuration
    UPLOADS_DIR: str = "uploads"
    
    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application configuration
    APP_NAME: str = "Todo Chat Application"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()