import os
import asyncio
from datetime import datetime, timezone
from celery import Celery
from redis import Redis
from motor.motor_asyncio import AsyncIOMotorClient

# Get Redis URL from environment variable
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
MONGO_DB_URL = os.getenv('MONGO_DB_URL', 'mongodb://localhost:27017/todo')

# Create Celery instance
celery_app = Celery(
    'todo_app',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_app']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)

async def create_todo_in_database():
    """Create a todo item in MongoDB database"""
    client = None
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
        db = client.todo
        
        # Test connection
        await client.admin.command('ping')
        
        # Get a user to assign the todo to (or create system user)
        users_collection = db.users
        users = await users_collection.find().to_list(length=None)
        
        if not users:
            # Create a system user if no users exist
            system_user = {
                "username": "system",
                "password": "system_generated",
                "created_at": datetime.now(timezone.utc)
            }
            result = await users_collection.insert_one(system_user)
            user_id = str(result.inserted_id)
        else:
            # Use the first available user
            user_id = str(users[0]["_id"])
        
        # Create todo document
        todo_doc = {
            "name": "Redis",
            "is_completed": False,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "celery_redis_task"
        }
        
        # Insert into todos collection (using the same structure as the app)
        # Check if we should use 'todos' or 'tasks' collection
        todos_collection = db.todos
        result = await todos_collection.insert_one(todo_doc)
        
        print(f"✅ Created Redis todo with ID: {result.inserted_id}")
        
        # Also store in Redis for caching
        try:
            redis_client = Redis.from_url(REDIS_URL)
            redis_client.incr('redis_todos_created')
            total_created = redis_client.get('redis_todos_created')
            print(f"📊 Total Redis todos created: {total_created.decode() if total_created else 0}")
        except Exception as redis_error:
            print(f"⚠️ Redis connection failed: {redis_error}")
            # Continue without Redis stats
        
        return {
            "id": str(result.inserted_id),
            "name": "Redis",
            "is_completed": False,
            "user_id": user_id,
            "created_at": todo_doc["created_at"].isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error creating Redis todo: {str(e)}")
        raise e
    finally:
        if client:
            client.close()

@celery_app.task
def create_redis_todo_task():
    """Celery task that creates a todo with text 'Redis' every 10 seconds"""
    try:
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(create_todo_in_database())
            print(f"🎉 Successfully created Redis todo: {result}")
            return result
        finally:
            loop.close()
            
    except Exception as e:
        print(f"💥 Redis todo creation task failed: {str(e)}")
        raise e

# Configure periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3600.0, create_redis_todo_task.s(), name='create-redis-todo-every-10-seconds')

if __name__ == '__main__':
    celery_app.start() 