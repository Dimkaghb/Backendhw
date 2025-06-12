from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from ..models.user import User, UserResponse
from ..core.security import verify_password, get_password_hash, create_access_token, invalidate_token
from ..config.database import get_database
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.db = get_database()

    async def signup(self, user: User):
        if self.db.mongodb_connected:
            # Use MongoDB
            existing_user = await self.db.users_collection.find_one({"username": user.username})
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already registered")
            
            # Hash the password before storing
            hashed_password = get_password_hash(user.password)
            user_dict = user.model_dump()
            user_dict["password"] = hashed_password
            user_dict["created_at"] = datetime.now(timezone.utc)
            
            await self.db.users_collection.insert_one(user_dict)
        else:
            # Use in-memory storage
            if user.username in self.db.in_memory_users:
                raise HTTPException(status_code=400, detail="Username already registered")
            
            # Hash the password before storing
            hashed_password = get_password_hash(user.password)
            self.db.in_memory_users[user.username] = {
                "username": user.username,
                "password": hashed_password,
                "created_at": datetime.now(timezone.utc)
            }
        
        return {"message": "User created successfully"}

    async def login(self, user: User):
        if self.db.mongodb_connected:
            # Use MongoDB
            stored_user = await self.db.users_collection.find_one({"username": user.username})
            if not stored_user or not verify_password(user.password, stored_user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            # Use in-memory storage
            stored_user = self.db.in_memory_users.get(user.username)
            if not stored_user or not verify_password(user.password, stored_user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

    async def logout(self, token: str):
        invalidate_token(token)
        return {"message": "Successfully logged out"}

auth_service = AuthService()