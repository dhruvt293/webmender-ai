<div align="center">

# WebMender AI — The Self-Healing Browser Agent

<img src="https://img.shields.io/badge/Track-AI%2FML-6366f1?style=for-the-badge&logo=robot&logoColor=white" />
<img src="https://img.shields.io/badge/TinyFish-Integrated-0ea5e9?style=for-the-badge&logo=fish&logoColor=white" />
<img src="https://img.shields.io/badge/Built%20at-Kritical%20Hacks%202026-f59e0b?style=for-the-badge&logo=lightning&logoColor=white" />
<img src="https://img.shields.io/badge/Stack-Python%20%7C%20FastAPI%20%7C%20React-22c55e?style=for-the-badge" />
<img src="https://img.shields.io/badge/LLM-GPT--4o-a855f7?style=for-the-badge&logo=openai&logoColor=white" />

<br /><br />

> ### *"Websites change. Your AI agent shouldn't break."*

<br />

**WebMender AI** is a reliability layer for browser automation agents.
It detects when a workflow breaks, investigates the live page using TinyFish's cloud browser,
diffs the DOM and screenshots with AI, repairs the broken locator, and verifies the fix —
**all without human intervention.**

</div>

---

## <img src="https://api.iconify.design/lucide:triangle-alert.svg?color=%23f59e0b" width="22" height="22" align="absmiddle" /> &nbsp;The Problem We're Solving

AI agents are increasingly expected to complete real-world tasks on the web: filling forms, collecting data, navigating portals. But the web is a moving target.

```
Day 1:  workflow clicks  →  button[id="btn-specifications"]   WORKS
Day 7:  Same workflow    →  button[id="tech-details-btn"]     FAILS
```

| Traditional Automation | WebMender AI |
|---|---|
| Breaks silently on selector changes | Detects failure instantly |
| Requires manual inspection | Inspects the live page autonomously |
| Engineer must rewrite the selector | LLM proposes and ranks repair candidates |
| No evidence trail | Full DOM diff + screenshot diff + audit log |
| Re-run fails again | Replays and validates the repaired workflow |

---

## <img src="https://api.iconify.design/lucide:boxes.svg?color=%236366f1" width="22" height="22" align="absmiddle" /> &nbsp;System Architecture

```mermaid
graph TD
    UI["React Dashboard\n(Workflow Visualizer · Repair Diff · Scorecard)"]
    API["FastAPI Orchestrator\n/api/v1/workflows · /api/v1/repair · /api/v1/sessions"]
    WR["Workflow Runner\n(Playwright Step Executor)"]
    EC["Evidence Collector"]
    DD["DOM Differ\n(difflib unified_diff)"]
    SD["Screenshot Differ\n(PIL + NumPy)"]
    RA["Repair Agent\n(GPT-4o Planner & Ranker)"]
    TF["TinyFish Integration Layer"]
    B["Browser API\n(Cloud CDP Session)"]
    WA["Web Agent\n(Goal-directed SSE)"]
    SF["Search + Fetch API\n(Doc retrieval & page parsing)"]
    RV["Replay & Verification Engine"]
    SC["Recovery Scorecard"]

    UI <-->|REST / WebSocket| API
    API --> WR
    WR -->|FAILURE DETECTED| EC
    EC --> DD
    EC --> SD
    DD --> RA
    SD --> RA
    RA --> TF
    TF --> B
    TF --> WA
    TF --> SF
    RA --> RV
    RV -->|PASS| SC
    RV -->|FAIL — retry| RA
```

---

## <img src="https://api.iconify.design/lucide:workflow.svg?color=%236366f1" width="22" height="22" align="absmiddle" /> &nbsp;The Self-Healing Pipeline

```mermaid
flowchart TD
    A["Browser Workflow Defined\n(Playwright Actions)"] --> B["Execute Workflow\nStep 1 → Step 2 → Step N"]
    B -->|SUCCESS| C["Workflow Complete"]
    B -->|FAILURE| D["Evidence Capture\nDOM Snapshot · Screenshot · Error + Selector"]
    D --> E["TinyFish Browser API\nInspect Live Page — Fresh DOM + Screenshot"]
    E --> F["Diff Engines"]
    F --> G["DOM Differ\ndifflib.unified_diff()"]
    F --> H["Screenshot Differ\nPIL ImageChops + NumPy"]
    G --> I["LLM Repair Planner\nGPT-4o — DOM diff + screenshot score + error → candidates"]
    H --> I
    I -->|"confidence < 0.4"| J["Escalate\nCannot repair confidently — surface failure"]
    I -->|"confidence ≥ 0.4"| K["Apply Best Candidate\nReplace broken selector"]
    K --> L["Replay Workflow\nFrom failed step N"]
    L -->|PASS| M["Recovery Scorecard\nLatency · Attempts · Locator changes · Output correctness"]
    L -->|FAIL| N["Retry with next candidate\nUp to MAX_REPAIR_RETRIES"]
    N --> K
```

---

