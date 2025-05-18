from fastapi import APIRouter, HTTPException, status

from . import functions

router = APIRouter(
    prefix="/sequence_search",
)


@router.post("/")
async def search_sequence(data: str, query_type: str):
    """
    Perform BLAST search on a given DNA sequence.
    """
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A DNA sequence is required",
        )

    try:
        genes_results = functions.fetch_gene(data, query_type == "gene")
        proteins_results = functions.fetch_protein(data, query_type == "protein")
        
        results =  {
            "gene_results": genes_results,
            "protein_results": proteins_results,
               
        }
        return results
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(ve)}",
        )
    except ConnectionError as ce:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(ce)}",
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Request timed out: {str(te)}",
        )
    except FileNotFoundError as fnfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(fnfe)}",
        )
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {str(pe)}",
        )
    except TypeError as te:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Type error: {str(te)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during BLAST search: {str(e)}",
        )
