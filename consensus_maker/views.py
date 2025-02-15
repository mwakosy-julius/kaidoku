from django.shortcuts import render
from . import functions

def consensus_maker(request):
    consensus = None

    if request.method == "POST":
        sequence = request.POST.get('sequence', '').strip()
        sequences = functions.parse_fasta_sequences(sequence)
        consensus = functions.generate_consensus(sequences)
    
    return render(request, "consensus_maker.html", {'consensus': consensus})
