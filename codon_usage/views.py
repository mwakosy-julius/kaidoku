from django.shortcuts import render
from . import functions

def codon_usage(request):
    context = {'sequence': '', 'result_table': ''}
    
    if request.method == 'POST':
        sequence = request.POST.get('sequence', '').strip()
        result = functions.calculate_codon_usage(sequence)
        result_table = functions.generate_codon_usage_table(result)
        
        context.update({'sequence': sequence, 'result_table': result_table})
    return render(request, "codon_usage.html", context)
