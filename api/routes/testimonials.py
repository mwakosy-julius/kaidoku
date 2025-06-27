from fastapi import APIRouter

router = APIRouter(prefix="/api/testimonials", tags=["testimonials"])

DUMMY_TESTIMONIALS = [
    {"id": 1, "title": "Great Tool!", "content": "Kaidoku helped my research.", "image": ""},
    {"id": 2, "title": "Easy to Use", "content": "Very user-friendly.", "image": ""},
]

@router.get("")
def get_testimonials():
    return DUMMY_TESTIMONIALS

@router.post("")
def add_testimonial(testimonial: dict):
    new_id = max(t["id"] for t in DUMMY_TESTIMONIALS) + 1
    testimonial["id"] = new_id
    DUMMY_TESTIMONIALS.append(testimonial)
    return testimonial