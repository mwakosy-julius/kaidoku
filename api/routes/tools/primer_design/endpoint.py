from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .functions import design_primers

router = APIRouter(prefix="/primer_design")

class PrimerRequest(BaseModel):
    sequence: str
    primer_len: int = 20
    tm_min: float = 50
    tm_max: float = 65
    gc_min: float = 40
    gc_max: float = 60

@router.post("/")
def design_primers_endpoint(request: PrimerRequest):
    result = design_primers(
        request.sequence,
        primer_len=request.primer_len,
        tm_min=request.tm_min,
        tm_max=request.tm_max,
        gc_min=request.gc_min,
        gc_max=request.gc_max
    )
    if result:
        return result
    raise HTTPException(status_code=404, detail="No suitable primers found.")
