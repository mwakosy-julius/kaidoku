from django.shortcuts import render
from . import functions

def multiple_alignment(request):
    aligned_sequences = None

    if request.method == "POST":
        sequence = request.POST.get('sequence', '').strip()
        sequences = functions.parse_fasta_sequences(sequence)
        if len(sequences) >= 2:
            distance_matrix = functions.calculate_distance_matrix(sequences)
            guide = functions.guide_tree(distance_matrix)
            aligned_sequences = functions.progressive_alignment(sequences, guide)
    
    return render(request, "multiple_alignment.html", {
        "aligned_sequences": aligned_sequences
    })