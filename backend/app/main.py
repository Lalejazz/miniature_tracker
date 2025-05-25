"""FastAPI application for miniature tracker."""

import os
from typing import List
from uuid import UUID
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Query, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.crud import MiniatureDB
from app.models import Miniature, MiniatureCreate, MiniatureUpdate, StatusLogEntry, StatusLogEntryCreate, StatusLogEntryUpdate, CollectionStatistics, TrendAnalysis, TrendRequest
from app.auth_routes import router as auth_router
from app.auth_dependencies import get_current_user_id
from app.player_routes import router as player_router
from app.oauth_routes import router as oauth_router
from app.user_crud import UserDB


# Create FastAPI app
app = FastAPI(
    title="Miniature Tracker API",
    description="API for tracking Warhammer miniature collection and painting progress",
    version="0.1.0"
)

# Include authentication routes
app.include_router(auth_router)
app.include_router(player_router)
app.include_router(oauth_router)


def get_db() -> MiniatureDB:
    """Dependency to get database instance."""
    return MiniatureDB()


@app.post("/miniatures", response_model=Miniature, status_code=status.HTTP_201_CREATED)
async def create_miniature(
    miniature: MiniatureCreate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Miniature:
    """Create a new miniature for the authenticated user."""
    return await db.create_miniature(miniature, current_user_id)


@app.get("/miniatures", response_model=List[Miniature])
async def get_all_miniatures(
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> List[Miniature]:
    """Get all miniatures for the authenticated user."""
    return await db.get_all_miniatures(current_user_id)


@app.get("/miniatures/statistics", response_model=CollectionStatistics)
async def get_collection_statistics(
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> CollectionStatistics:
    """Get collection statistics for the authenticated user."""
    return await db.get_collection_statistics(current_user_id)


@app.post("/miniatures/trends", response_model=TrendAnalysis)
async def get_trend_analysis(
    request: TrendRequest,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Get trend analysis for the user's collection."""
    return await db.get_trend_analysis(
        current_user_id,
        request.from_date,
        request.to_date,
        request.group_by
    )


@app.get("/miniatures/export/{format}")
async def export_collection(
    format: str,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Export user's collection in JSON or CSV format."""
    if format.lower() not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    try:
        # Get all miniatures for the user
        miniatures = await db.get_all_miniatures(current_user_id)
        
        # Get user info for filename
        from app.database import get_database
        database = get_database()
        await database.initialize()
        user = await database.get_user_by_id(current_user_id)
        username = user.username if user else "user"
        
        if format.lower() == "json":
            # Export as JSON (works even with empty collection)
            export_data = {
                "export_info": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "user_id": str(current_user_id),
                    "username": username,
                    "total_units": len(miniatures)
                },
                "miniatures": []
            }
            
            # Process each miniature for JSON export
            for miniature in miniatures:
                miniature_data = miniature.model_dump()
                
                # Add status timeline summary for easier analysis
                status_timeline = {}
                for log_entry in miniature.status_history:
                    log_date = log_entry.date if hasattr(log_entry, 'date') else log_entry.created_at
                    status_timeline[log_entry.to_status] = log_date.isoformat() if log_date else None
                
                miniature_data["status_timeline"] = status_timeline
                export_data["miniatures"].append(miniature_data)
            
            # Create JSON response
            json_content = json.dumps(export_data, indent=2, default=str)
            
            return Response(
                content=json_content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=miniature_collection_{username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )
        
        else:  # CSV format
            import io
            import csv
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Get all possible statuses for column headers
            from app.models import PaintingStatus
            status_columns = [f"status_{status.value}" for status in PaintingStatus]
            
            # Write header - basic info + status timeline columns
            headers = [
                "id", "name", "faction", "unit_type", "game_system", "current_status", 
                "quantity", "base_dimension", "custom_base_size", "cost", 
                "notes", "created_at", "updated_at"
            ] + status_columns
            writer.writerow(headers)
            
            # Write data rows (even if empty, we still have headers)
            for miniature in miniatures:
                try:
                    # Build status timeline dictionary
                    status_timeline = {}
                    for log_entry in miniature.status_history:
                        # Use the date when the miniature moved TO this status
                        status_key = f"status_{log_entry.to_status}"
                        log_date = log_entry.date if hasattr(log_entry, 'date') else log_entry.created_at
                        status_timeline[status_key] = log_date.isoformat() if log_date else ""
                    
                    # Basic miniature data
                    row = [
                        str(miniature.id),
                        miniature.name,
                        miniature.faction,
                        miniature.unit_type.value if miniature.unit_type else "",
                        miniature.game_system.value if miniature.game_system else "",
                        miniature.status.value if hasattr(miniature.status, 'value') else str(miniature.status),
                        miniature.quantity,
                        miniature.base_dimension.value if miniature.base_dimension else "",
                        miniature.custom_base_size or "",
                        str(miniature.cost) if miniature.cost else "",
                        miniature.notes or "",
                        miniature.created_at.isoformat() if miniature.created_at else "",
                        miniature.updated_at.isoformat() if miniature.updated_at else ""
                    ]
                    
                    # Add status timeline columns
                    for status_col in status_columns:
                        row.append(status_timeline.get(status_col, ""))
                    
                    writer.writerow(row)
                except Exception as e:
                    # Log the error but continue with other miniatures
                    print(f"Error processing miniature {miniature.id}: {e}")
                    continue
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=miniature_collection_{username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
    
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/miniatures/import/{format}")
async def import_collection(
    format: str,
    file: UploadFile = File(...),
    replace_existing: bool = Query(False, description="Whether to replace existing collection or merge"),
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Import collection from JSON or CSV file."""
    if format.lower() not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    try:
        # Read file content
        content = await file.read()
        
        imported_miniatures = []
        
        if format.lower() == "json":
            # Parse JSON
            try:
                data = json.loads(content.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
            
            # Extract miniatures from JSON
            if "miniatures" in data:
                miniatures_data = data["miniatures"]
            elif isinstance(data, list):
                miniatures_data = data
            else:
                raise HTTPException(status_code=400, detail="JSON must contain 'miniatures' array or be an array of miniatures")
            
            # Convert JSON data to MiniatureCreate objects
            for item in miniatures_data:
                try:
                    # Map old field names to new ones if needed
                    if "model_type" in item and "unit_type" not in item:
                        item["unit_type"] = item["model_type"]
                    
                    # Remove fields that shouldn't be imported
                    import_data = {k: v for k, v in item.items() 
                                 if k not in ["id", "user_id", "status_history", "created_at", "updated_at"]}
                    
                    miniature_create = MiniatureCreate(**import_data)
                    imported_miniatures.append(miniature_create)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid miniature data: {str(e)}")
        
        else:  # CSV format
            import csv
            import io
            
            try:
                csv_content = content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                for row in csv_reader:
                    try:
                        # Convert CSV row to miniature data
                        miniature_data = {}
                        
                        # Required fields
                        miniature_data["name"] = row.get("name", "").strip()
                        miniature_data["faction"] = row.get("faction", "").strip()
                        
                        # Handle unit_type (with fallback to model_type for backward compatibility)
                        unit_type = row.get("unit_type", "").strip() or row.get("model_type", "").strip()
                        if unit_type:
                            miniature_data["unit_type"] = unit_type
                        
                        # Handle game_system
                        game_system = row.get("game_system", "").strip()
                        if game_system:
                            miniature_data["game_system"] = game_system
                        
                        # Handle status
                        status = row.get("status", "").strip()
                        if status:
                            miniature_data["status"] = status
                        
                        # Optional fields
                        if row.get("quantity", "").strip():
                            miniature_data["quantity"] = int(row["quantity"])
                        
                        if row.get("base_dimension", "").strip():
                            miniature_data["base_dimension"] = row["base_dimension"].strip()
                        
                        if row.get("custom_base_size", "").strip():
                            miniature_data["custom_base_size"] = row["custom_base_size"].strip()
                        
                        if row.get("cost", "").strip():
                            miniature_data["cost"] = float(row["cost"])
                        
                        if row.get("notes", "").strip():
                            miniature_data["notes"] = row["notes"].strip()
                        
                        # Validate required fields
                        if not miniature_data.get("name"):
                            continue  # Skip rows without name
                        
                        miniature_create = MiniatureCreate(**miniature_data)
                        imported_miniatures.append(miniature_create)
                        
                    except Exception as e:
                        # Log error but continue with other rows
                        print(f"Error processing CSV row: {e}")
                        continue
                        
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
        
        if not imported_miniatures:
            raise HTTPException(status_code=400, detail="No valid miniatures found in import file")
        
        # If replace_existing is True, delete existing miniatures
        if replace_existing:
            existing_miniatures = await db.get_all_miniatures(current_user_id)
            for miniature in existing_miniatures:
                await db.delete_miniature(miniature.id, current_user_id)
        
        # Import new miniatures
        created_miniatures = []
        for miniature_create in imported_miniatures:
            try:
                created_miniature = await db.create_miniature(miniature_create, current_user_id)
                created_miniatures.append(created_miniature)
            except Exception as e:
                # Log error but continue with other miniatures
                print(f"Error creating miniature '{miniature_create.name}': {e}")
                continue
        
        return {
            "message": f"Successfully imported {len(created_miniatures)} miniatures",
            "imported_count": len(created_miniatures),
            "total_in_file": len(imported_miniatures),
            "replaced_existing": replace_existing
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.get("/miniatures/{miniature_id}", response_model=Miniature)
async def get_miniature(
    miniature_id: UUID,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Miniature:
    """Get a specific miniature by ID for the authenticated user."""
    miniature = await db.get_miniature(miniature_id, current_user_id)
    if miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    return miniature


@app.put("/miniatures/{miniature_id}", response_model=Miniature)
async def update_miniature(
    miniature_id: UUID,
    miniature_update: MiniatureUpdate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> Miniature:
    """Update an existing miniature for the authenticated user."""
    updated_miniature = await db.update_miniature(miniature_id, miniature_update, current_user_id)
    if updated_miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    return updated_miniature


@app.delete("/miniatures/{miniature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_miniature(
    miniature_id: UUID,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> None:
    """Delete a miniature for the authenticated user."""
    success = await db.delete_miniature(miniature_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )


# Status log endpoints
@app.post("/miniatures/{miniature_id}/status-logs", response_model=StatusLogEntry, status_code=status.HTTP_201_CREATED)
async def add_status_log(
    miniature_id: UUID,
    log_data: StatusLogEntryCreate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> StatusLogEntry:
    """Add a manual status log entry to a miniature."""
    miniature = await db.add_status_log_entry(miniature_id, log_data, current_user_id)
    if miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miniature with ID {miniature_id} not found"
        )
    # Return the last status log entry (the one we just added)
    return miniature.status_history[-1]


@app.put("/miniatures/{miniature_id}/status-logs/{log_id}", response_model=StatusLogEntry)
async def update_status_log(
    miniature_id: UUID,
    log_id: UUID,
    log_update: StatusLogEntryUpdate,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> StatusLogEntry:
    """Update a status log entry."""
    updated_miniature = await db.update_status_log_entry(miniature_id, log_id, log_update, current_user_id)
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
async def delete_status_log(
    miniature_id: UUID,
    log_id: UUID,
    db: MiniatureDB = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
) -> None:
    """Delete a manual status log entry."""
    updated_miniature = await db.delete_status_log_entry(miniature_id, log_id, current_user_id)
    if updated_miniature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status log entry with ID {log_id} not found or cannot be deleted"
        )


@app.post("/admin/migrate-games")
async def migrate_games_endpoint(
    db: MiniatureDB = Depends(get_db)
):
    """Admin endpoint to add missing games to the database."""
    try:
        # All games that should be in the database
        expected_games = [
            ("Warhammer 40,000", "The iconic grimdark sci-fi wargame"),
            ("Age of Sigmar", "Fantasy battles in the Mortal Realms"),
            ("Warhammer: The Old World", "Classic fantasy battles in the Old World"),
            ("Horus Heresy", "The galaxy-spanning civil war in the 31st millennium"),
            ("Kill Team", "Small-scale skirmish battles in the 40K universe"),
            ("Warcry", "Fast-paced skirmish combat in Age of Sigmar"),
            ("Warhammer Underworlds", "Competitive deck-based skirmish game"),
            ("Adeptus Titanicus", "Epic-scale Titan warfare"),
            ("Necromunda", "Gang warfare in the underhive"),
            ("Blood Bowl", "Fantasy football with violence"),
            ("Middle-earth SBG", "Battle in Tolkien's world"),
            ("Bolt Action", "World War II historical wargaming"),
            ("Flames of War", "World War II tank combat"),
            ("SAGA", "Dark Age skirmish gaming"),
            ("Kings of War", "Mass fantasy battles"),
            ("Infinity", "Sci-fi skirmish with anime aesthetics"),
            ("Malifaux", "Gothic horror skirmish game"),
            ("Warmachine/Hordes", "Steampunk fantasy battles"),
            ("X-Wing", "Star Wars space combat"),
            ("Star Wars: Legion", "Ground battles in the Star Wars universe"),
            ("BattleTech", "Giant robot combat"),
            ("Dropzone Commander", "10mm sci-fi warfare"),
            ("Guild Ball", "Fantasy sports meets skirmish gaming"),
            ("D&D / RPG", "Dungeons & Dragons and RPG miniatures"),
            ("Pathfinder", "Fantasy RPG miniatures"),
            ("Frostgrave", "Wizard warband skirmish"),
            ("Mordheim", "Skirmish in the City of the Damned"),
            ("Gaslands", "Post-apocalyptic vehicular combat"),
            ("Zombicide", "Cooperative zombie survival"),
            ("Trench Crusade", "Grimdark alternate history warfare"),
            ("Other Game System", "Custom or unlisted game systems")
        ]
        
        # Get current games
        current_games = await db.get_all_games()
        current_game_names = [game.name for game in current_games]
        
        # Find missing games
        missing_games = []
        for name, description in expected_games:
            if name not in current_game_names:
                missing_games.append((name, description))
        
        if not missing_games:
            return {
                "message": "All games are already present",
                "total_games": len(current_games),
                "added_games": 0
            }
        
        # Add missing games
        added_games = []
        failed_games = []
        
        for name, description in missing_games:
            try:
                await db.create_game(name, description)
                added_games.append(name)
            except Exception as e:
                failed_games.append({"name": name, "error": str(e)})
        
        # Get final count
        final_games = await db.get_all_games()
        
        return {
            "message": f"Migration complete! Added {len(added_games)} games",
            "total_games": len(final_games),
            "added_games": len(added_games),
            "added_game_names": added_games,
            "failed_games": failed_games
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """Delete a user (admin only - for now, any authenticated user can delete)."""
    user_db = UserDB()
    
    # Check if user exists
    user = await user_db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the user
    success = await user_db.delete_user(user_id)
    
    if success:
        return {"message": f"User {user.email} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete user")


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