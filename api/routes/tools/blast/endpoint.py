from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from . import functions

router = APIRouter(prefix="/blast")

class BlastRequest(BaseModel):
    sequence: str = Field(..., min_length=1, description="Raw or FASTA sequence")
    program: str = Field("blastn", pattern="^(blastn|blastp)$", description="BLAST program")
    database: str = Field("nt", description="BLAST database (e.g., nt, nr)")
    evalue: float = Field(1e-5, gt=0, le=10.0, description="E-value cutoff")
    max_results: int = Field(10, ge=1, le=100, description="Max number of results")
    organism: Optional[str] = Field(None, description="Optional organism filter")

class BlastResult(BaseModel):
    organism: str
    accession: str
    hit_id: str
    percentage_identity: float
    query_coverage: float
    evalue: float
    bit_score: float
    gaps: int

class BlastResponse(BaseModel):
    results: List[BlastResult]
    errors: List[str]

@router.post("/", response_model=BlastResponse)
async def run_blast(request: BlastRequest):
    """Run BLAST query for gene or protein sequences."""
    try:
        results = functions.blast_sequence(
            sequence=request.sequence,
            program=request.program,
            database=request.database,
            evalue=request.evalue,
            max_results=request.max_results,
            organism=request.organism
        )
        return BlastResponse(results=results, errors=[])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BLAST failed: {str(e)}")