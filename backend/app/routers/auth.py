from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from ..models.user import User
from ..services.auth_service import auth_service
from ..core.security import security

router = APIRouter(tags=["authentication"])

@router.post("/signup")
async def signup(user: User):
    return await auth_service.signup(user)

@router.post("/login")
async def login(user: User):
    return await auth_service.login(user)   

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return await auth_service.logout(token)