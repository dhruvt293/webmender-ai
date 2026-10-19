# 🦾 WebMender AI — The Self-Healing Browser Agent

<div align="center">

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

## ⚡ The Problem We're Solving

AI agents are increasingly expected to complete real-world tasks on the web: filling forms, collecting data, navigating portals. But the web is a moving target.

```
Day 1:  workflow clicks  →  button[id="btn-specifications"]  ✅ Works
Day 7:  Same workflow    →  button[id="tech-details-btn"]    ❌ FAILS
```

| Traditional Automation | WebMender AI |
|---|---|
| 🔴 Breaks silently on selector changes | 🟢 Detects failure instantly |
| 🔴 Requires manual inspection | 🟢 Inspects the live page autonomously |
| 🔴 Engineer must rewrite the selector | 🟢 LLM proposes and ranks repair candidates |
| 🔴 No evidence trail | 🟢 Full DOM diff + screenshot diff + audit log |
| 🔴 Re-run fails again | 🟢 Replays and validates the repaired workflow |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WebMender AI Platform                        │
│                                                                     │
│  ┌──────────────┐    ┌────────────────────────────────────────┐    │
│  │   React UI   │◄──►│         FastAPI Orchestrator           │    │
│  │  Dashboard   │    │   /api/v1/workflows  /api/v1/repair    │    │
│  │  Repair Diff │    └────────────┬───────────────────────────┘    │
│  │  Scorecard   │                 │                                 │
│  └──────────────┘    ┌────────────▼───────────────────────────┐    │
│                       │         Workflow Runner                 │    │
│                       │   (Playwright + Step Executor)         │    │
│                       └────────────┬───────────────────────────┘    │
│                                    │ FAILURE DETECTED               │
│                       ┌────────────▼───────────────────────────┐    │
│                       │        Evidence Collector               │    │
│                       │  ┌──────────────┬──────────────┐       │    │
│                       │  │  DOM Diff    │  Screenshot  │       │    │
│                       │  │  Engine      │  Differ      │       │    │
│                       │  └──────┬───────┴──────┬───────┘       │    │
│                       └─────────┼──────────────┼───────────────┘    │
│                                 │              │                     │
│                       ┌─────────▼──────────────▼───────────────┐    │
│                       │          Repair Agent (LLM Core)        │    │
│                       │    GPT-4o Repair Planner & Ranker       │    │
│                       └─────────────────┬───────────────────────┘    │
│                                         │                           │
│                       ┌─────────────────▼───────────────────────┐    │
│                       │         TinyFish Integration Layer       │    │
│                       │  ┌──────────┬────────────┬──────────┐   │    │
│                       │  │ Browser  │ Web Agent  │ Search   │   │    │
│                       │  │ (CDP)    │ (SSE)      │ & Fetch  │   │    │
│                       │  └──────────┴────────────┴──────────┘   │    │
│                       └─────────────────┬───────────────────────┘    │
│                                         │                           │
│                       ┌─────────────────▼───────────────────────┐    │
│                       │    Replay & Verification Engine          │    │
│                       │   (Re-run → Assert → Recovery Scorecard) │    │
│                       └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 The Self-Healing Pipeline

