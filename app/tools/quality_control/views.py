from django.shortcuts import render
from .forms import SequenceForm
from . import functions
import os

def quality_control(request):
    form = SequenceForm()
    results = None

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file_path = uploaded_file.file.path

            sequences, qualities = parse_fastq(file_path)
            gc_contents = calculate_gc_content(sequences)
            quality_scores = calculate_quality_distribution(qualities)

            results = {
                "gc_contents": gc_contents,
                "quality_scores": quality_scores
            }
    
    return render(request, "quality_control.html", {"form": form, "results": results})