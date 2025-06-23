from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/docs", tags=["docs"])

DUMMY_DOCS = [
    {"slug": "getting-started", "title": "Getting Started", "content": "How to use Kaidoku."},
    {"slug": "faq", "title": "FAQ", "content": "Frequently asked questions."},
]

@router.get("")
def get_docs():
    return DUMMY_DOCS

@router.get("/{slug}")
def get_doc(slug: str):
    for d in DUMMY_DOCS:
        if d["slug"] == slug:
            return d
    raise HTTPException(status_code=404, detail="Doc not found")