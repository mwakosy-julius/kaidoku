from django.shortcuts import render
from . import functions

def musicdna(request):
    result = ''
    if request.method == 'POST':
        sequence = request.POST.get('sequence')  
        if sequence:
            sequence = functions.sequence_validator(sequence)
            if functions.is_dna(sequence):
                melody = functions.melody_maker(sequence, scale='major')
                harmony = functions.harmony_maker(sequence, scale='major')
                rhythm = functions.generate_rhythm(sequence)
                functions.play_melody_with_harmony(melody, harmony)
            else:
                return HttpResponse("Invalid input data")

    context = {'result': result}
    return render(request, "musicdna.html", context) 