## <img src="https://api.iconify.design/simple-icons:fish.svg?color=%230ea5e9" width="22" height="22" align="absmiddle" /> &nbsp;TinyFish Integration — The Core Enabler

WebMender AI integrates **all four TinyFish capabilities** as first-class infrastructure:

| Capability | How WebMender Uses It | Why It's Indispensable |
|---|---|---|
| **Browser API** | Spins up a cloud-browser session to execute workflows in a real environment and captures live DOM snapshots and screenshots after failure. | Without real browser execution, actual failures cannot be observed and live evidence cannot be gathered. |
| **Web Agent** | `POST /v1/automation/run-sse` — explores the broken page with a natural-language goal to discover the alternative interaction path. | The agent finds elements that CSS selectors cannot predict — aria labels, text content, contextual layout. |
| **Search API** | Retrieves public documentation or changelogs when a site's update notes are publicly available, enriching the LLM's repair context. | Gives the LLM external signal beyond the DOM — optional but powerful. |
| **Fetch API** | Extracts clean, AI-ready page content in markdown format to supplement the DOM diff with readable text context. | Gives the LLM a human-readable view of the page alongside raw HTML. |

```python
# TinyFish Web Agent exploration — called during repair
async for event in tinyfish.run_web_agent(
    goal="Find the button or link that reveals the product technical specifications",
    url="https://target-website.com/product/xyz",
    session_id=active_browser_session,
):
    print(event)   # SSE events: thought, action, observation, result
```

> **Integration is functional, not cosmetic.** Every repair loop that involves a real website calls the TinyFish Browser API to capture evidence. For sites with unknown change patterns, the Web Agent is invoked to explore and discover paths autonomously.

---

## <img src="https://api.iconify.design/lucide:folder-tree.svg?color=%2322c55e" width="22" height="22" align="absmiddle" /> &nbsp;Project Structure

```
webmender-ai/
│
├── backend/                        # FastAPI Orchestration Server
│   ├── app/
│   │   ├── main.py                 # App entrypoint, CORS, router registration
│   │   ├── core/
│   │   │   └── config.py           # Pydantic settings (TinyFish keys, LLM config)
│   │   ├── models/
│   │   │   └── schemas.py          # All Pydantic schemas: Workflow, Failure, Repair, Scorecard
│   │   ├── agents/
│   │   │   └── repair_agent.py     # AI repair planner (LLM + evidence → candidates)
│   │   ├── services/
│   │   │   ├── tinyfish_service.py # TinyFish Browser / Agent / Search / Fetch wrapper
│   │   │   ├── workflow_runner.py  # Playwright executor + failure capture + repair loop
│   │   │   ├── dom_differ.py       # DOM snapshot diff engine
│   │   │   └── screenshot_differ.py# Pixel-level screenshot comparison (PIL + NumPy)
│   │   └── api/routes/
│   │       ├── workflows.py        # POST /workflows/run, GET /workflows/definitions
│   │       ├── repair.py           # GET /POST /repair/{session_id}
│   │       ├── sessions.py         # GET /sessions/{session_id} — poll for scorecard
│   │       └── health.py           # GET /health
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                       # React Dashboard (React Flow + Tailwind)
│   └── src/
│       ├── components/
│       │   ├── dashboard/          # KPI cards, timeline, status indicators
│       │   └── workflow/           # React Flow workflow visualizer
│       ├── pages/                  # Dashboard, Sessions, Repair View
│       └── hooks/                  # useWorkflow, useRepair, useScorecard
│
├── demo/                           # Controlled demo environment
│   ├── pages/
│   │   ├── version_a/index.html    # Original page — workflow succeeds
│   │   └── version_b/index.html    # Modified page — triggers self-healing
│   └── workflows/
│       └── demo_spec_scraper.py    # End-to-end demo runner
│
└── README.md
```

---

## <img src="https://api.iconify.design/lucide:brain-circuit.svg?color=%23a855f7" width="22" height="22" align="absmiddle" /> &nbsp;AI/ML Architecture Deep Dive

### Repair Agent Intelligence

The repair agent is not a brute-force retry machine. It reasons from structured evidence:

```
EVIDENCE IN:
  ├─ Original failed selector: #btn-specifications
  ├─ Error: TimeoutError — element not found after 5000ms
  ├─ DOM Diff: 47 changed lines
  │    - <button id="btn-specifications">Specifications</button>  (REMOVED)
  │    + <button id="tech-details-btn">Technical Details</button> (ADDED)
  └─ Screenshot diff score: 0.312 (31.2% visual change)

LLM REASONING:
  "The original button with id 'btn-specifications' and text 'Specifications' has been
   replaced by a button with id 'tech-details-btn' and text 'Technical Details'.
   This is a rename with high semantic equivalence. CSS selector #tech-details-btn
   is the most reliable repair; text-based selector button:has-text('Technical Details')
   is the fallback."

CANDIDATES OUT (ranked by confidence):
  1. CSS:   #tech-details-btn                              — confidence: 0.95
  2. Text:  button:has-text("Technical Details")           — confidence: 0.88
  3. XPath: //button[contains(text(),'Technical')]         — confidence: 0.71
```

