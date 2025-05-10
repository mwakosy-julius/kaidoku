import numpy as np
from fastapi import HTTPException

# Function to compute Hamming distance matrix
def compute_distance_matrix(fasta_input):
    lines = fasta_input.strip().split("\n")
    sequences = {}
    current_seq = ""
    current_name = None
    
    for line in lines:
        if line.startswith(">"):
            if current_name and current_seq:
                sequences[current_name] = current_seq
            current_name = line[1:].strip()
            current_seq = ""
        else:
            current_seq += line.strip()
    if current_name and current_seq:
        sequences[current_name] = current_seq
    
    if len(sequences) < 2:
        raise HTTPException(status_code=400, detail="At least 2 sequences required")
    
    names = list(sequences.keys())
    seqs = list(sequences.values())
    n = len(seqs)
    
    seq_length = len(seqs[0])
    # if not all(len(seq) == seq_length for seq in seqs):
    #     raise HTTPException(status_code=400, detail="All sequences must be the same length")
    
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            diff = sum(a != b for a, b in zip(seqs[i], seqs[j]))
            dist = diff / seq_length
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    
    return dist_matrix, names

# Neighbor-Joining algorithm
def neighbor_joining(dist_matrix, names):
    n = len(dist_matrix)
    if n <= 1:
        return None
    
    nodes = [f"{name}:0" for name in names]
    matrix = dist_matrix.copy()
    
    while n > 2:
        Q = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                total_dist = sum(matrix[i]) + sum(matrix[j]) - 2 * matrix[i, j]
                Q[i, j] = (n - 2) * matrix[i, j] - total_dist
                Q[j, i] = Q[i, j]
        
        i, j = np.unravel_index(np.argmin(Q), Q.shape)
        if i > j:
            i, j = j, i
        
        total_dist_i = sum(matrix[i]) / (n - 2)
        total_dist_j = sum(matrix[j]) / (n - 2)
        d_ij = matrix[i, j]
        branch_i = (d_ij + total_dist_i - total_dist_j) / 2
        branch_j = d_ij - branch_i
        
        new_node = f"({nodes[i]}:{branch_i:.4f},{nodes[j]}:{branch_j:.4f})"
        nodes.pop(j)
        nodes.pop(i)
        nodes.append(new_node)
        
        new_dist = np.zeros((n - 1))
        for k in range(n):
            if k != i and k != j:
                new_dist[k if k < i else (k - 1 if k < j else k - 2)] = (matrix[i, k] + matrix[j, k] - d_ij) / 2
        
        n -= 1
        matrix = np.delete(matrix, [i, j], axis=0)
        matrix = np.delete(matrix, [i, j], axis=1)
        matrix = np.vstack([matrix, new_dist[:-1]])
        matrix = np.hstack([matrix, new_dist[:, None]])
    
    if n == 2:
        return f"({nodes[0]}:{matrix[0, 1]/2:.4f},{nodes[1]}:{matrix[0, 1]/2:.4f});"
    return nodes[0] + ";"
    