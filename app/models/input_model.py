from datetime import datetime
import uuid
from pydantic import BaseModel
# Define the input model for the request to generate the reponse
class ContentRequest(BaseModel):
    thread_id: str  # UUID reference to Thread
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.utcnow()
    
class Thread(BaseModel):
    thread_id: str
    user_id: str
    title: str = "New Chat"
    created_at: datetime = datetime.utcnow()
    last_updated: datetime = datetime.utcnow()
    