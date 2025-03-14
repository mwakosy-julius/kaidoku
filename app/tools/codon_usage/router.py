from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_active_user

from functions import parse_fasta_sequences, generate_consensus

router = APIRouter(
    prefix="/codon_usage",
    tags=["codon usage"],
    dependencies=[Depends(get_current_active_user)],
)


class CodonUsageRequest(BaseModel):
    sequence: str


class CodonUsageResponse(BaseModel):
    consensus: str


@router.post("/", response_model=CodonUsageResponse)
async def calculate_codon_usage(data: CodonUsageRequest):
    """
    Calculate codon usage from a DNA sequence.
    """
    if not data.sequence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A DNA sequence is required",
        )

    try:
        # Parse the input sequence
        sequences = parse_fasta_sequences(data.sequence)
        # Generate the consensus sequence
        consensus = generate_consensus(sequences)
        # Return the consensus sequence
        return {"consensus": consensus}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during codon usage calculation: {str(e)}",
        )
