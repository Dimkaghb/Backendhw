import os
import random
from datetime import datetime, timezone
from celery import current_app as celery_app
from celery.utils.log import get_task_logger
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Get logger for this task
logger = get_task_logger(__name__)

# Random todo task ideas
RANDOM_TODO_TASKS = [
    "Buy groceries for the week",
    "Call mom and dad",
    "Schedule dentist appointment",
    "Clean the house",
    "Exercise for 30 minutes",
    "Read a chapter of a book",
    "Water the plants",
    "Organize desk workspace",
    "Plan weekend activities",
    "Update resume",
    "Learn something new online",
    "Cook a healthy meal",
    "Take a walk in the park",
    "Write in journal",
    "Backup computer files",
    "Pay monthly bills",
    "Declutter wardrobe",
    "Call an old friend",
    "Practice a hobby",
    "Plan next vacation",
    "Review monthly budget",
    "Clean out email inbox",
    "Update social media profiles",
    "Research new recipes",
    "Organize photo collection",
    "Schedule car maintenance",
    "Learn a new skill",
    "Write thank you notes",
    "Plan healthy meals for the week",
    "Meditate for 10 minutes",
    "Stretch or do yoga",
    "Listen to a podcast",
    "Watch an educational video",
    "Clean out browser bookmarks",
    "Update password manager",
    "Research investment options",
    "Plan a date night",
    "Organize important documents",
    "Check smoke detector batteries",
    "Research local events"
]

async def get_database_connection():
    """Get MongoDB connection"""
    mongo_url = os.getenv('MONGO_DB_URL', 'mongodb://localhost:27017/todo')
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client.todo
    return client, db

async def create_todo_in_db(todo_name: str):
    """Create a todo in the database"""
    client = None
    try:
        client, db = await get_database_connection()
        
        # Test connection
        await client.admin.command('ping')
        
        # Get users collection to find a user to assign the todo to
        users_collection = db.users
        users = await users_collection.find().to_list(length=None)
        
        if not users:
            logger.warning("No users found in database, creating todo without user assignment")
            user_id = "system"
        else:
            # Pick a random user
            random_user = random.choice(users)
            user_id = str(random_user["_id"])
        
        # Create todo document
        todo_doc = {
            "name": todo_name,
            "is_completed": False,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "celery_auto_task"
        }
        
        # Insert into todos collection
        todos_collection = db.todos
        result = await todos_collection.insert_one(todo_doc)
        
        logger.info(f"Created todo task: '{todo_name}' with ID: {result.inserted_id}")
        
        return {
            "id": str(result.inserted_id),
            "name": todo_name,
            "is_completed": False,
            "user_id": user_id,
            "created_at": todo_doc["created_at"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create todo in database: {str(e)}")
        raise e
    finally:
        if client:
            client.close()

@celery_app.task(bind=True)
def create_random_todo_task(self):
    """
    Celery task that creates a todo with text "redis" every minute
    """
    try:
        # Create todo with "redis" text
        todo_text = "redis"
        
        # Create the todo in database using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(create_todo_in_db(todo_text))
            logger.info(f"Successfully created redis todo: {todo_text}")
            
            return {
                "status": "success",
                "todo": result,
                "task_id": str(self.request.id),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Redis todo creation task failed: {str(e)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task
def create_custom_todo_task(todo_name: str, user_id: str = None):
    """
    Manual task to create a custom todo
    Can be called manually for testing purposes
    """
    try:
        # Create the todo in database using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(create_todo_in_db(todo_name))
            logger.info(f"Successfully created custom todo: {todo_name}")
            
            return {
                "status": "success",
                "todo": result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Custom todo creation task failed: {str(e)}")
        raise e

@celery_app.task
def get_todo_stats():
    """
    Task to get statistics about todos in the database
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def get_stats():
            client = None
            try:
                client, db = await get_database_connection()
                await client.admin.command('ping')
                
                todos_collection = db.todos
                
                # Get total count
                total_todos = await todos_collection.count_documents({})
                
                # Get completed count
                completed_todos = await todos_collection.count_documents({"is_completed": True})
                
                # Get pending count
                pending_todos = total_todos - completed_todos
                
                # Get todos created by celery
                celery_todos = await todos_collection.count_documents({"created_by": "celery_auto_task"})
                
                return {
                    "total_todos": total_todos,
                    "completed_todos": completed_todos,
                    "pending_todos": pending_todos,
                    "celery_created_todos": celery_todos
                }
            finally:
                if client:
                    client.close()
        
        try:
            stats = loop.run_until_complete(get_stats())
            logger.info(f"Todo statistics: {stats}")
            
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Get todo stats task failed: {str(e)}")
        raise e 