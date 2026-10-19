"""
WebMender AI — Demo Workflow Script
Demonstrates the full self-healing cycle on the controlled demo pages.

Run: python demo/workflows/demo_spec_scraper.py
"""

import asyncio
import json

# Demo workflow: click "Specifications" and extract table
WORKFLOW_VERSION_A = {
    "workflow_id": "demo-spec-scraper",
    "name": "Product Specification Scraper",
    "target_url": "http://localhost:8080/version_a/index.html",
    "actions": [
        {"action_type": "navigate", "url": "http://localhost:8080/version_a/index.html"},
        {"action_type": "wait_for_selector", "selector": "#btn-specifications", "timeout": 5000},
        {"action_type": "click", "selector": "#btn-specifications"},
        {"action_type": "wait_for_selector", "selector": "#spec-section", "timeout": 5000},
    ],
    "expected_output": {"table_visible": True},
    "assertions": ["#spec-section is visible"],
}

# Same workflow run against Version B — the selector #btn-specifications no longer exists
WORKFLOW_VERSION_B = {
    **WORKFLOW_VERSION_A,
    "target_url": "http://localhost:8080/version_b/index.html",
    "actions": [
        {"action_type": "navigate", "url": "http://localhost:8080/version_b/index.html"},
        {"action_type": "wait_for_selector", "selector": "#btn-specifications", "timeout": 5000},
        {"action_type": "click", "selector": "#btn-specifications"},   # ← WILL FAIL
        {"action_type": "wait_for_selector", "selector": "#spec-section", "timeout": 5000},
    ],
}

import httpx


async def run_demo():
    base = "http://localhost:8000/api/v1"

    print("=" * 60)
    print("  WebMender AI — Self-Healing Demo")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: Run against Version A (should succeed)
        print("\n[1/3] Running workflow against Version A (original page)…")
        r = await client.post(f"{base}/workflows/run", json={
            "workflow": WORKFLOW_VERSION_A,
            "use_tinyfish_browser": False,
        })
        result = r.json()
        print(f"      Session: {result['session_id']}")
        print(f"      Status:  {result['status']}")

        # Step 2: Run against Version B (will fail → trigger repair)
        print("\n[2/3] Running workflow against Version B (modified page — expect failure)…")
        r2 = await client.post(f"{base}/workflows/run", json={
            "workflow": WORKFLOW_VERSION_B,
            "use_tinyfish_browser": True,
        })
        r2_json = r2.json()
        session_id = r2_json["session_id"]
        print(f"      Session: {session_id}")
        print(f"      Status:  {r2_json['status']}")

        # Step 3: Poll for scorecard
        print("\n[3/3] Polling for recovery scorecard…")
        for _ in range(20):
            await asyncio.sleep(3)
            poll = await client.get(f"{base}/sessions/{session_id}")
            data = poll.json()
            status = data.get("status", "running")
            if status not in ("running", "pending"):
                print(f"\n✅ Final Status: {status}")
                print(json.dumps(data, indent=2))
                break
            print(f"      … still {status}")


if __name__ == "__main__":
    asyncio.run(run_demo())
