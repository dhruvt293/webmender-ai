"""
WebMender AI — Workflow API Routes
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import RunWorkflowRequest, RunWorkflowResponse, WorkflowStatus
from app.services.workflow_runner import WorkflowRunner
import uuid

router = APIRouter()
_active_scorecards: dict = {}   # session_id -> RecoveryScorecard


@router.post("/run", response_model=RunWorkflowResponse)
async def run_workflow(request: RunWorkflowRequest, background_tasks: BackgroundTasks):
    """
    Start a workflow run. The workflow executes in the background.
    Poll /sessions/{session_id} for the result.
    """
    session_id = str(uuid.uuid4())
    runner = WorkflowRunner()

    async def _run():
        scorecard = await runner.run(
            workflow=request.workflow,
            use_tinyfish=request.use_tinyfish_browser,
        )
        _active_scorecards[session_id] = scorecard

    background_tasks.add_task(_run)

    return RunWorkflowResponse(
        session_id=session_id,
        status=WorkflowStatus.RUNNING,
        message="Workflow started. Poll /api/v1/sessions/{session_id} for results.",
    )


@router.get("/definitions")
async def list_workflow_definitions():
    """Return example workflow definitions for the demo."""
    return {
        "workflows": [
            {
                "workflow_id": "demo-spec-scraper",
                "name": "Product Specification Scraper",
                "description": "Scrapes product specs by clicking the Specifications tab",
                "target_url": "http://localhost:8080/version_a/",
            },
            {
                "workflow_id": "demo-login-flow",
                "name": "Login Form Automation",
                "description": "Fills username/password and submits the login form",
                "target_url": "http://localhost:8080/version_a/login",
            },
        ]
    }
