from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/api/blogs", tags=["blogs"])

DUMMY_BLOGS = [
    {"id": 1, "title": "Welcome to Kaidoku", "content": "First post!", "image": "", "description": "Intro"},
    {"id": 2, "title": "New Features", "content": "We added new tools.", "image": "", "description": "Update"},
]

@router.get("")
def get_blogs():
    return DUMMY_BLOGS

@router.get("/{id}")
def get_blog(id: int):
    for b in DUMMY_BLOGS:
        if b["id"] == id:
            return b
    raise HTTPException(status_code=404, detail="Blog not found")

@router.post("")
def add_blog(blog: dict):
    new_id = max(b["id"] for b in DUMMY_BLOGS) + 1
    blog["id"] = new_id
    DUMMY_BLOGS.append(blog)
    return blog