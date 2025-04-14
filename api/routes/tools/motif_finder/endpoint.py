from fastapi import APIRouter, HTTPException
from . import functions

router = APIRouter(
    prefix="/motif_finder",
)

@router.post("/")
def find_motifs(fasta: str):
    """
    Find motifs in FASTA sequences using Gibbs Sampling.
    """
    sequences = functions.parse_fasta(fasta)
    if len(sequences) < 2:
        raise HTTPException(status_code=400, detail="At least two sequences required")
    
    motif_length = functions.estimate_max_motif_length(sequences)
    motifs, score = functions.gibbs_sampling(sequences, motif_length)
    if not motifs:
        raise HTTPException(status_code=404, detail="No motifs found")
    
    consensus = functions.motifs_to_consensus(motifs)
    positions = functions.find_motif_positions(sequences, consensus)
    
    return {
        "consensus": consensus,
        "score": score,
        "motif_length": motif_length,
        "positions": positions
    }
