from django.shortcuts import render
from . import functions

def dna_assembler(request):
    assembled_sequence = None
    sequences = None
    
    if request.method == "POST":
        sequences = request.POST.get("sequence").split()  # User enters sequences separated by space
        assembled_sequence = functions.assemble_dna(sequences)
        
    
    return render(request, "dna_assembler.html", {'assembled_sequence': assembled_sequence})
