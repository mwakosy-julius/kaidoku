from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel


from api.routes.tools.codon_usage.functions import calculate_codon_usage, generate_codon_usage_table

router = APIRouter(
    prefix="/codon_usage",
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
        sequences = calculate_codon_usage(data.sequence)
        # Generate the consensus sequence
        consensus = generate_codon_usage_table(sequences)
        # Return the consensus sequence
        return {"consensus": consensus}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during codon usage calculation: {str(e)}",
        )
