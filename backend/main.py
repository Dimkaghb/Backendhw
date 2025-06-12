from fastapi import FastAPI, HTTPException, Depends, File, UploadFile   
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from passlib.context import CryptContext
import os
import logging

# Import the interaction module
from interaction import A2AInteraction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# MongoDB configuration
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
if not MONGO_DB_URL:
    logger.warning("MONGO_DB_URL environment variable is not set, using default local MongoDB")
    MONGO_DB_URL = "mongodb://localhost:27017"

# Create MongoDB client with proper async configuration
client = AsyncIOMotorClient(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
db = client.todo
users_collection = db.users
tasks_collection = db.tasks

# Global variable to track MongoDB connection status
mongodb_connected = False

# In-memory storage for development when MongoDB is not available
in_memory_users = {}
in_memory_tasks = {}
task_counter = 1

# Test MongoDB connection on startup
@app.on_event("startup")
async def startup_event():
    global mongodb_connected
    try:
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        mongodb_connected = True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Application will continue with in-memory storage for development")
        mongodb_connected = False

@app.on_event("shutdown")
async def shutdown_event():
    if mongodb_connected:
        client.close()
        logger.info("MongoDB connection closed")

# CORS middleware: allow requests from the frontend origin
# This fixes the CORS error for 'http://localhost:5173'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only allow your frontend origin
    allow_credentials=True,                   # Credentials (cookies, auth headers) allowed
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

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

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

# Models
class TaskBase(BaseModel):
    title: str
    description: str
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    username: str
    created_at: datetime

# Chatbot models
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime

# Initialize the A2A interaction
try:
    a2a_interaction = A2AInteraction()
    logger.info("A2A Interaction initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize A2A Interaction: {e}")
    a2a_interaction = None

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
    if mongodb_connected:
        # Use MongoDB
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Hash the password before storing
        hashed_password = get_password_hash(user.password)
        user_dict = user.model_dump()
        user_dict["password"] = hashed_password
        user_dict["created_at"] = datetime.now(timezone.utc)
        
        await users_collection.insert_one(user_dict)
    else:
        # Use in-memory storage
        if user.username in in_memory_users:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Hash the password before storing
        hashed_password = get_password_hash(user.password)
        in_memory_users[user.username] = {
            "username": user.username,
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc)
        }
    
    return {"message": "User created successfully"}

@app.post("/login")
async def login(user: User):
    if mongodb_connected:
        # Use MongoDB
        stored_user = await users_collection.find_one({"username": user.username})
        if not stored_user or not verify_password(user.password, stored_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        # Use in-memory storage
        stored_user = in_memory_users.get(user.username)
        if not stored_user or not verify_password(user.password, stored_user["password"]):
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

@app.get("/me")
async def get_user_info(current_user: str = Depends(get_current_user)):
    if mongodb_connected:
        # Use MongoDB
        user = await users_collection.find_one({"username": current_user})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            username=user["username"],
            created_at=user.get("created_at", datetime.now(timezone.utc))
        )
    else:
        # Use in-memory storage
        user = in_memory_users.get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            username=user["username"],
            created_at=user.get("created_at", datetime.now(timezone.utc))
        )

@app.post("/create_task")
async def create_task(
    task: TaskCreate,
    current_user: str = Depends(get_current_user)
):
    global task_counter
    
    if mongodb_connected:
        # Use MongoDB
        user = await users_collection.find_one({"username": current_user})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create task document
        task_dict = task.model_dump()
        task_dict.update({
            "user_id": str(user["_id"]),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        
        # Insert task
        result = await tasks_collection.insert_one(task_dict)
        task_dict["id"] = str(result.inserted_id)
        
        return Task(**task_dict)
    else:
        # Use in-memory storage
        user = in_memory_users.get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create task
        task_dict = task.model_dump()
        task_dict.update({
            "id": str(task_counter),
            "user_id": current_user,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        
        if current_user not in in_memory_tasks:
            in_memory_tasks[current_user] = []
        
        in_memory_tasks[current_user].append(task_dict)
        task_counter += 1
        
        return Task(**task_dict)

@app.get("/get_tasks", response_model=List[Task])
async def get_tasks(current_user: str = Depends(get_current_user)):
    if mongodb_connected:
        # Use MongoDB
        user = await users_collection.find_one({"username": current_user})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all tasks for the user
        tasks = []
        async for task in tasks_collection.find({"user_id": str(user["_id"])}):
            task["id"] = str(task.pop("_id"))
            tasks.append(Task(**task))
        
        return tasks
    else:
        # Use in-memory storage
        user = in_memory_users.get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_tasks = in_memory_tasks.get(current_user, [])
        return [Task(**task) for task in user_tasks]

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    chat_message: ChatMessage,
    current_user: str = Depends(get_current_user)
):
    """
    Chat endpoint that uses LangChain and LlamaIndex agents
    """
    try:
        if not a2a_interaction:
            # Fallback response if agents are not available
            response_text = "I'm sorry, the AI agents are currently unavailable. Please try again later."
        else:
            # Use the A2A interaction to get response from agents
            response_text = a2a_interaction.ask(chat_message.message)
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now(timezone.utc)
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        # Return a friendly error message
        return ChatResponse(
            response="I encountered an error while processing your message. Please try again.",
            timestamp=datetime.now(timezone.utc)
        )

@app.get("/chat/history")
async def get_chat_history(current_user: str = Depends(get_current_user)):
    """
    Get chat history for the current user
    """
    try:
        if not a2a_interaction:
            return {"history": []}
        
        # Return the conversation history
        return {"history": a2a_interaction.history}
    
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return {"history": []}

@app.post("/chat/clear")
async def clear_chat_history(current_user: str = Depends(get_current_user)):
    """
    Clear chat history for the current user
    """
    try:
        if a2a_interaction:
            a2a_interaction.history = []
        
        return {"message": "Chat history cleared successfully"}
    
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")
    
@app.post("/chat/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the server
    """
    db_file = await file.read()
    file_name = file.filename
    file_path = f"uploads/{file_name}"
    with open(file_path, "wb") as f:
        f.write(db_file)
    return {"message": "File uploaded successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
