from fastapi import APIRouter, HTTPException
from . import functions

router = APIRouter(
    prefix="/multiple_alignment",
)

@router.post('/')
def multiple_alignment(request):
    aligned_sequences = None

    if request.method == "POST":
        sequence = request.POST.get('sequence', '').strip()
        sequences = functions.parse_fasta_sequences(sequence)
        if len(sequences) >= 2:
            distance_matrix = functions.calculate_distance_matrix(sequences)
            guide = functions.guide_tree(distance_matrix)
            aligned_sequences = functions.progressive_alignment(sequences, guide)

    return {
        "aligned_sequences": aligned_sequences
    }