```
                        ╔══════════════════════════════╗
                        ║   Browser Workflow Defined   ║
                        ║   (Playwright Actions)       ║
                        ╚══════════════╦═══════════════╝
                                       ║
                                       ▼
                        ╔══════════════════════════════╗
                        ║      Execute Workflow         ║
                        ║   Step 1 → Step 2 → Step N   ║
                        ╚══════╦═══════════════╦════════╝
                               ║               ║
                         SUCCESS ✅         FAILURE ❌
                               ║               ║
                               ▼               ▼
                        ┌──────────┐   ╔══════════════════════════╗
                        │  Done ✅  │   ║  Evidence Capture        ║
                        └──────────┘   ║  • DOM Snapshot          ║
                                       ║  • Screenshot (base64)   ║
                                       ║  • Error + Selector      ║
                                       ╚══════════╦═══════════════╝
                                                  ║
                                                  ▼
                                       ╔══════════════════════════╗
                                       ║  TinyFish Browser API    ║
                                       ║  Inspect Live Page       ║
                                       ║  • Fresh DOM snapshot    ║
                                       ║  • Live screenshot       ║
                                       ╚══════════╦═══════════════╝
                                                  ║
                                                  ▼
                                       ╔══════════════════════════╗
                                       ║   Diff Engines           ║
                                       ║  ┌──────────────────┐   ║
                                       ║  │  DOM Differ      │   ║
                                       ║  │  unified_diff()  │   ║
                                       ║  ├──────────────────┤   ║
                                       ║  │ Screenshot Diff  │   ║
                                       ║  │ PIL + numpy      │   ║
                                       ║  └──────────────────┘   ║
                                       ╚══════════╦═══════════════╝
                                                  ║
                                                  ▼
                                       ╔══════════════════════════╗
                                       ║  LLM Repair Planner      ║
                                       ║  (GPT-4o / gpt-4o-mini) ║
                                       ║  • DOM diff as context   ║
                                       ║  • Screenshot diff score ║
                                       ║  • Error message         ║
                                       ║  → Repair candidates[]   ║
                                       ║  → Confidence scores     ║
                                       ║  → Reasoning             ║
                                       ╚══════════╦═══════════════╝
                                                  ║
                              ┌───────────────────┼────────────────────┐
                              ║                   ║                    ║
                       confidence               medium            low (<0.4)
                       ≥ 0.4                   → retry             → STOP
                              ║                                        ║
                              ▼                                        ▼
                    ╔═══════════════════╗                   ╔══════════════════╗
                    ║  Apply Repair     ║                   ║  Escalate        ║
                    ║  Best Candidate   ║                   ║  "Cannot repair  ║
                    ║  selector         ║                   ║   confidently"   ║
                    ╚═════════╦═════════╝                   ╚══════════════════╝
                              ║
                              ▼
                    ╔═══════════════════╗
                    ║  Replay Workflow  ║
                    ║  (from step N)    ║
                    ╚═════════╦═════════╝
                              ║
                   ┌──────────┴──────────┐
               PASS ✅              FAIL ❌
                   ║                     ║
                   ▼                     ▼
         ╔═══════════════╗      ╔════════════════╗
         ║  Recovery     ║      ║   Retry with   ║
         ║  Scorecard    ║      ║ next candidate ║
         ╚═══════════════╝      ╚════════════════╝
```

---

## 🐟 TinyFish Integration — The Core Enabler

WebMender AI integrates **all four TinyFish capabilities** as first-class infrastructure:

| Capability | How WebMender Uses It | Why It's Indispensable |
|---|---|---|
| **🌐 Browser API** | Spins up a cloud-browser to execute workflows in a real environment. Captures live DOM snapshots and screenshots after failure. | Without real browser execution, we can't observe actual failures or gather live evidence. |
| **🤖 Web Agent** | `POST /v1/automation/run-sse` — explores the broken page with a natural-language goal to discover the alternative interaction path. | The agent discovers elements that CSS selectors can't predict — aria labels, text content, contextual layout. |
| **🔍 Search API** | Retrieves public documentation or changelogs when a site's update notes are publicly available, enriching the LLM's repair context. | Optional but powerful — gives the LLM external signal beyond the DOM. |
| **📄 Fetch API** | Extracts clean, AI-ready page content in markdown format to supplement the DOM diff with readable text context. | Gives the LLM a human-readable view of the page alongside raw HTML. |

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

## 📁 Project Structure

