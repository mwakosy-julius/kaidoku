from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
# from .core.security import get_current_user

router = APIRouter(prefix="/api", tags=["dashboard"])

def get_current_user():
    return "dummy_user"  # Placeholder for user authentication


currentr_user = lambda: "dummy_user"  # Placeholder for user authentication

# Dummy data
DUMMY_COLLECTIONS = [
    {"id": 1, "name": "Genomics Tools", "items": ["BLAST", "GC Content"]},
    {"id": 2, "name": "Protein Analysis", "items": ["Motif Finder"]},
]
DUMMY_ACTIVITY = [
    {"id": 1, "action": "Used BLAST", "timestamp": "2024-06-01T10:00:00"},
    {"id": 2, "action": "Created project 'Genome Study'", "timestamp": "2024-06-02T12:00:00"},
]
DUMMY_PROJECTS = [
    {"id": 1, "name": "Genome Study", "description": "Analysis of genome data."},
    {"id": 2, "name": "Protein Project", "description": "Protein structure analysis."},
]
DUMMY_SAVED_TOOLS = [
    {"id": 1, "tool": "BLAST", "config": {"evalue": 0.001}},
    {"id": 2, "tool": "GC Content", "config": {"window": 100}},
]

# 1. Library Collections
@router.get("/library")
def get_library_collections(current_user=Depends(get_current_user)):
    return DUMMY_COLLECTIONS

@router.get("/library/{id}")
def get_library_collection(id: int, current_user=Depends(get_current_user)):
    for c in DUMMY_COLLECTIONS:
        if c["id"] == id:
            return c
    raise HTTPException(status_code=404, detail="Collection not found")

# 2. Recent Activity
@router.get("/activity")
def get_recent_activity(current_user=Depends(currentr_user)):
    return DUMMY_ACTIVITY

# 3. Projects
@router.get("/projects")
def get_projects(current_user=Depends(get_current_user)):
    return DUMMY_PROJECTS

@router.get("/projects/{id}")
def get_project(id: int, current_user=Depends(get_current_user)):
    for p in DUMMY_PROJECTS:
        if p["id"] == id:
            return p
    raise HTTPException(status_code=404, detail="Project not found")

@router.post("/projects")
def create_project(project: Dict[str, Any], current_user=Depends(get_current_user)):
    new_id = max(p["id"] for p in DUMMY_PROJECTS) + 1
    project["id"] = new_id
    DUMMY_PROJECTS.append(project)
    return project

# 4. Saved Tools
@router.get("/saved-tools")
def get_saved_tools(current_user=Depends(get_current_user)):
    return DUMMY_SAVED_TOOLS

@router.post("/saved-tools")
def save_tool(tool: Dict[str, Any], current_user=Depends(get_current_user)):
    new_id = max(t["id"] for t in DUMMY_SAVED_TOOLS) + 1
    tool["id"] = new_id
    DUMMY_SAVED_TOOLS.append(tool)
    return tool

@router.delete("/saved-tools/{id}")
def delete_saved_tool(id: int, current_user=Depends(get_current_user)):
    for t in DUMMY_SAVED_TOOLS:
        if t["id"] == id:
            DUMMY_SAVED_TOOLS.remove(t)
            return {"detail": "Deleted"}
    raise HTTPException(status_code=404, detail="Tool not found")
