from collections import Counter
from typing import List, Optional
import numpy as np

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

# def generate_consensus(sequences):
#     consensus_sequence = ""
#     sequence_length = len(sequences[0])

#     for i in range(sequence_length):
#         column = [seq[i] for seq in sequences]
#         most_common_nucleotide = Counter(column).most_common(1)[0][0]
#         consensus_sequence += most_common_nucleotide

#     return consensus_sequence

def generate_consensus(sequences: List[str], tie_breaker: str = "random") -> Optional[str]:
    sequence_length = len(sequences[0])
    # if not all(len(seq) == sequence_length for seq in sequences):
    #     raise ValueError("All sequences must have the same length")
    
    valid_nucleotides = set("ATGCatgc-")
    for seq in sequences:
        if not all(c in valid_nucleotides for c in seq):
            raise ValueError(f"Invalid nucleotide in sequence: {seq}")
    
    seq_array = np.array([list(seq.upper()) for seq in sequences])
    
    consensus = []
    
    iupac_codes = {
        frozenset(['A', 'G']): 'R',
        frozenset(['C', 'T']): 'Y',
        frozenset(['A', 'C']): 'M',
        frozenset(['G', 'T']): 'K',
        frozenset(['A', 'T']): 'W',
        frozenset(['C', 'G']): 'S',
        frozenset(['A', 'C', 'G', 'T']): 'N',
    }
    
    for i in range(sequence_length):
        column = seq_array[:, i]
        
        counts = Counter(column)
        max_count = max(counts.values())
        
        most_common = [nuc for nuc, count in counts.items() if count == max_count]
        
        if len(most_common) == 1:
            consensus.append(most_common[0])
        else:
            if tie_breaker == "random":
                consensus.append(np.random.choice(most_common))
            elif tie_breaker == "iupac":
                key = frozenset(most_common)
                consensus.append(iupac_codes.get(key, 'N'))  
            else:
                raise ValueError("Invalid tie_breaker strategy")
    
    return ''.join(consensus)