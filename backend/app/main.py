"""FastAPI application for miniature tracker."""

import os
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.crud import MiniatureDB
from app.models import Miniature, MiniatureCreate, MiniatureUpdate, StatusLogEntry, StatusLogEntryCreate, StatusLogEntryUpdate
from app.auth_routes import router as auth_router
from app.auth_dependencies import get_current_user_id


# Create FastAPI app
app = FastAPI(
    title="Miniature Tracker API",
    description="API for tracking Warhammer miniature collection and painting progress",
    version="0.1.0"
)

# Include authentication routes
app.include_router(auth_router)


def get_db() -> MiniatureDB:
    """Dependency to get database instance."""
    return MiniatureDB()


@app.post("/miniatures", response_model=Miniature, status_code=status.HTTP_201_CREATED)
def create_miniature(
    miniature: MiniatureCreate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Miniature:
    """Create a new miniature for the authenticated user."""
    return db.create_miniature(miniature, current_user_id)


@app.get("/miniatures", response_model=List[Miniature])
def get_all_miniatures(
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> List[Miniature]:
    """Get all miniatures for the authenticated user."""
    return db.get_all_miniatures(current_user_id)


@app.get("/miniatures/{miniature_id}", response_model=Miniature)
def get_miniature(
    miniature_id: UUID,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Miniature:
    """Get a specific miniature by ID for the authenticated user."""
    miniature = db.get_miniature(miniature_id, current_user_id)
    if miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    return miniature


@app.put("/miniatures/{miniature_id}", response_model=Miniature)
def update_miniature(
    miniature_id: UUID,
    miniature_update: MiniatureUpdate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Miniature:
    """Update an existing miniature for the authenticated user."""
    updated_miniature = db.update_miniature(miniature_id, miniature_update, current_user_id)
    if updated_miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    return updated_miniature


@app.delete("/miniatures/{miniature_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_miniature(
    miniature_id: UUID,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> None:
    """Delete a miniature for the authenticated user."""
    success = db.delete_miniature(miniature_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )


# Status log endpoints
@app.post("/miniatures/{miniature_id}/status-logs", response_model=StatusLogEntry, status_code=status.HTTP_201_CREATED)
def add_status_log(
    miniature_id: UUID,
    log_data: StatusLogEntryCreate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> StatusLogEntry:
    """Add a manual status log entry to a miniature."""
    miniature = db.add_status_log_entry(miniature_id, log_data, current_user_id)
    if miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    # Return the last status log entry (the one we just added)
    return miniature.status_history[-1]


@app.put("/miniatures/{miniature_id}/status-logs/{log_id}", response_model=StatusLogEntry)
def update_status_log(
    miniature_id: UUID,
    log_id: UUID,
    log_update: StatusLogEntryUpdate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> StatusLogEntry:
    """Update a status log entry."""
    updated_miniature = db.update_status_log_entry(miniature_id, log_id, log_update, current_user_id)
    if updated_miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status log entry with ID {log_id} not found"
        )
    # Find and return the updated log entry
    for log_entry in updated_miniature.status_history:
        if str(log_entry.id) == str(log_id):
            return log_entry
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Status log entry with ID {log_id} not found"
    )


@app.delete("/miniatures/{miniature_id}/status-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status_log(
    miniature_id: UUID,
    log_id: UUID,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> None:
    """Delete a manual status log entry."""
    updated_miniature = db.delete_status_log_entry(miniature_id, log_id, current_user_id)
    if updated_miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status log entry with ID {log_id} not found or cannot be deleted"
        )


# Add CORS middleware for frontend integration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://*.railway.app",  # Railway domains
        "https://*.onrender.com",  # Render domains
        "*"  # Allow all origins in production (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (React build) in production
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount React's static assets (CSS, JS)
    react_static_dir = os.path.join(static_dir, "static")
    if os.path.exists(react_static_dir):
        app.mount("/static", StaticFiles(directory=react_static_dir), name="static")
    
    @app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        """Serve React app for all non-API routes."""
        # Don't serve React app for API routes
        if (full_path.startswith("api/") or 
            full_path.startswith("miniatures") or 
            full_path.startswith("auth") or
            full_path.startswith("docs") or 
            full_path.startswith("openapi.json") or
            full_path.startswith("redoc")):
            raise HTTPException(status_code=404, detail="Not found")
            
        # Serve index.html for all other routes (React Router)
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not found")
else:
    # Fallback API endpoint when no static files are available
    @app.get("/")
    def read_root() -> dict:
        """Root endpoint with API information."""
        return {
            "message": "Welcome to the Miniature Tracker API! Track your Warhammer miniature collection and painting progress.",
            "docs": "/docs",
            "version": "0.1.0"
        } 