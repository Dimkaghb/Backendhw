from fastapi import HTTPException
from datetime import datetime, timezone
from typing import List
from ..models.task import Task, TaskCreate
from ..config.database import get_database
import logging

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self):
        self.db = get_database()

    async def create_task(self, task: TaskCreate, username: str):
        if self.db.mongodb_connected:
            # Use MongoDB
            user = await self.db.users_collection.find_one({"username": username})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Create task document
            task_dict = task.model_dump()
            task_dict.update({
                "user_id": str(user["_id"]),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            
            # Insert task
            result = await self.db.tasks_collection.insert_one(task_dict)
            task_dict["id"] = str(result.inserted_id)
            
            return Task(**task_dict)
        else:
            # Use in-memory storage
            user = self.db.in_memory_users.get(username)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Create task
            task_dict = task.model_dump()
            task_dict.update({
                "id": str(self.db.task_counter),
                "user_id": username,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            
            if username not in self.db.in_memory_tasks:
                self.db.in_memory_tasks[username] = []
            
            self.db.in_memory_tasks[username].append(task_dict)
            self.db.task_counter += 1
            
            return Task(**task_dict)

    async def get_tasks(self, username: str) -> List[Task]:
        if self.db.mongodb_connected:
            # Use MongoDB
            user = await self.db.users_collection.find_one({"username": username})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get all tasks for the user
            tasks = []
            async for task in self.db.tasks_collection.find({"user_id": str(user["_id"])}):
                task["id"] = str(task.pop("_id"))
                tasks.append(Task(**task))
            
            return tasks
        else:
            # Use in-memory storage
            user = self.db.in_memory_users.get(username)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_tasks = self.db.in_memory_tasks.get(username, [])
            return [Task(**task) for task in user_tasks]

task_service = TaskService()