### Multimodal Evidence Pipeline

```mermaid
flowchart LR
    SB["Screenshot Before"]
    SA["Screenshot After"]
    DB["DOM Snapshot Before"]
    DA["DOM Snapshot After"]

    SB --> PIL["PIL ImageChops.difference()\nNumPy pixel analysis\nRegional change heatmap"]
    SA --> PIL
    PIL --> DS["Diff Score\n0.0 identical → 1.0 different"]

    DB --> DIFF["difflib.unified_diff()\nNoise attribute stripping\nInteractive element extraction"]
    DA --> DIFF
    DIFF --> DD["Structured DOM Diff String"]

    DS --> LLM["GPT-4o Repair Planner"]
    DD --> LLM
    LLM --> OUT["JSON Repair Candidates\nlocator · confidence · reasoning"]
```

---

## <img src="https://api.iconify.design/lucide:layers.svg?color=%236366f1" width="22" height="22" align="absmiddle" /> &nbsp;Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Orchestration** | Python 3.12 + FastAPI | Async API server, workflow management |
| **Browser Automation** | Playwright (async) | Execute and replay browser workflows |
| **Cloud Browser** | TinyFish Browser API | Real browser execution in the cloud |
| **Web Exploration** | TinyFish Web Agent | Goal-directed page exploration via SSE |
| **Web Intelligence** | TinyFish Search + Fetch | Documentation retrieval and page parsing |
| **AI Repair Planner** | OpenAI GPT-4o | Multimodal reasoning for locator repair |
| **DOM Diffing** | Python `difflib` | Structural DOM change detection |
| **Visual Diffing** | Pillow + NumPy | Pixel-level screenshot comparison |
| **Schema Validation** | Pydantic v2 | Type-safe data models throughout |
| **Frontend Dashboard** | React 18 + React Flow | Workflow visualizer, repair diff viewer |
| **Styling** | Tailwind CSS | Responsive, professional UI |

---

## <img src="https://api.iconify.design/lucide:terminal.svg?color=%2322c55e" width="22" height="22" align="absmiddle" /> &nbsp;Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- TinyFish API key — [tinyfish.ai](https://tinyfish.ai)
- OpenAI API key

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
playwright install chromium

cp .env.example .env
# Add your TINYFISH_API_KEY and OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

### 2. Demo Pages Server

```bash
cd demo/pages
python -m http.server 8080
```

### 3. Run the Demo

```bash
python demo/workflows/demo_spec_scraper.py
```

### 4. Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### 5. API Explorer

Visit `http://localhost:8000/api/docs` for the interactive Swagger UI.

---

## <img src="https://api.iconify.design/lucide:plug-zap.svg?color=%230ea5e9" width="22" height="22" align="absmiddle" /> &nbsp;API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `POST` | `/api/v1/workflows/run` | Start a workflow run |
| `GET` | `/api/v1/workflows/definitions` | List example workflow definitions |
| `GET` | `/api/v1/sessions/{id}` | Poll for recovery scorecard |
| `GET` | `/api/v1/repair/{id}` | Get repair plan details |
| `POST` | `/api/v1/repair/{id}/accept` | Accept a repair and trigger replay |
| `POST` | `/api/v1/repair/{id}/reject` | Reject repair — escalate as unrecoverable |

---

## <img src="https://api.iconify.design/lucide:globe.svg?color=%2322c55e" width="22" height="22" align="absmiddle" /> &nbsp;Real-World Use Cases

**Enterprise QA Automation**
Stop paying engineers to update selectors after every UI redesign. WebMender repairs them automatically and logs every change with a full audit trail.

**Production AI Agents**
Your GPT-powered web agent breaks every time the target website updates. WebMender wraps it with a reliability layer that self-heals in real time.

**Web Scraping Pipelines**
Data pipelines that break on layout changes get expensive fast. WebMender recovers them and emits structured change audit trails.

**Regression Testing**
Catch unintended UI changes before your QA team does — by running WebMender as part of your CI/CD pipeline.

---

## <img src="https://api.iconify.design/lucide:map.svg?color=%23f59e0b" width="22" height="22" align="absmiddle" /> &nbsp;Roadmap

```mermaid
flowchart LR
    P1["Phase 1 — Hackathon MVP\nSingle workflow\nControlled demo pages\nLLM repair loop\nRecovery scorecard"]
    P2["Phase 2 — Q1 2027\nWorkflow library\nConcurrent workflows\nRepair history DB\nGitHub Actions integration"]
    P3["Phase 3 — Q3 2027\nSaaS platform\nTeam dashboards\nFine-tuned repair model\nChrome extension"]

    P1 --> P2 --> P3
```

---

## <img src="https://api.iconify.design/lucide:trophy.svg?color=%23f59e0b" width="22" height="22" align="absmiddle" /> &nbsp;Built For

<div align="center">

**Kritical Hacks 2026**
Indira Gandhi Delhi Technical University for Women (IGDTUW)
AI/ML Track — Open Innovation

*Mandatory TinyFish Integration: Browser · Web Agent · Search · Fetch*

</div>
