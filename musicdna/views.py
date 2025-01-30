from django.shortcuts import render
from . import functions

def musicdna(request):
    result = ''
    if request.method == 'POST':
        sequence = request.POST.get('sequence')  
        if sequence:
            sequence = functions.sequence_validator(sequence)
            if functions.is_dna(sequence):
                melody = functions.melody_maker(sequence)
                functions.play_melody(melody)
            else:
                return HttpResponse("Invalid input data")

    context = {'result': result}
    return render(request, "musicdna.html", context) 
