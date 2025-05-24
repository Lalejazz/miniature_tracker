"""FastAPI application for miniature tracker."""

import os
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.crud import MiniatureDB
from app.models import Miniature, MiniatureCreate, MiniatureUpdate


# Create FastAPI app
app = FastAPI(
    title="Miniature Tracker API",
    description="API for tracking Warhammer miniature collection and painting progress",
    version="0.1.0"
)


def get_db() -> MiniatureDB:
    """Dependency to get database instance."""
    return MiniatureDB()


@app.post("/miniatures", response_model=Miniature, status_code=status.HTTP_201_CREATED)
def create_miniature(
    miniature: MiniatureCreate,
    db: MiniatureDB = Depends(get_db)
) -> Miniature:
    """Create a new miniature."""
    return db.create(miniature)


@app.get("/miniatures", response_model=List[Miniature])
def get_all_miniatures(db: MiniatureDB = Depends(get_db)) -> List[Miniature]:
    """Get all miniatures."""
    return db.get_all()


@app.get("/miniatures/{miniature_id}", response_model=Miniature)
def get_miniature(
    miniature_id: UUID,
    db: MiniatureDB = Depends(get_db)
) -> Miniature:
    """Get a specific miniature by ID."""
    miniature = db.get_by_id(miniature_id)
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
    db: MiniatureDB = Depends(get_db)
) -> Miniature:
    """Update an existing miniature."""
    updated_miniature = db.update(miniature_id, miniature_update)
    if updated_miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    return updated_miniature


@app.delete("/miniatures/{miniature_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_miniature(
    miniature_id: UUID,
    db: MiniatureDB = Depends(get_db)
) -> None:
    """Delete a miniature."""
    success = db.delete(miniature_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )


# Add CORS middleware for frontend integration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
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
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        """Serve React app for all non-API routes."""
        # Don't serve React app for API routes
        if (full_path.startswith("api/") or 
            full_path.startswith("miniatures") or 
            full_path.startswith("docs") or 
            full_path.startswith("openapi.json") or
            full_path.startswith("redoc")):
            raise HTTPException(status_code=404, detail="Not found")
            
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