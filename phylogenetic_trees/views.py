from django.shortcuts import render
from . import functions, funk2
import json

def phylogenetic_trees(request):
    tree = None
    if request.method == "POST":
        sequence = request.POST.get('sequence', '').strip()
        sequences = funk2.parse_fasta(sequence)
        labels, dist_matrix = funk2.create_distance_matrix(sequences)
        newick_data = funk2.neighbor_joining(labels, dist_matrix) + ";"
        tree = funk2.render_phylogenetic_tree(newick_data)
          
    return render(request, "trees.html", {'tree': tree})
