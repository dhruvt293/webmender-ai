"""
WebMender AI — TinyFish Service
Wraps TinyFish Browser, Web Agent, Search, and Fetch APIs.
"""

import httpx
import json
from typing import Optional, AsyncGenerator
from app.core.config import settings


class TinyFishService:
    """
    Interface to all four TinyFish capabilities:
      - Browser  : cloud-browser via Playwright/CDP
      - Web Agent: goal-directed SSE automation
      - Search   : live web search for documentation discovery
      - Fetch    : clean content extraction from URLs
    """

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.TINYFISH_API_KEY}",
            "Content-Type": "application/json",
        }

    # ─────────────────────────────────────────────
    # Browser API — returns CDP / Playwright session
    # ─────────────────────────────────────────────
    async def create_browser_session(self) -> dict:
        """Spin up a TinyFish cloud-browser session."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.TINYFISH_BROWSER_ENDPOINT}/sessions",
                headers=self.headers,
                json={"headless": False, "record_video": True},
            )
            resp.raise_for_status()
            return resp.json()

    async def take_screenshot(self, session_id: str) -> str:
        """Capture a screenshot from a live TinyFish browser session (base64 PNG)."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{settings.TINYFISH_BROWSER_ENDPOINT}/sessions/{session_id}/screenshot",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json().get("screenshot_b64", "")

    async def get_dom_snapshot(self, session_id: str) -> str:
        """Retrieve full DOM snapshot from the live TinyFish browser session."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{settings.TINYFISH_BROWSER_ENDPOINT}/sessions/{session_id}/dom",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json().get("dom", "")

    async def close_browser_session(self, session_id: str) -> None:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.delete(
                f"{settings.TINYFISH_BROWSER_ENDPOINT}/sessions/{session_id}",
                headers=self.headers,
            )

    # ─────────────────────────────────────────────
    # Web Agent API — goal-directed SSE exploration
    # ─────────────────────────────────────────────
    async def run_web_agent(
        self,
        goal: str,
        url: str,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Stream SSE events from the TinyFish Web Agent.
        Used to explore a broken page and discover alternative interaction paths.
        """
        payload = {
            "goal": goal,
            "start_url": url,
            "stream": True,
        }
        if session_id:
            payload["session_id"] = session_id

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                settings.TINYFISH_AGENT_ENDPOINT,
                headers={**self.headers, "Accept": "text/event-stream"},
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        raw = line[6:]
                        if raw.strip() == "[DONE]":
                            break
                        try:
                            yield json.loads(raw)
                        except json.JSONDecodeError:
                            continue

    # ─────────────────────────────────────────────
    # Search API — live web search (optional)
    # ─────────────────────────────────────────────
    async def search(self, query: str, num_results: int = 5) -> list[dict]:
        """Retrieve structured search results for documentation or page discovery."""
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                settings.TINYFISH_SEARCH_ENDPOINT,
                headers=self.headers,
                json={"query": query, "num_results": num_results},
            )
            resp.raise_for_status()
            return resp.json().get("results", [])

    # ─────────────────────────────────────────────
    # Fetch API — clean content extraction
    # ─────────────────────────────────────────────
    async def fetch_page(self, url: str, format: str = "markdown") -> str:
        """Extract clean content from a URL in AI-ready format."""
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                settings.TINYFISH_FETCH_ENDPOINT,
                headers=self.headers,
                json={"url": url, "format": format},
            )
            resp.raise_for_status()
            return resp.json().get("content", "")
