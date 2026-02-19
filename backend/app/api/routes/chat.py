from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.services.agent_service import agent_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = agent_service.chat(request.message, request.session_id)
        
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id,
            appointment_id=result.get("appointment_id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    try:
        agent_service.clear_session(session_id)
        return {"message": "Session cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))