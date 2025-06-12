from fastapi import APIRouter, Depends
from ..models.user import UserResponse
from ..services.user_service import user_service
from ..core.dependencies import get_authenticated_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: str = Depends(get_authenticated_user)):
    return await user_service.get_user_info(current_user)