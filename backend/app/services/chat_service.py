from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone
from typing import List
from ..models.chat import ChatMessage, ChatResponse
from ..config.settings import settings
import os
import sys
import logging

# Add the backend directory to the path to import interaction module
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from interaction import A2AInteraction

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            self.a2a_interaction = A2AInteraction()
            logger.info("A2A Interaction initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize A2A Interaction: {e}")
            self.a2a_interaction = None
        
        # Create uploads directory if it doesn't exist
        os.makedirs(settings.UPLOADS_DIR, exist_ok=True)

    async def chat_with_agent(self, chat_message: ChatMessage, username: str) -> ChatResponse:
        """
        Chat endpoint that uses LangChain and LlamaIndex agents with user-specific context
        """
        try:
            if not self.a2a_interaction:
                # Fallback response if agents are not available
                response_text = "I'm sorry, the AI agents are currently unavailable. Please try again later."
            else:
                # Use the A2A interaction to get response from agents with user context
                response_text = self.a2a_interaction.ask(chat_message.message, username)
            
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

    async def get_chat_history(self, username: str):
        """
        Get chat history for the current user
        """
        try:
            if not self.a2a_interaction:
                return {"history": []}
            
            # Return the user-specific conversation history
            return {"history": self.a2a_interaction.get_user_history(username)}
        
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return {"history": []}

    async def clear_chat_history(self, username: str):
        """
        Clear chat history for the current user
        """
        try:
            if self.a2a_interaction:
                self.a2a_interaction.clear_user_history(username)
            
            return {"message": "Chat history cleared successfully"}
        
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
            raise HTTPException(status_code=500, detail="Failed to clear chat history")

    async def upload_file(self, file: UploadFile, username: str):
        """
        Upload a file to the server for the current user
        """
        try:
            # Create user-specific upload directory
            user_upload_dir = os.path.join(settings.UPLOADS_DIR, username)
            os.makedirs(user_upload_dir, exist_ok=True)
            
            # Read file content
            file_content = await file.read()
            file_name = file.filename
            
            # Save file to user-specific directory
            file_path = os.path.join(user_upload_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Rebuild the user's index to include the new file
            if self.a2a_interaction:
                self.a2a_interaction.rebuild_user_index(username)
            
            return {
                "message": "File uploaded successfully",
                "filename": file_name,
                "user": username
            }
        
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")

    async def get_user_files(self, username: str):
        """
        Get list of uploaded files for the current user
        """
        try:
            user_upload_dir = os.path.join(settings.UPLOADS_DIR, username)
            if not os.path.exists(user_upload_dir):
                return {"files": []}
            
            files = []
            for file_name in os.listdir(user_upload_dir):
                file_path = os.path.join(user_upload_dir, file_name)
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    files.append({
                        "name": file_name,
                        "size": file_stats.st_size,
                        "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc)
                    })
            
            return {"files": files}
        
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            return {"files": []}

    async def delete_user_file(self, filename: str, username: str):
        """
        Delete a specific file for the current user
        """
        try:
            user_upload_dir = os.path.join(settings.UPLOADS_DIR, username)
            file_path = os.path.join(user_upload_dir, filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            os.remove(file_path)
            
            # Rebuild the user's index after file deletion
            if self.a2a_interaction:
                self.a2a_interaction.rebuild_user_index(username)
            
            return {"message": f"File {filename} deleted successfully"}
        
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete file")

chat_service = ChatService()