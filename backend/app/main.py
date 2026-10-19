"""
WebMender AI — FastAPI Orchestration Server
Self-Healing Browser Agent for AI Workflow Resilience
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import workflows, repair, sessions, health
from app.core.config import settings

app = FastAPI(
    title="WebMender AI",
    description="Self-Healing Browser Agent — Websites change. Your AI agent shouldn't break.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(repair.router, prefix="/api/v1/repair", tags=["Repair"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Sessions"])


@app.on_event("startup")
async def startup_event():
    print("🦾 WebMender AI is online — ready to self-heal broken browser agents.")


@app.on_event("shutdown")
async def shutdown_event():
    print("WebMender AI shutting down gracefully.")
