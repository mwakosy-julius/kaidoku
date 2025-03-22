from fastapi import APIRouter, Request
from . import functions

def phylogenetic_trees(request):
    plot_url = None
    if request.method == "POST":
        sequence = request.POST.get('sequence', '').strip()
        sequences = functions.parse_fasta(sequence)
        plot_url = functions.phylogenetic_tree(sequences)
          
    return render(request, "trees.html", {"plot_url": plot_url})
