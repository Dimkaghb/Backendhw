from fastapi import HTTPException
from typing import List
from datetime import datetime, timezone
from ..models.todo import ToDo
from ..config.database import get_database
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)

class TodoService:
    def __init__(self):
        self.db = get_database()
        # Fallback in-memory storage
        self.todos = []
        self.current_id = 1

    async def get_todos(self) -> List[ToDo]:
        if self.db.mongodb_connected:
            # Use MongoDB
            todos = []
            async for todo in self.db.db.todos.find():
                todo_dict = {
                    "id": str(todo["_id"]),
                    "name": todo["name"],
                    "is_completed": todo["is_completed"]
                }
                todos.append(ToDo(**todo_dict))
            return todos
        else:
            # Use in-memory storage
            return self.todos

    async def get_todo(self, todo_id: int) -> ToDo:
        if self.db.mongodb_connected:
            # Use MongoDB
            try:
                todo = await self.db.db.todos.find_one({"_id": ObjectId(str(todo_id))})
                if not todo:
                    raise HTTPException(status_code=404, detail="Todo not found")
                
                return ToDo(
                    id=str(todo["_id"]),
                    name=todo["name"],
                    is_completed=todo["is_completed"]
                )
            except:
                raise HTTPException(status_code=404, detail="Todo not found")
        else:
            # Use in-memory storage
            for todo in self.todos:
                if todo.id == todo_id:
                    return todo
            raise HTTPException(status_code=404, detail="Todo not found")

    async def create_todo(self, todo: ToDo) -> ToDo:
        if self.db.mongodb_connected:
            # Use MongoDB
            todo_dict = {
                "name": todo.name,
                "is_completed": todo.is_completed,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await self.db.db.todos.insert_one(todo_dict)
            todo.id = str(result.inserted_id)
            return todo
        else:
            # Use in-memory storage
            todo.id = self.current_id
            self.current_id += 1
            self.todos.append(todo)
            return todo

    async def update_todo(self, todo_id: int, updated_todo: ToDo) -> ToDo:
        if self.db.mongodb_connected:
            # Use MongoDB
            try:
                update_data = {
                    "name": updated_todo.name,
                    "is_completed": updated_todo.is_completed,
                    "updated_at": datetime.now(timezone.utc)
                }
                
                result = await self.db.db.todos.update_one(
                    {"_id": ObjectId(str(todo_id))},
                    {"$set": update_data}
                )
                
                if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail="Todo not found")
                
                updated_todo.id = str(todo_id)
                return updated_todo
            except:
                raise HTTPException(status_code=404, detail="Todo not found")
        else:
            # Use in-memory storage
            for i, todo in enumerate(self.todos):
                if todo.id == todo_id:
                    updated_todo.id = todo_id
                    self.todos[i] = updated_todo
                    return updated_todo
            raise HTTPException(status_code=404, detail="Todo not found")

    async def delete_todo(self, todo_id: int) -> ToDo:
        if self.db.mongodb_connected:
            # Use MongoDB
            try:
                todo = await self.db.db.todos.find_one({"_id": ObjectId(str(todo_id))})
                if not todo:
                    raise HTTPException(status_code=404, detail="Todo not found")
                
                await self.db.db.todos.delete_one({"_id": ObjectId(str(todo_id))})
                
                return ToDo(
                    id=str(todo["_id"]),
                    name=todo["name"],
                    is_completed=todo["is_completed"]
                )
            except:
                raise HTTPException(status_code=404, detail="Todo not found")
        else:
            # Use in-memory storage
            for i, todo in enumerate(self.todos):
                if todo.id == todo_id:
                    return self.todos.pop(i)
            raise HTTPException(status_code=404, detail="Todo not found")

todo_service = TodoService()