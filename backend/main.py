from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# MongoDB configuration
MONGO_DB_URL = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_DB_URL)
db = client.todo
users_collection = db.users

# Fix CORS middleware: allow all origins, methods, and headers, but do NOT set allow_credentials=True with allow_origins=["*"]
# See: https://fastapi.tiangolo.com/tutorial/cors/#cors-and-credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=False,  # Must be False if allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Store invalidated tokens (in production, use Redis or similar)
invalidated_tokens = set()

# Security
security = HTTPBearer()

class ToDo(BaseModel):
    id: int | None = None
    name: str
    is_completed: bool

todos = []
current_id = 1

# User model
class User(BaseModel):
    username: str
    password: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials

        if token in invalidated_tokens:
            raise HTTPException(status_code=401, detail="Token has been invalidated")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.post("/signup")
async def signup(user: User):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_dict = user.model_dump()
    await users_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(user: User):
    stored_user = await users_collection.find_one({"username": user.username})
    if not stored_user or stored_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    invalidated_tokens.add(token)
    return {"message": "Successfully logged out"}

@app.get("/todos")
async def get_todos(current_user: str = Depends(get_current_user)):
    return todos

@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int, current_user: str = Depends(get_current_user)):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos")
async def create_todo(todo: ToDo, current_user: str = Depends(get_current_user)):
    global current_id
    todo.id = current_id
    current_id += 1
    todos.append(todo)
    return todo

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, updated_todo: ToDo, current_user: str = Depends(get_current_user)):
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            updated_todo.id = todo_id
            todos[i] = updated_todo
            return updated_todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, current_user: str = Depends(get_current_user)):
    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            return todos.pop(i)
    raise HTTPException(status_code=404, detail="Todo not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



