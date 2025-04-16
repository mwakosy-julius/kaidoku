import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
import re
from scipy.cluster.hierarchy import linkage, to_tree
from itertools import combinations

# Scoring matrices
DNAFULL = {
    ('A', 'A'): 5, ('A', 'T'): -4, ('A', 'C'): -4, ('A', 'G'): -4,
    ('T', 'T'): 5, ('T', 'A'): -4, ('T', 'C'): -4, ('T', 'G'): -4,
    ('C', 'C'): 5, ('C', 'A'): -4, ('C', 'T'): -4, ('C', 'G'): -4,
    ('G', 'G'): 5, ('G', 'A'): -4, ('G', 'T'): -4, ('G', 'C'): -4,
    ('-', '-'): 0, ('-', 'A'): -10, ('-', 'T'): -10, ('-', 'C'): -10, ('-', 'G'): -10,
    ('A', '-'): -10, ('T', '-'): -10, ('C', '-'): -10, ('G', '-'): -10
}

BLOSUM62 = {}  # Simplified; load from file in production
for aa1 in 'ARNDCQEGHILKMFPSTWYV-':
    for aa2 in 'ARNDCQEGHILKMFPSTWYV-':
        BLOSUM62[(aa1, aa2)] = -4 if aa1 != aa2 else 4 if aa1 != '-' else 0
        if aa1 == '-' or aa2 == '-':
            BLOSUM62[(aa1, aa2)] = -11 if aa1 == aa2 else -11  # Gap open
BLOSUM62.update({('A', 'A'): 4, ('R', 'R'): 5, ('N', 'N'): 6})  # Example scores

def parse_fasta(fasta: str, seq_type: str) -> List[Tuple[str, str]]:
    """Parse FASTA into (header, sequence) pairs."""
    sequences = []
    current_header = None
    current_seq = []
    lines = fasta.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if current_header and current_seq:
                seq = ''.join(current_seq).upper()
                if seq_type == 'nucleotide' and re.match(r'^[ATCGN-]+$', seq):
                    sequences.append((current_header, seq))
                elif seq_type == 'protein' and re.match(r'^[ARNDCQEGHILKMFPSTWYV-]+$', seq):
                    sequences.append((current_header, seq))
                current_seq = []
            current_header = line[1:]
        elif current_header:
            current_seq.append(line)
    
    if current_header and current_seq:
        seq = ''.join(current_seq).upper()
        if seq_type == 'nucleotide' and re.match(r'^[ATCGN-]+$', seq):
            sequences.append((current_header, seq))
        elif seq_type == 'protein' and re.match(r'^[ARNDCQEGHILKMFPSTWYV-]+$', seq):
            sequences.append((current_header, seq))
    
    if not sequences:
        raise ValueError(f"No valid {seq_type} sequences found")
    return sequences

def needleman_wunsch(seq1: str, seq2: str, scoring: Dict, seq_type: str) -> float:
    """Compute pairwise identity using Needleman-Wunsch."""
    gap_open = -11 if seq_type == 'protein' else -10
    gap_extend = -1 if seq_type == 'protein' else -10
    
    m, n = len(seq1), len(seq2)
    dp = np.zeros((m + 1, n + 1))
    
    for i in range(m + 1):
        dp[i, 0] = i * gap_open
    for j in range(n + 1):
        dp[0, j] = j * gap_open
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = dp[i-1, j-1] + scoring.get((seq1[i-1], seq2[j-1]), -4)
            gap1 = dp[i-1, j] + (gap_extend if i > 1 and seq1[i-2] == '-' else gap_open)
            gap2 = dp[i, j-1] + (gap_extend if j > 1 and seq2[j-2] == '-' else gap_open)
            dp[i, j] = max(match, gap1, gap2)
    
    matches = 0
    i, j = m, n
    while i > 0 and j > 0:
        if dp[i, j] == dp[i-1, j-1] + scoring.get((seq1[i-1], seq2[j-1]), -4):
            if seq1[i-1] == seq2[j-1]:
                matches += 1
            i -= 1
            j -= 1
        elif dp[i, j] == dp[i-1, j] + (gap_extend if i > 1 and seq1[i-2] == '-' else gap_open):
            i -= 1
        else:
            j -= 1
    
    return matches / max(m, n) * 100

