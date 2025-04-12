from fastapi import APIRouter, HTTPException
from . import functions

router = APIRouter(
    prefix="/phylogenetic_trees",
)

@router.post("/")
def build_phylogenetic_tree(fasta: str):
    try:
        dist_matrix, names = functions.compute_distance_matrix(fasta)
        tree_data = functions.neighbor_joining(dist_matrix, names)
        if not tree_data:
            raise HTTPException(status_code=500, detail="Failed to build tree")
        return {"newick": tree_data}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")