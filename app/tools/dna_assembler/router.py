from fastapi import APIRouter, HTTPException, status

from app.models.dna import DNASequences, DNASequence
from app.tools.dna_assembler.functions import assemble_dna

router = APIRouter(
    prefix="/dna_assembler",
)


@router.post("/", response_model=DNASequence)
async def assemble_sequences(data: DNASequences):
    """
    Assemble multiple DNA sequences into a single contig.
    """
    if not data.sequences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one DNA sequence is required",
        )

    try:
        result = assemble_dna(data.sequences)
        return {"sequence": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during DNA assembly: {str(e)}",
        )
