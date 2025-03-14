from django.shortcuts import render
from . import functions

def motif_finder(request):
    k_length = 6
    if request.method == 'POST':
        sequences = request.POST.get('sequence', '')
        sequences = functions.parse_fasta_sequences(sequences)
        motifs = functions.find_motif(sequences, k_length)
        motif = functions.generate_consensus(motifs)
    
    return render(request, "motif.html", {'motif': motif})