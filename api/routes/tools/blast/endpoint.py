from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from . import functions
from . import former_blast

router = APIRouter(prefix="/blast")

class BlastRequest(BaseModel):
    sequence: str
    seqType: str = "dna"
    
class BlastResult(BaseModel):
    organism: str
    hit_id: str
    percentage_match: float

class BlastResponse(BaseModel):
    results: List[BlastResult]
    errors: List[str]

@router.post("/", response_model=BlastResponse)
async def run_blast(request: BlastRequest):
    """Run BLAST query for gene or protein sequences."""
    sequence = request.sequence
    seqType = request.seqType

    sequence = former_blast.format_sequence(sequence)
    try:
        if seqType == "dna":
            results = former_blast.perform_blastn(sequence)
        elif seqType == "protein":
            results = former_blast.perform_blastp(sequence)
        else:
            raise ValueError("Invalid sequence type. Must be 'dna' or 'protein'.")

        return BlastResponse(results=results, errors=[])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BLAST failed: {str(e)}")