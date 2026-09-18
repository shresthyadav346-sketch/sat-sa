"""
SAT-SA: Supervisory Analytics Tool for SOC Assessment
Main FastAPI Application Entrypoint
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.api import (
    dashboard_router,
    cses_router,
    findings_router,
    review_queue_router,
    negative_space_router,
    peer_comparison_router,
    audit_router,
    audit_chain_router,
    reports_router,
    ingest_router
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Offline Supervisory Analytics & Decision Support Tool for NCIIPC evaluating Critical Sector Entities (CSEs)."
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(dashboard_router)
app.include_router(cses_router)
app.include_router(findings_router)
app.include_router(review_queue_router)
app.include_router(negative_space_router)
app.include_router(peer_comparison_router)
app.include_router(audit_router)
app.include_router(audit_chain_router)
app.include_router(reports_router)
app.include_router(ingest_router)

@app.on_event("startup")
def on_startup():
    """Ensure database schema is created on application startup."""
    init_db()

@app.get("/api/health")
def health_check():
    """Health check endpoint confirming offline-first operation."""
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "offline_mode": True,
        "demonstration_banner": settings.NCIIPC_BANNER
    }

# Serve frontend build if dist folder exists
dist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="static_assets")
    
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
