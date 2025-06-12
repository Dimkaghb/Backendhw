from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config.settings import settings
from .config.database import connect_to_mongo, close_mongo_connection
from .utils.logger import logger

# Import routers
from .routers import auth, users, tasks, todos, chat

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    logger.info("Application shutdown complete")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(todos.router)
app.include_router(chat.router)

# Legacy endpoints for backward compatibility
@app.post("/signup")
async def signup_legacy(user_data: dict):
    from .models.user import User
    from .services.auth_service import auth_service
    user = User(**user_data)
    return await auth_service.signup(user)

@app.post("/login")
async def login_legacy(user_data: dict):
    from .models.user import User
    from .services.auth_service import auth_service
    user = User(**user_data)
    return await auth_service.login(user)

@app.post("/logout")
async def logout_legacy():
    from fastapi import Depends
    from fastapi.security import HTTPAuthorizationCredentials
    from .core.security import security
    from .services.auth_service import auth_service
    
    async def _logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        return await auth_service.logout(token)
    
    return await _logout()

@app.get("/me")
async def get_me_legacy():
    from fastapi import Depends
    from .core.dependencies import get_authenticated_user
    from .services.user_service import user_service
    
    async def _get_me(current_user: str = Depends(get_authenticated_user)):
        return await user_service.get_user_info(current_user)
    
    return await _get_me()

@app.post("/create_task")
async def create_task_legacy(task_data: dict):
    from fastapi import Depends
    from .models.task import TaskCreate
    from .services.task_service import task_service
    from .core.dependencies import get_authenticated_user
    
    async def _create_task(current_user: str = Depends(get_authenticated_user)):
        task = TaskCreate(**task_data)
        return await task_service.create_task(task, current_user)
    
    return await _create_task()

@app.get("/get_tasks")
async def get_tasks_legacy():
    from fastapi import Depends
    from .services.task_service import task_service
    from .core.dependencies import get_authenticated_user
    
    async def _get_tasks(current_user: str = Depends(get_authenticated_user)):
        return await task_service.get_tasks(current_user)
    
    return await _get_tasks()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)