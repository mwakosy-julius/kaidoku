from fastapi import APIRouter, HTTPException, status
from . import functions
from pydantic import BaseModel

class Sequence(BaseModel):
    sequence: str

class MusicResponse(BaseModel):
    melody: list[str]

router = APIRouter(prefix="/musicdna")

@router.post("/", response_model=MusicResponse)
def musicdna(request: Sequence):
    if not request.sequence.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sequence is required")
    
    sequence = functions.sequence_validator(request.sequence)
    if not functions.is_dna(sequence):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid DNA sequence")
    
    melody = functions.melody_maker(sequence)
    return {"melody": melody}