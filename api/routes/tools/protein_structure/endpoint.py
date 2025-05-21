from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from . import functions

router = APIRouter(prefix="/protein_structure")

class PredictionRequest(BaseModel):
    sequence: str

@router.post("/")
async def predict_structure(request: PredictionRequest):
    """
    Predict protein structure from amino acid sequence.
    Returns PDB data and confidence score.
    """
    if not request.sequence.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amino acid sequence is required"
        )

    try:
        result = functions.predict_structure(request.sequence)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting structure: {str(e)}"
        )