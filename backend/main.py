from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from dotenv import load_dotenv

# Import structured app components
from app.config.database import connect_to_mongo, close_mongo_connection
from app.config.settings import settings
from app.utils.logger import logger

# Import routers
from app.routers import auth, users, todos, tasks, chat

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Todo Chat Application",
    description="A todo application with AI chat functionality",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    logger.info("Application shutdown complete")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(tasks.router)
app.include_router(chat.router)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Todo Chat Application API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
