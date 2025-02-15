from django.shortcuts import render
from . import functions

def variant_calling(request):
    summary = None

    if request.method == 'POST':
        reference = request.POST.get('reference', '') 
        sequence_input = request.POST.get('sequence', '').strip()
        sequences = functions.parse_fasta_sequences(sequence_input)
        reads = functions.generate_reads(sequences, read_length=10, coverage=3)
        summary = functions.call_variants(reference, reads, threshold=0.7)
    
    return render(request, "variant_calling.html", {"summary": summary})