from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist, squareform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

# Example distance matrix for sequences
# Replace this with real computed distances
# sequences = ["AAGTCC", "AAGCCC", "TAGTCC", "AAGTGC"]

def parse_fasta_sequences(fasta_input):
    sequences = []
    current_sequence = ""
    lines = fasta_input.strip().splitlines()
    for line in lines:
        if line.startswith(">"):
            if current_sequence:
                sequences.append(current_sequence)
                current_sequence = ""
        else:
            current_sequence += line.strip()
    if current_sequence:
        sequences.append(current_sequence)
    return sequences

def parse_fasta(fasta_text):
    sequences = {}
    current_sequence_name = None
    current_sequence = []

    for line in fasta_text.strip().split('\n'):
        if line.startswith('>'):
            if current_sequence_name:
                sequences[current_sequence_name] = ''.join(current_sequence)
            current_sequence_name = line[1:].strip() 
            current_sequence = []
        else:
            current_sequence.append(line.strip())

    if current_sequence_name:
        sequences[current_sequence_name] = ''.join(current_sequence)

    return sequences

def simple_substitution_distance(seq1, seq2):
    """Simple model to compute genetic substitution distance."""
    # Assuming sequences are already aligned
    mismatches = sum(1 for a, b in zip(seq1, seq2) if a != b)
    return mismatches / len(seq1)

def build_distance_matrix(sequences):
    """Create a distance matrix based on pairwise sequence distances."""
    n = len(sequences)
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i < j:
                distance_matrix[i][j] = simple_substitution_distance(
                    sequences[i], sequences[j]
                )
                distance_matrix[j][i] = distance_matrix[i][j]
    return distance_matrix

def phylogenetic_tree(sequence_dict):
    """Generates a Neighbor-Joining phylogenetic tree."""
    sequence_names = list(sequence_dict.keys())
    sequence_list = list(sequence_dict.values())

    # Ensure sequences are aligned
    aligned_length = set(len(seq) for seq in sequence_list)
    if len(aligned_length) > 1:
        raise ValueError("All sequences must have the same length for alignment.")

    # Compute distance matrix
    distance_matrix = build_distance_matrix(sequence_list)

    # Visualize tree using hierarchical clustering
    plt.figure(figsize=(8, 5))
    linked = linkage(squareform(distance_matrix), 'average')
    dendrogram(linked,
            orientation='left',
               labels=sequence_names,
               distance_sort='descending',
               show_leaf_counts=True)
    plt.title("Phylogenetic Tree")
    plt.xlabel("Distance")
    # plt.show()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return plot_url
    
