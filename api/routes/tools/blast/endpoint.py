from fastapi import APIRouter, HTTPException, status

from . import functions

router = APIRouter(
    prefix="/blast",
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
        gene_blast_results = functions.perform_blastn(data)
        protein_blast_results = functions.perform_blastp(data)
        results =  {
            "gene_blast_results": gene_blast_results,
            "protein_blast_results": protein_blast_results,    
        }
        return results
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(ve)}",
        )