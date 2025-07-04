from fastapi import APIRouter, HTTPException, status

from api.routes.tools.consensus_maker.functions import parse_fasta, generate_consensus

router = APIRouter(
    prefix="/consensus_maker",
)


@router.post("/")
async def create_consensus(data: str):
    """
    Create a consensus sequence from multiple DNA sequences.
    """
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one DNA sequence is required",
        )

    try:
        sequences = parse_fasta(data)
        consensus = generate_consensus(sequences)
        return {"consensus": consensus}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during consensus creation: {str(e)}",
        )
