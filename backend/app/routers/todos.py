from fastapi import APIRouter, Depends
from typing import List
from ..models.todo import ToDo
from ..services.todo_service import todo_service
from ..core.dependencies import get_authenticated_user

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=List[ToDo])
async def get_todos(current_user: str = Depends(get_authenticated_user)):
    return await todo_service.get_todos()



@router.get("/{todo_id}", response_model=ToDo)
async def get_todo(todo_id: int, current_user: str = Depends(get_authenticated_user)):
    return await todo_service.get_todo(todo_id)

@router.post("/", response_model=ToDo)
async def create_todo(todo: ToDo, current_user: str = Depends(get_authenticated_user)):
    return await todo_service.create_todo(todo)

@router.put("/{todo_id}", response_model=ToDo)
async def update_todo(todo_id: int, updated_todo: ToDo, current_user: str = Depends(get_authenticated_user)):
    return await todo_service.update_todo(todo_id, updated_todo)

@router.delete("/{todo_id}", response_model=ToDo)
async def delete_todo(todo_id: int, current_user: str = Depends(get_authenticated_user)):
    return await todo_service.delete_todo(todo_id)