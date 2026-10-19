"""
WebMender AI — Repair Agent
Core AI loop: detect failure → inspect page → diff → plan repair → verify
"""

import asyncio
import base64
import json
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.schemas import (
    FailureReport, RepairPlan, RepairCandidate,
    PlaywrightAction, WorkflowStatus
)
from app.services.tinyfish_service import TinyFishService
from app.services.dom_differ import DOMDiffer
from app.services.screenshot_differ import ScreenshotDiffer


class RepairAgent:
    """
    The self-healing core of WebMender AI.

    Pipeline:
      1. Receive failure report from workflow runner
      2. Use TinyFish Browser to re-inspect the live page
      3. Diff current DOM against last-known-good snapshot
      4. Diff screenshots to quantify visual change
      5. Ask LLM to reason about the most likely repair
      6. Generate and rank candidate locators
      7. Return a RepairPlan for the workflow runner to execute
    """

    def __init__(self):
        self.llm = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.tinyfish = TinyFishService()
        self.dom_differ = DOMDiffer()
        self.screenshot_differ = ScreenshotDiffer()

    async def plan_repair(
        self,
        failure: FailureReport,
        current_dom: str,
        current_screenshot_b64: str,
    ) -> Optional[RepairPlan]:
        """
        Main repair planning entry point.
        Returns a RepairPlan or None if the agent cannot confidently repair.
        """
        # Step 1: Compute DOM diff
        dom_diff = self.dom_differ.diff(
            old_dom=failure.dom_snapshot_before or "",
            new_dom=current_dom,
        )

        # Step 2: Compute screenshot diff score
        diff_score = 0.0
        if failure.screenshot_before:
            diff_score = await self.screenshot_differ.compare(
                before_b64=failure.screenshot_before,
                after_b64=current_screenshot_b64,
            )

        # Step 3: Ask LLM to propose repair candidates
        candidates = await self._ask_llm_for_candidates(
            failure=failure,
            dom_diff=dom_diff,
            diff_score=diff_score,
        )

        if not candidates:
            return None

        # Step 4: Sort by confidence and pick the best
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        best = candidates[0]

        if best.confidence < 0.4:
            # Not confident enough — surface failure instead of guessing
            return None

        return RepairPlan(
            original_action=PlaywrightAction(
                action_type="click",
                selector=failure.selector_used,
            ),
            candidates=candidates,
            selected_candidate=best,
            dom_diff_summary=dom_diff[:500],
            screenshot_diff_score=diff_score,
            llm_explanation=best.reasoning,
        )

    async def _ask_llm_for_candidates(
        self,
        failure: FailureReport,
        dom_diff: str,
        diff_score: float,
    ) -> list[RepairCandidate]:
        """Send evidence to the LLM and parse repair candidates."""

        system_prompt = """You are WebMender AI's repair planner.
Given a failed browser automation action and evidence of what changed on the page,
propose the most likely replacement locators ranked by confidence.

Respond ONLY with a JSON array of repair candidates:
[
  {
    "locator_type": "css|xpath|text|aria-label|role",
    "locator_value": "...",
    "confidence": 0.0-1.0,
    "reasoning": "...",
    "evidence": ["..."]
  }
]
"""

        user_prompt = f"""FAILED ACTION:
- Action type: {failure.error_message.split(':')[0] if ':' in failure.error_message else 'click'}
- Original selector: {failure.selector_used}
- Error: {failure.error_message}

DOM DIFF SUMMARY (first 800 chars):
{dom_diff[:800]}

SCREENSHOT CHANGE SCORE: {diff_score:.3f} (0=identical, 1=completely different)

Propose up to 5 repair candidates for the failed selector.
"""

        try:
            response = await self.llm.chat.completions.create(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)

            candidates_data = data if isinstance(data, list) else data.get("candidates", [])
            return [RepairCandidate(**c) for c in candidates_data]
        except Exception as e:
            print(f"[RepairAgent] LLM call failed: {e}")
            return []
