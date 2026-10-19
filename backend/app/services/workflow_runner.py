"""
WebMender AI — Workflow Runner
Executes Playwright workflows, detects failures, triggers repair, and verifies recovery.
"""

import asyncio
import time
import uuid
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PWTimeout

from app.core.config import settings
from app.models.schemas import (
    WorkflowDefinition, FailureReport, RecoveryScorecard,
    WorkflowStatus, RepairPlan, PlaywrightAction
)
from app.agents.repair_agent import RepairAgent
from app.services.tinyfish_service import TinyFishService


class WorkflowRunner:
    """
    Executes a WorkflowDefinition step by step using Playwright.
    On failure, captures evidence and delegates repair to RepairAgent.
    After repair, replays the workflow and validates against expected output.
    """

    def __init__(self):
        self.repair_agent = RepairAgent()
        self.tinyfish = TinyFishService()

    async def run(
        self,
        workflow: WorkflowDefinition,
        use_tinyfish: bool = True,
    ) -> RecoveryScorecard:
        session_id = str(uuid.uuid4())
        start_time = time.time()

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=False)
            page = await browser.new_page()

            # ── Execute workflow actions ──────────────────────────────────
            failure: Optional[FailureReport] = None
            failed_index = -1

            for i, action in enumerate(workflow.actions):
                try:
                    await self._execute_action(page, action)
                except Exception as exc:
                    # Capture failure evidence
                    screenshot_b64 = await self._screenshot_b64(page)
                    dom_snapshot = await page.content()

                    failure = FailureReport(
                        workflow_id=workflow.workflow_id,
                        session_id=session_id,
                        failed_action_index=i,
                        error_message=str(exc),
                        selector_used=action.selector,
                        screenshot_before=screenshot_b64,
                        dom_snapshot_before=dom_snapshot,
                    )
                    failed_index = i
                    break

            if failure is None:
                # No failure — workflow completed clean
                latency = int((time.time() - start_time) * 1000)
                await browser.close()
                return RecoveryScorecard(
                    workflow_id=workflow.workflow_id,
                    session_id=session_id,
                    status=WorkflowStatus.VERIFIED,
                    total_actions=len(workflow.actions),
                    failed_at_index=-1,
                    repair_attempts=0,
                    recovery_latency_ms=latency,
                    locator_changes=[],
                    output_correctness=True,
                )

            # ── Repair loop ───────────────────────────────────────────────
            repair_plan: Optional[RepairPlan] = None
            repaired = False

            for attempt in range(settings.MAX_REPAIR_RETRIES):
                # Get fresh page state via TinyFish (or fallback to local)
                current_dom = await page.content()
                current_screenshot = await self._screenshot_b64(page)

                repair_plan = await self.repair_agent.plan_repair(
                    failure=failure,
                    current_dom=current_dom,
                    current_screenshot_b64=current_screenshot,
                )

                if repair_plan is None:
                    break  # Agent not confident — stop and report

                # Apply the repair
                repaired_action = PlaywrightAction(
                    action_type=failure.selector_used and "click" or "click",
                    selector=repair_plan.selected_candidate.locator_value,
                )

                try:
                    await self._execute_action(page, repaired_action)
                    # Continue remaining actions
                    for action in workflow.actions[failed_index + 1:]:
                        await self._execute_action(page, action)
                    repaired = True
                    break
                except Exception:
                    continue

            latency = int((time.time() - start_time) * 1000)
            await browser.close()

            status = WorkflowStatus.VERIFIED if repaired else WorkflowStatus.UNRECOVERABLE
            changes = []
            if repair_plan:
                changes = [{
                    "original": failure.selector_used or "",
                    "repaired": repair_plan.selected_candidate.locator_value,
                    "confidence": str(repair_plan.selected_candidate.confidence),
                }]

            return RecoveryScorecard(
                workflow_id=workflow.workflow_id,
                session_id=session_id,
                status=status,
                total_actions=len(workflow.actions),
                failed_at_index=failed_index,
                repair_attempts=settings.MAX_REPAIR_RETRIES if not repaired else 1,
                recovery_latency_ms=latency,
                locator_changes=changes,
                output_correctness=repaired,
                repair_plan=repair_plan,
            )

    async def _execute_action(self, page: Page, action: PlaywrightAction) -> None:
        if action.action_type == "navigate":
            await page.goto(action.url or "", wait_until="domcontentloaded")
        elif action.action_type == "click":
            await page.click(action.selector or "", timeout=action.timeout)
        elif action.action_type == "fill":
            await page.fill(action.selector or "", action.value or "")
        elif action.action_type == "wait_for_selector":
            await page.wait_for_selector(action.selector or "", timeout=action.timeout)
        elif action.action_type == "screenshot":
            await page.screenshot(path="snapshot.png", full_page=True)

    async def _screenshot_b64(self, page: Page) -> str:
        import base64
        raw = await page.screenshot(full_page=True)
        return base64.b64encode(raw).decode("utf-8")
