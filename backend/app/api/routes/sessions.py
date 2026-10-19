from fastapi import APIRouter, HTTPException
from app.models.schemas import WorkflowStatus

router = APIRouter()
_sessions: dict = {}


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Poll for the recovery scorecard of a workflow session."""
    result = _sessions.get(session_id)
    if not result:
        return {"session_id": session_id, "status": WorkflowStatus.RUNNING, "message": "Still processing…"}
    return result
