from fastapi import APIRouter, Depends, File, UploadFile
from ..models.chat import ChatMessage, ChatResponse
from ..services.chat_service import chat_service
from ..core.dependencies import get_authenticated_user

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    chat_message: ChatMessage,
    current_user: str = Depends(get_authenticated_user)
):
    return await chat_service.chat_with_agent(chat_message, current_user)

@router.get("/history")
async def get_chat_history(current_user: str = Depends(get_authenticated_user)):
    return await chat_service.get_chat_history(current_user)

@router.post("/clear")
async def clear_chat_history(current_user: str = Depends(get_authenticated_user)):
    return await chat_service.clear_chat_history(current_user)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_authenticated_user)
):
    return await chat_service.upload_file(file, current_user)

@router.get("/files")
async def get_user_files(current_user: str = Depends(get_authenticated_user)):
    return await chat_service.get_user_files(current_user)

@router.delete("/files/{filename}")
async def delete_user_file(
    filename: str,
    current_user: str = Depends(get_authenticated_user)
):
    return await chat_service.delete_user_file(filename, current_user)