"""
WebMender AI — Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    REPAIRING = "repairing"
    REPAIRED = "repaired"
    VERIFIED = "verified"
    UNRECOVERABLE = "unrecoverable"


class PlaywrightAction(BaseModel):
    action_type: str  # click, fill, navigate, wait_for_selector, etc.
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    timeout: int = 30000
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    workflow_id: str
    name: str
    target_url: str
    actions: List[PlaywrightAction]
    expected_output: Optional[Dict[str, Any]] = None
    assertions: List[str] = Field(default_factory=list)


class FailureReport(BaseModel):
    workflow_id: str
    session_id: str
    failed_action_index: int
    error_message: str
    selector_used: Optional[str] = None
    screenshot_before: Optional[str] = None   # base64
    dom_snapshot_before: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RepairCandidate(BaseModel):
    locator_type: str           # css, xpath, text, aria-label, role
    locator_value: str
    confidence: float           # 0.0 – 1.0
    reasoning: str
    evidence: List[str] = Field(default_factory=list)


class RepairPlan(BaseModel):
    original_action: PlaywrightAction
    candidates: List[RepairCandidate]
    selected_candidate: RepairCandidate
    dom_diff_summary: str
    screenshot_diff_score: float
    llm_explanation: str


class RecoveryScorecard(BaseModel):
    workflow_id: str
    session_id: str
    status: WorkflowStatus
    total_actions: int
    failed_at_index: int
    repair_attempts: int
    recovery_latency_ms: int
    locator_changes: List[Dict[str, str]]
    output_correctness: bool
    final_output: Optional[Dict[str, Any]] = None
    repair_plan: Optional[RepairPlan] = None


class RunWorkflowRequest(BaseModel):
    workflow: WorkflowDefinition
    use_tinyfish_browser: bool = True


class RunWorkflowResponse(BaseModel):
    session_id: str
    status: WorkflowStatus
    message: str
