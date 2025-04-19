from fastapi import HTTPException, status, APIRouter
from pydantic import BaseModel
from .functions import align_sequences

router = APIRouter(prefix="/align")


class AlignRequest(BaseModel):
    sequences: str
    seq_type: str


class AlignResponse(BaseModel):
    alignment: str


@router.post("/", response_model=AlignResponse)
async def align(request: AlignRequest):
    """
    Align sequences using Clustal Omega API.

    Args:
        request: Contains sequences (FASTA) and seq_type (dna/protein).

    Returns:
        Alignment in Clustal format.

    Raises:
        HTTPException: For invalid inputs or API errors.
    """
    try:
        alignment = align_sequences(request.sequences, request.seq_type)
        if alignment is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Alignment failed",
            )
        return {"alignment": alignment}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
