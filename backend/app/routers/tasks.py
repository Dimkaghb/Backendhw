from fastapi import APIRouter, Depends
from typing import List
from ..models.task import Task, TaskCreate
from ..services.task_service import task_service
from ..core.dependencies import get_authenticated_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    current_user: str = Depends(get_authenticated_user)
):
    return await task_service.create_task(task, current_user)

@router.get("/", response_model=List[Task])
async def get_tasks(current_user: str = Depends(get_authenticated_user)):
    return await task_service.get_tasks(current_user)