def build_distance_matrix(sequences: List[Tuple[str, str]], seq_type: str) -> np.ndarray:
    """Compute pairwise identity matrix."""
    n = len(sequences)
    dist_matrix = np.zeros((n, n))
    scoring = DNAFULL if seq_type == 'nucleotide' else BLOSUM62
    
    for i, j in combinations(range(n), 2):
        identity = needleman_wunsch(sequences[i][1], sequences[j][1], scoring, seq_type)
        dist_matrix[i, j] = dist_matrix[j, i] = 100 - identity
    
    return dist_matrix

def neighbor_joining(dist_matrix: np.ndarray) -> List[Tuple[int, int]]:
    """Build guide tree using Neighbor-Joining."""
    linkage_matrix = linkage(dist_matrix, method='average')
    tree = to_tree(linkage_matrix)
    
    def get_pairs(node, indices):
        if node.is_leaf():
            return [(indices[node.id], indices[node.id])]
        left = get_pairs(node.left, indices)
        right = get_pairs(node.right, indices)
        return left + right + [(max(left[-1]), max(right[-1]))]
    
    pairs = get_pairs(tree, list(range(len(dist_matrix))))
    return pairs[1:]  # Skip self-pairs

def align_profiles(profile1: List[str], profile2: List[str], scoring: Dict, seq_type: str) -> List[str]:
    """Align two sequence profiles."""
    gap_open = -11 if seq_type == 'protein' else -10
    gap_extend = -1 if seq_type == 'protein' else -10
    
    m, n = len(profile1[0]), len(profile2[0])
    dp = np.zeros((m + 1, n + 1))
    
    for i in range(m + 1):
        dp[i, 0] = i * gap_open
    for j in range(n + 1):
        dp[0, j] = j * gap_open
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Sum-of-pairs score
            score = 0
            for s1 in profile1:
                for s2 in profile2:
                    score += scoring.get((s1[i-1], s2[j-1]), -4) / (len(profile1) * len(profile2))
            match = dp[i-1, j-1] + score
            gap1 = dp[i-1, j] + (gap_extend if i > 1 and profile1[0][i-2] == '-' else gap_open)
            gap2 = dp[i, j-1] + (gap_extend if j > 1 and profile2[0][j-2] == '-' else gap_open)
            dp[i, j] = max(match, gap1, gap2)
    
    aligned1, aligned2 = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i, j] == dp[i-1, j-1] + sum(
            scoring.get((s1[i-1], s2[j-1]), -4) / (len(profile1) * len(profile2))
            for s1 in profile1 for s2 in profile2
        ):
            aligned1 = [s[:i-1] + s[i-1] + s[i:] for s in profile1] + aligned1
            aligned2 = [s[:j-1] + s[j-1] + s[j:] for s in profile2] + aligned2
            i -= 1
            j -= 1
        elif i > 0 and dp[i, j] == dp[i-1, j] + (gap_extend if i > 1 and profile1[0][i-2] == '-' else gap_open):
            aligned1 = [s[:i-1] + s[i-1] + s[i:] for s in profile1] + aligned1
            aligned2 = [s + '-' for s in profile2] + aligned2
            i -= 1
        else:
            aligned1 = [s + '-' for s in profile1] + aligned1
            aligned2 = [s[:j-1] + s[j-1] + s[j:] for s in profile2] + aligned2
            j -= 1
    
    return aligned1 + aligned2

