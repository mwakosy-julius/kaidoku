from fastapi import APIRouter, HTTPException
from . import functions

router = APIRouter(
    prefix="/variant_calling",
)

@router.get("/")
def variant_call(ref_fasta: str, sample_fasta: str):
    ref = functions.format_sequence(ref_fasta)
    sample = functions.format_sequence(sample_fasta)
    if functions.is_dna(ref) and functions.is_dna(sample):
        variants = functions.call_variants(ref, sample)
    else:
        raise HTTPException(status_code=400, detail="Invalid FASTA")
    return {"variants": variants}