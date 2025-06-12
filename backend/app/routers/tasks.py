from fastapi import APIRouter, Depends
from typing import List
from ..models.task import Task, TaskCreate
from ..services.task_service import task_service
from ..core.dependencies import get_authenticated_user

router = APIRouter(tags=["tasks"])

# Maintain backward compatibility with original endpoints
@router.post("/create_task", response_model=Task)
async def create_task(
    task: TaskCreate,
    current_user: str = Depends(get_authenticated_user)
):
    return await task_service.create_task(task, current_user)

@router.get("/get_tasks", response_model=List[Task])
async def get_tasks(current_user: str = Depends(get_authenticated_user)):
    return await task_service.get_tasks(current_user)

# New RESTful endpoints
@router.post("/tasks", response_model=Task)
async def create_task_rest(
    task: TaskCreate,
    current_user: str = Depends(get_authenticated_user)
):
    return await task_service.create_task(task, current_user)

@router.get("/tasks", response_model=List[Task])
async def get_tasks_rest(current_user: str = Depends(get_authenticated_user)):
    return await task_service.get_tasks(current_user) 