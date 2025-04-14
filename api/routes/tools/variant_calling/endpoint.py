from fastapi import APIRouter, HTTPException
from . import functions

router = APIRouter(
    prefix="/variant_calling",
)

@router.get("/")
def variant_call(ref_fasta: str, sample_fasta: str):
    ref = functions.parse_fasta(ref_fasta)
    sample = functions.parse_fasta(sample_fasta)
    if not ref or not sample:
        raise HTTPException(status_code=400, detail="Invalid FASTA")
    variants = functions.call_variants(ref, sample)
    return {"variants": variants}