```
webmender-ai/
│
├── 📂 backend/                    # FastAPI Orchestration Server
│   ├── app/
│   │   ├── main.py                # App entrypoint, CORS, router registration
│   │   ├── core/
│   │   │   └── config.py          # Pydantic settings (TinyFish keys, LLM config)
│   │   ├── models/
│   │   │   └── schemas.py         # All Pydantic schemas: Workflow, Failure, Repair, Scorecard
│   │   ├── agents/
│   │   │   └── repair_agent.py    # 🧠 AI repair planner (LLM + evidence → candidates)
│   │   ├── services/
│   │   │   ├── tinyfish_service.py   # 🐟 TinyFish Browser/Agent/Search/Fetch wrapper
│   │   │   ├── workflow_runner.py    # Playwright executor + failure capture + repair loop
│   │   │   ├── dom_differ.py         # DOM snapshot diff engine
│   │   │   └── screenshot_differ.py  # Pixel-level screenshot comparison (PIL + numpy)
│   │   └── api/routes/
│   │       ├── workflows.py       # POST /workflows/run, GET /workflows/definitions
│   │       ├── repair.py          # GET/POST /repair/{session_id}
│   │       ├── sessions.py        # GET /sessions/{session_id} — poll for scorecard
│   │       └── health.py          # GET /health
│   ├── requirements.txt
│   └── .env.example
│
├── 📂 frontend/                   # React Dashboard (React Flow + Tailwind)
│   └── src/
│       ├── components/
│       │   ├── dashboard/         # KPI cards, timeline, status indicators
│       │   └── workflow/          # React Flow workflow visualizer
│       ├── pages/                 # Main pages: Dashboard, Sessions, Repair View
│       └── hooks/                 # useWorkflow, useRepair, useScorecard
│
├── 📂 demo/                       # Controlled demo environment
│   ├── pages/
│   │   ├── version_a/index.html   # ✅ Original page — workflow SUCCEEDS
│   │   └── version_b/index.html   # ❌ Modified page — triggers self-healing
│   └── workflows/
│       └── demo_spec_scraper.py   # End-to-end demo runner
│
└── 📄 README.md
```

---

## 🧠 AI/ML Architecture Deep Dive

### Repair Agent Intelligence

The repair agent is not a brute-force retry machine. It reasons:

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
   is the most reliable repair; text-based selector 'button:text("Technical Details")'
   is the fallback."

CANDIDATES OUT (ranked by confidence):
  1. CSS:   #tech-details-btn           — confidence: 0.95
  2. Text:  button:has-text("Technical Details")  — confidence: 0.88
  3. XPath: //button[contains(text(),'Technical')]  — confidence: 0.71
```

### Multimodal Evidence Pipeline

```
Screenshot Before  ──┐
Screenshot After   ──┤──► PIL ImageChops.difference()
                      │    numpy pixel analysis
                      │    Regional change heatmap
                      └──► Diff Score ∈ [0.0, 1.0]

DOM Before         ──┐
DOM After          ──┤──► difflib.unified_diff()
                      │    Noise attribute stripping
                      │    Interactive element extraction
                      └──► Structured diff string

Both signals       ──► GPT-4o Repair Planner
                        → JSON repair candidates[]
