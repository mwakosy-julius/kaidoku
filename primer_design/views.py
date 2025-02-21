from django.shortcuts import render
from . import functions

def primer_design(request):
    primers = None
    if request.method == "POST":
            sequence = request.POST.get("sequence").strip().upper()
            primer_length = int(request.POST.get("primer_length", 20))
            min_gc = int(request.POST.get("min_gc", 40))
            max_gc = int(request.POST.get("max_gc", 60))
            min_tm = int(request.POST.get("min_tm", 50))
            max_tm = int(request.POST.get("max_tm", 65))

            primers = functions.find_primers(sequence, primer_length, min_gc, max_gc, min_tm, max_tm)
    
    return render(request, "primer_design.html", {'primers': primers})
