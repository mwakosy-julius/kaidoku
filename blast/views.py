from django.shortcuts import render
from . import functions

def blast(request):
    results = ''
    if request.method == "POST":
        text = request.POST.get("text", "")
        results = functions.perform_blastp(text)

    return render(request, "blast.html", {"results": results})