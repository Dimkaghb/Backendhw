from fastapi import HTTPException
from datetime import datetime, timezone
from ..models.user import UserResponse
from ..config.database import get_database
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = get_database()

    async def get_user_info(self, username: str):
        if self.db.mongodb_connected:
            # Use MongoDB
            user = await self.db.users_collection.find_one({"username": username})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserResponse(
                username=user["username"],
                created_at=user.get("created_at", datetime.now(timezone.utc))
            )
        else:
            # Use in-memory storage
            user = self.db.in_memory_users.get(username)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserResponse(
                username=user["username"],
                created_at=user.get("created_at", datetime.now(timezone.utc))
            )

user_service = UserService()