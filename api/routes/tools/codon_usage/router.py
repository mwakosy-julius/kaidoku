from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from api.routes.tools.codon_usage.functions import (
    format_sequence,
    is_dna,
    calculate_codon_usage,
    generate_codon_usage_table,
)

router = APIRouter(prefix="/codon_usage")


class CodonUsageRequest(BaseModel):
    sequence: str


class CodonUsageResponse(BaseModel):
    codon_usage: dict
    table: str


@router.post("/", response_model=CodonUsageResponse)
async def calculate_codon_usage_endpoint(data: CodonUsageRequest):
    """
    Calculate codon usage from a DNA sequence.
    """
    if not data.sequence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A DNA sequence is required",
        )

    try:
        codon_sequence = format_sequence(data.sequence)
        if not is_dna(codon_sequence):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect DNA sequence",
            )
        codon_usage = calculate_codon_usage(codon_sequence)
        table = generate_codon_usage_table(codon_usage)
        return {"codon_usage": codon_usage, "table": table}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during codon usage calculation: {str(e)}",
        )
