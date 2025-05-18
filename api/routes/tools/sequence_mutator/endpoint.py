from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from . import functions

router = APIRouter(prefix="/mutator")

class MutationRequest(BaseModel):
    sequence: str
    sequence_type: str  # "dna" or "protein"
    mutation_type: str  # "substitution", "insertion", "deletion"
    mutation_rate: float

@router.post("/")
async def mutate_sequence(request: MutationRequest):
    """
    Mutate a DNA or protein sequence.
    Returns original sequence, mutated sequence, and mutation details.
    """
    if not request.sequence.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sequence is required"
        )

    if request.sequence_type not in ["dna", "protein"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sequence type must be 'dna' or 'protein'"
        )

    if request.mutation_type not in ["substitution", "insertion", "deletion"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mutation type must be 'substitution', 'insertion', or 'deletion'"
        )

    if not (0 <= request.mutation_rate <= 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mutation rate must be between 0 and 1"
        )

    try:
        result = functions.mutate_sequence(
            request.sequence,
            request.sequence_type,
            request.mutation_type,
            request.mutation_rate
        )
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error mutating sequence: {str(e)}"
        )