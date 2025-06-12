from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None
    users_collection = None
    tasks_collection = None
    todos_collection = None
    mongodb_connected = False
    
    # In-memory storage for development when MongoDB is not available
    in_memory_users = {}
    in_memory_tasks = {}
    in_memory_todos = []
    task_counter = 1
    todo_counter = 1

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        database.client = AsyncIOMotorClient(
            settings.MONGO_DB_URL, 
            serverSelectionTimeoutMS=5000
        )
        database.db = database.client.todo
        database.users_collection = database.db.users
        database.tasks_collection = database.db.tasks
        database.todos_collection = database.db.todos
        
        # Test the connection
        await database.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        database.mongodb_connected = True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Application will continue with in-memory storage for development")
        database.mongodb_connected = False

async def close_mongo_connection():
    """Close database connection"""
    if database.mongodb_connected and database.client:
        database.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    return database