```

---

## 📊 Recovery Scorecard — What Judges See

After every self-healing cycle, WebMender emits a machine-readable **Recovery Scorecard**:

```json
{
  "workflow_id": "demo-spec-scraper",
  "session_id": "a3f1c2d9-...",
  "status": "verified",
  "total_actions": 4,
  "failed_at_index": 2,
  "repair_attempts": 1,
  "recovery_latency_ms": 4821,
  "output_correctness": true,
  "locator_changes": [
    {
      "original": "#btn-specifications",
      "repaired": "#tech-details-btn",
      "confidence": "0.95"
    }
  ],
  "repair_plan": {
    "dom_diff_summary": "47 changed lines...",
    "screenshot_diff_score": 0.312,
    "selected_candidate": {
      "locator_type": "css",
      "locator_value": "#tech-details-btn",
      "confidence": 0.95,
      "reasoning": "Renamed button with identical semantic role"
    },
    "llm_explanation": "Button 'Specifications' renamed to 'Technical Details'..."
  }
}
```

---

## 🎬 The Winning Demo Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LIVE DEMO SEQUENCE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 1: Baseline (Version A — Original Page)                      │
│  ─────────────────────────────────────────────                      │
│  ① Open Version A in TinyFish cloud browser                        │
│  ② Run Playwright workflow → click #btn-specifications              │
│  ③ Watch: specs table loads ✅                                       │
│  ④ Show: workflow trace, green status                               │
│                                                                     │
│  PHASE 2: The Break (Version B — Modified Page)                     │
│  ───────────────────────────────────────────────                    │
│  ⑤ Switch to Version B (button renamed, layout changed)            │
│  ⑥ Re-run exact same workflow → TimeoutError ❌                     │
│  ⑦ Show: failure capture, error trace                              │
│                                                                     │
│  PHASE 3: Self-Healing (WebMender takes over)                       │
│  ─────────────────────────────────────────────                      │
│  ⑧ TinyFish Browser re-inspects the live page                      │
│  ⑨ DOM diff highlights removed/added elements                      │
│  ⑩ Screenshot diff shows visual change score: 0.31                 │
│  ⑪ LLM generates repair candidates with confidence                 │
│  ⑫ Best candidate applied: #tech-details-btn (conf: 0.95)          │
│                                                                     │
│  PHASE 4: Verification & Scorecard                                  │
│  ──────────────────────────────────                                 │
│  ⑬ Repaired workflow replays → specs load ✅                         │
│  ⑭ Recovery Scorecard displayed:                                   │
│     • Recovery latency: ~4.8s                                       │
│     • Repair attempts: 1                                            │
│     • Output correctness: ✅                                        │
│     • Locator change: #btn-specifications → #tech-details-btn       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Orchestration** | Python 3.12 + FastAPI | Async API server, workflow management |
| **Browser Automation** | Playwright (async) | Execute and replay browser workflows |
| **Cloud Browser** | TinyFish Browser API | Real browser execution in the cloud |
| **Web Exploration** | TinyFish Web Agent | Goal-directed page exploration via SSE |
| **Web Intelligence** | TinyFish Search + Fetch | Documentation retrieval & page parsing |
| **AI Repair Planner** | OpenAI GPT-4o | Multimodal reasoning for locator repair |
| **DOM Diffing** | Python `difflib` | Structural DOM change detection |
| **Visual Diffing** | Pillow + NumPy | Pixel-level screenshot comparison |
| **Schema Validation** | Pydantic v2 | Type-safe data models throughout |
| **Frontend Dashboard** | React 18 + React Flow | Workflow visualizer, repair diff viewer |
| **Styling** | Tailwind CSS | Responsive, professional UI |

---

## 🚀 Quick Start

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
# Serve the controlled demo pages on port 8080
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

Visit **http://localhost:8000/api/docs** for the interactive Swagger UI.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `POST` | `/api/v1/workflows/run` | Start a workflow run |
| `GET` | `/api/v1/workflows/definitions` | List example workflow definitions |
| `GET` | `/api/v1/sessions/{id}` | Poll for recovery scorecard |
| `GET` | `/api/v1/repair/{id}` | Get repair plan details |
| `POST` | `/api/v1/repair/{id}/accept` | Accept a repair and trigger replay |
| `POST` | `/api/v1/repair/{id}/reject` | Reject repair — escalate as unrecoverable |

**Interactive docs:** `http://localhost:8000/api/docs`

---

## 🌐 Real-World Use Cases

```
  🏢 Enterprise QA Automation
     Stop paying engineers to update selectors after every UI redesign.
     WebMender repairs them automatically and logs every change.

  🤖 Production AI Agents
     Your GPT-powered web agent breaks every time the target website updates.
     WebMender wraps it with a reliability layer that self-heals in real time.

  📊 Web Scraping Pipelines
     Data pipelines that break on layout changes get expensive fast.
     WebMender recovers them and emits structured change audit trails.

  🧪 Regression Testing
     Catch unintended UI changes before your QA team does —
     by running WebMender as part of your CI/CD pipeline.
```

---

## 📈 Long-Term Roadmap

```
Phase 1 (Hackathon MVP) ────────────────────────────────── ✅ NOW
  Single workflow · controlled demo pages · LLM repair · scorecard

Phase 2 (Post-Hackathon) ─────────────────────────────── 🔜 Q1 2027
  Workflow library · multiple concurrent workflows · repair history DB
  VS Code extension · GitHub Actions integration

Phase 3 (Product) ────────────────────────────────────── 🔜 Q3 2027
  SaaS platform · team dashboards · enterprise SSO
  Fine-tuned repair model (trained on repair history)
  Chrome extension for one-click workflow recording
```

---

## 👥 Team

| Name | Role |
|---|---|
| **BugByte League** | Kritical Hacks 2026 · AI/ML Track · Student Category |

---

## 🏆 Built For

<div align="center">

**Kritical Hacks 2026**  
Indira Gandhi Delhi Technical University for Women (IGDTUW)  
AI/ML Track — Open Innovation  

*Mandatory TinyFish Integration: ✅ Browser · ✅ Web Agent · ✅ Search · ✅ Fetch*

---

<sub>WebMender AI · Kritical Hacks 2026 · Built with ❤️ in 24 hours</sub>

</div>
