from itertools import product
from collections import Counter

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

def generate_kmers(k):
    """Generate all possible k-mers of length k."""
    return [''.join(kmer) for kmer in product('ACGT', repeat=k)]

def calculate_consensus_score(motif_matrix):
    """Calculate the consensus score of a motif matrix."""
    consensus_score = 0
    for i in range(len(motif_matrix[0])):
        column = [motif_matrix[j][i] for j in range(len(motif_matrix))]
        most_common_base = max(set(column), key=column.count)
        consensus_score += column.count(most_common_base)
    return consensus_score

def find_motif(dna_sequences, k):
    """Find the most conserved motif of length k in the given DNA sequences."""
    best_motif = None
    best_score = 0

    kmers = generate_kmers(k)

    for kmer in kmers:
        motif_matrix = []
        for sequence in dna_sequences:
            best_match = None
            best_distance = float('inf')

            for i in range(len(sequence) - k + 1):
                substring = sequence[i:i+k]
                distance = sum([1 for x, y in zip(kmer, substring) if x != y])

                if distance < best_distance:
                    best_distance = distance
                    best_match = substring

            motif_matrix.append(best_match)

        score = calculate_consensus_score(motif_matrix)

        if score > best_score:
            best_score = score
            best_motif = motif_matrix

    return best_motif

def generate_consensus(sequences):
    consensus_sequence = ""
    sequence_length = len(sequences[0])

    for i in range(sequence_length):
        column = [seq[i] for seq in sequences]
        most_common_nucleotide = Counter(column).most_common(1)[0][0]
        consensus_sequence += most_common_nucleotide

    return consensus_sequence

# Example usage
# dna_sequences = [
#     "ATGCGTAGC",
#     "GCATCGTAC",
#     "TACGATCGA",
#     "CAGTCGTAC"
# ]

# k = 3
# motif, score = find_motif(dna_sequences, k)
# print("Best Motif:", motif)
# print("Consensus Score:", score)