from fastapi import HTTPException
from typing import List
from ..models.todo import ToDo
import logging

logger = logging.getLogger(__name__)

class TodoService:
    def __init__(self):
        self.todos = []
        self.current_id = 1

    def get_todos(self) -> List[ToDo]:
        return self.todos

    def get_todo(self, todo_id: int) -> ToDo:
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        raise HTTPException(status_code=404, detail="Todo not found")

    def create_todo(self, todo: ToDo) -> ToDo:
        todo.id = self.current_id
        self.current_id += 1
        self.todos.append(todo)
        return todo

    def update_todo(self, todo_id: int, updated_todo: ToDo) -> ToDo:
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                updated_todo.id = todo_id
                self.todos[i] = updated_todo
                return updated_todo
        raise HTTPException(status_code=404, detail="Todo not found")

    def delete_todo(self, todo_id: int) -> ToDo:
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                return self.todos.pop(i)
        raise HTTPException(status_code=404, detail="Todo not found")

todo_service = TodoService()