def refine_alignment(alignment: List[Tuple[str, str]], seq_type: str, iterations: int = 3) -> List[Tuple[str, str]]:
    """Iteratively refine alignment."""
    scoring = DNAFULL if seq_type == 'nucleotide' else BLOSUM62
    headers, seqs = zip(*alignment)
    
    for _ in range(iterations):
        # Split into two random groups
        indices = np.random.permutation(len(seqs))
        group1 = [seqs[i] for i in indices[:len(seqs)//2]]
        group2 = [seqs[i] for i in indices[len(seqs)//2:]]
        
        if not group1 or not group2:
            continue
        
        # Align groups
        aligned = align_profiles(group1, group2, scoring, seq_type)
        
        # Update sequences
        seqs = aligned
    
    return list(zip(headers, seqs))

def compute_conservation(alignment: List[str]) -> List[float]:
    """Compute column-wise conservation scores."""
    if not alignment:
        return []
    scores = []
    for i in range(len(alignment[0])):
        column = [seq[i] for seq in alignment]
        counts = pd.Series(column).value_counts()
        max_freq = counts.max() / len(column)
        scores.append(max_freq * 100)
    return scores

def format_clustal(alignment: List[Tuple[str, str]]) -> str:
    """Format alignment in Clustal format."""
    max_header = max(len(h) for h, _ in alignment)
    block_size = 60
    output = ["CLUSTAL multiple sequence alignment\n"]
    
    seq_len = len(alignment[0][1])
    for block_start in range(0, seq_len, block_size):
        block_end = min(block_start + block_size, seq_len)
        for header, seq in alignment:
            output.append(f"{header:<{max_header}}  {seq[block_start:block_end]}")
        # Conservation line
        conservation = [' ' for _ in range(block_start, block_end)]
        for i in range(block_start, block_end):
            column = [seq[i] for _, seq in alignment]
            if all(c == column[0] and c != '-' for c in column):
                conservation[i - block_start] = '*'
            elif sum(1 for c in column if c != '-') > 1:
                conservation[i - block_start] = ':'
        output.append(f"{'':<{max_header}}  {''.join(conservation)}")
        output.append("")
    
    return "\n".join(output)

def align_sequences(fasta: str, seq_type: str) -> Tuple[List[Dict], Dict, pd.DataFrame, str]:
    """Perform multiple sequence alignment."""
    if seq_type not in ['nucleotide', 'protein']:
        raise ValueError("Sequence type must be 'nucleotide' or 'protein'")
    
    sequences = parse_fasta(fasta, seq_type)
    if len(sequences) < 2:
        raise ValueError("At least two sequences required")
    
    # Pairwise distances
    dist_matrix = build_distance_matrix(sequences, seq_type)
    
    # Guide tree
    pairs = neighbor_joining(dist_matrix)
    
    # Progressive alignment
    alignment = sequences
    scoring = DNAFULL if seq_type == 'nucleotide' else BLOSUM62
    for idx1, idx2 in pairs:
        profile1 = [alignment[idx1][1]]
        profile2 = [alignment[idx2][1]]
        aligned_seqs = align_profiles(profile1, profile2, scoring, seq_type)
        alignment = [
            (h, s) for i, (h, s) in enumerate(alignment) if i not in [idx1, idx2]
        ] + [(sequences[idx1][0], aligned_seqs[0]), (sequences[idx2][0], aligned_seqs[1])]
    
    # Refinement
    alignment = refine_alignment(alignment, seq_type)
    
    # Results
    aligned_seqs = [seq for _, seq in alignment]
    conservation = compute_conservation(aligned_seqs)
    taxa = [
        {"position": i + 1, "conservation": score}
        for i, score in enumerate(conservation)
    ]
    
    stats = {
        "num_sequences": len(sequences),
        "alignment_length": len(aligned_seqs[0]),
        "avg_conservation": np.mean(conservation)
    }
    
    identity_df = pd.DataFrame(dist_matrix, index=[h for h, _ in sequences], columns=[h for h, _ in sequences])
    identity_df = identity_df.where(np.triu(np.ones_like(identity_df, dtype=bool), k=1)).stack().reset_index()
    identity_df.columns = ['seq1', 'seq2', 'identity']
    identity_df['identity'] = 100 - identity_df['identity']
    
    clustal_output = format_clustal(alignment)
    
    return taxa, stats, identity_df, clustal_output