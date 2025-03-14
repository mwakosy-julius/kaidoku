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

def generate_consensus(sequences):
    consensus_sequence = ""
    sequence_length = len(sequences[0])

    for i in range(sequence_length):
        column = [seq[i] for seq in sequences]
        most_common_nucleotide = Counter(column).most_common(1)[0][0]
        consensus_sequence += most_common_nucleotide

    return consensus_sequence