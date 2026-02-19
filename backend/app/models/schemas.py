from pydantic import BaseModel, EmailStr
from typing import Optional, List

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: str

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    session_id: str
    appointment_id: Optional[int] = None
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str