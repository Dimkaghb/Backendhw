from fastapi import Depends
from ..config.database import get_database
from .security import get_current_user

def get_db():
    return get_database()

def get_authenticated_user(current_user: str = Depends(get_current_user)):
    return current_user