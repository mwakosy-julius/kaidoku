from fastapi import APIRouter

from . import functions

router = APIRouter(
    prefix="/motif_finder",
)


@router.post("/")
def motif_finder(request):
    k_length = 6
    motif = None
    if request.method == 'POST':
        sequences = request.POST.get('sequence', '')
        sequences = functions.parse_fasta_sequences(sequences)
        motifs = functions.find_motif(sequences, k_length)
        motif = functions.generate_consensus(motifs)

    return {
        "motif": motif,
    }
