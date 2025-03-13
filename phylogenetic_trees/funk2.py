import re
import matplotlib.pyplot as plt
import io
import base64
import ete3
from ete3 import Tree, TreeStyle
import PyQt5

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

def hamming_distance(seq1, seq2):
    return sum(c1 != c2 for c1, c2 in zip(seq1, seq2))

def create_distance_matrix(sequences):
    labels = list(sequences.keys())
    n = len(labels)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dist = hamming_distance(sequences[labels[i]], sequences[labels[j]])
            matrix[i][j] = dist
            matrix[j][i] = dist
    return labels, matrix

def find_min_pair(matrix, labels):
    min_dist = float('inf')
    min_pair = (0, 1)
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            if matrix[i][j] < min_dist and matrix[i][j] > 0:
                min_dist = matrix[i][j]
                min_pair = (i, j)
    return min_pair

def neighbor_joining(labels, matrix):
    if len(labels) <= 2:
        if len(labels) == 2:
            return f"({labels[0]}:{matrix[0][1]/2},{labels[1]}:{matrix[0][1]/2})"
        return labels[0]
    
    i, j = find_min_pair(matrix, labels)
    dist_ij = matrix[i][j]
    
    new_node = f"({labels[i]}:{dist_ij/2},{labels[j]}:{dist_ij/2})"
    new_labels = [label for k, label in enumerate(labels) if k != i and k != j]
    new_labels.append(new_node)
    
    n = len(matrix)
    new_matrix = [[0] * (n - 1) for _ in range(n - 1)]
    for k in range(n):
        if k != i and k != j:
            new_i = new_labels.index(labels[k]) if labels[k] in new_labels else n - 2
            for m in range(k + 1, n):
                if m != i and m != j:
                    new_j = new_labels.index(labels[m]) if labels[m] in new_labels else n - 2
                    new_matrix[new_i][new_j] = matrix[k][m]
                    new_matrix[new_j][new_i] = matrix[k][m]
            if new_i < n - 2:
                dist_to_new = (matrix[k][i] + matrix[k][j]) / 2
                new_matrix[new_i][n - 2] = dist_to_new
                new_matrix[n - 2][new_i] = dist_to_new
    
    return neighbor_joining(new_labels, new_matrix)

def render_phylogenetic_tree(newick_str):
    tree = Tree(newick_str, format=1)
    
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_branch_length = True
    ts.show_branch_support = True
    
    img_file = 'tree.png'
    tree.render(img_file, w=500, tree_style=ts)
    
    with open(img_file, 'rb') as img:
        img_base64 = base64.b64encode(img.read()).decode('utf-8')
    
    return img_base64