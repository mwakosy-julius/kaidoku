from collections import Counter


def read_fasta(aligned_sequence):
    sequences = []
    sequence = ""

    for line in aligned_sequence.splitlines():
        line = line.strip()
        if line.startswith(">"):
            if sequence:
                sequences.append(sequence)
                sequence = ""
        else:
            sequence += line
    if sequence:
        sequences.append(sequence)
    return sequences


def generate_consensus(sequences):
    consensus_sequence = ""
    sequence_length = len(sequences[0])

    for i in range(sequence_length):
        column = [seq[i] for seq in sequences]
        most_common_nucleotide = Counter(column).most_common(1)[0][0]
        consensus_sequence += most_common_nucleotide

    return consensus_sequence
