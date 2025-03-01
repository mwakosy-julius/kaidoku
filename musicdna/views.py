from django.shortcuts import render
from . import functions, funk
import random

def musicdna(request):
    result = ''
    if request.method == 'POST':
        sequence = request.POST.get('sequence')  
        if sequence:
            sequence = funk.sequence_validator(sequence)
            if functions.is_dna(sequence):
                # melody = functions.melody_maker(sequence)
                # functions.play_melody(melody)
                apply_inversion = random.choice([True, False])
                funk.play_musicdna(sequence, use_inversion=apply_inversion)
            else:
                return HttpResponse("Invalid input data")

    context = {'result': result}
    return render(request, "musicdna.html", context) 
