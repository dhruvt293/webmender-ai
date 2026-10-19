"""
WebMender AI — Repair & Sessions API Routes + Health Check
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import WorkflowStatus

# ─── Repair Router ──────────────────────────────────────────────────────────
router = APIRouter()

_repair_store: dict = {}


@router.get("/{session_id}")
async def get_repair_plan(session_id: str):
    """Retrieve the repair plan generated for a failed workflow session."""
    plan = _repair_store.get(session_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No repair plan found for this session.")
    return plan


@router.post("/{session_id}/accept")
async def accept_repair(session_id: str):
    """Mark a repair plan as accepted and trigger replay."""
    return {"status": "accepted", "session_id": session_id, "message": "Replay initiated."}


@router.post("/{session_id}/reject")
async def reject_repair(session_id: str):
    """Reject a repair plan and escalate as unrecoverable."""
    return {"status": "rejected", "session_id": session_id}
