# mrwa/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

# ------------------------------------------------------------------
# CREATE APP FIRST (THIS FIXES NameError: app not defined)
# ------------------------------------------------------------------

app = FastAPI(
    title="MRWA - Marathon Research & Workflow Agent",
    version="0.1.0",
)

# ------------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# SAFE IMPORTS (AFTER app EXISTS)
# ------------------------------------------------------------------

try:
    from core.orchestrator.engine import OrchestratorEngine
except Exception as e:
    raise RuntimeError(f"Failed to load OrchestratorEngine: {e}")

try:
    from core.storage.provider import get_storage_provider
except Exception as e:
    raise RuntimeError(f"Failed to load storage provider: {e}")

# OPTIONAL / NON-FATAL IMPORTS
PDFParser = None
try:
    from ingestion.document_parser.pdf_parser import PDFParser
except Exception:
    # Prevent crash if module is missing
    pass

# ------------------------------------------------------------------
# INITIALIZE GLOBALS (RELOAD SAFE)
# ------------------------------------------------------------------

orchestrator: Optional[OrchestratorEngine] = None
storage = None

@app.on_event("startup")
async def startup_event():
    global orchestrator, storage

    if orchestrator is None:
        orchestrator = OrchestratorEngine()

    if storage is None:
        storage = get_storage_provider()

@app.on_event("shutdown")
async def shutdown_event():
    # Add cleanup here if needed
    pass

# ------------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}

# ------------------------------------------------------------------
# FILE UPLOAD ENDPOINT
# ------------------------------------------------------------------

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    data = await file.read()

    if not storage:
        raise HTTPException(status_code=500, detail="Storage not initialized")

    url = await storage.save_file(
        data=data,
        filename=file.filename,
        content_type=file.content_type,
    )

    return {
        "success": True,
        "filename": file.filename,
        "url": url,
    }

# ------------------------------------------------------------------
# EXECUTION ENDPOINT
# ------------------------------------------------------------------

@app.post("/api/v1/execute")
async def execute(payload: dict):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not ready")

    result = await orchestrator.execute(payload)
    return result
