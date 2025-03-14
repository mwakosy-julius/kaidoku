from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user

from functions import perform_blastp

router = APIRouter(
    prefix="/blast",
    tags=["blast"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/")
async def blast_sequence(data: str):
    """
    Perform BLAST search on a given DNA sequence.
    """
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A DNA sequence is required",
        )

    try:
        results = perform_blastp(data)
        return {"results": results}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during BLAST search: {str(e)}",
        )
