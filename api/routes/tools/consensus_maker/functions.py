from collections import Counter
from typing import List, Optional
import numpy as np
import gc

def parse_fasta(fasta: str) -> List[str]:
    sequences = []
    current_seq = []
    lines = fasta.strip().split("\n")
    for line in lines:
        if line.startswith(">"):
            if current_seq:
                sequences.append("".join(current_seq))
                current_seq = []
        else:
            current_seq.append(line.strip())
    if current_seq:
        sequences.append("".join(current_seq))
    return [seq.upper() for seq in sequences if seq]

# def format_sequence(sequence):
#     sequence = sequence.upper()
#     if sequence[0] == ">":
#         sequence = sequence.splitlines()[1:]
#         sequence = "".join(sequence).strip()
#     else:
#         sequence = "".join(sequence.splitlines()).strip()
#     return sequence

# def generate_consensus(sequences):
#     consensus_sequence = ""
#     sequence_length = len(sequences[0])

#     for i in range(sequence_length):
#         column = [seq[i] for seq in sequences]
#         most_common_nucleotide = Counter(column).most_common(1)[0][0]
#         consensus_sequence += most_common_nucleotide

#     return consensus_sequence

def generate_consensus(sequences: List[str], tie_breaker: str = "random", chunk_size: int = 1000) -> Optional[str]:
    # Validate input sequences
    if not sequences:
        return None
    
    # Define valid nucleotides including gap character
    valid_nucleotides = set("ATGCatgc-")
    for seq in sequences:
        if not all(c in valid_nucleotides for c in seq):
            raise ValueError(f"Invalid nucleotide in sequence: {seq}")
    
    # Find the maximum sequence length for padding
    max_length = max(len(seq) for seq in sequences)
    
    # Initialize IUPAC ambiguity codes for nucleotide combinations
    iupac_codes = {
        frozenset(['A', 'G']): 'R',
        frozenset(['C', 'T']): 'Y',
        frozenset(['A', 'C']): 'M',
        frozenset(['G', 'T']): 'K',
        frozenset(['A', 'T']): 'W',
        frozenset(['C', 'G']): 'S',
        frozenset(['A', 'C', 'G', 'T']): 'N',
        frozenset(['A', 'C', 'G', 'T', '-']): 'N',  # Handle gaps in ties
    }
    
    # Initialize consensus as a string builder (more memory-efficient than list for large sequences)
    consensus = []
    
    # Process sequences in chunks to reduce memory usage
    for chunk_start in range(0, max_length, chunk_size):
        chunk_end = min(chunk_start + chunk_size, max_length)
        
        # Pad sequences for the current chunk only
        chunk_sequences = [seq.upper() + '-' * (max_length - len(seq)) for seq in sequences]
        chunk_sequences = [s[chunk_start:chunk_end] for s in chunk_sequences]
        
        # Convert chunk to numpy array for efficient column-wise processing
        seq_array = np.array([list(seq) for seq in chunk_sequences], dtype='U1')
        
        # Process each position in the chunk
        for i in range(chunk_end - chunk_start):
            column = seq_array[:, i]
            
            # Count nucleotides at this position, excluding gaps unless all are gaps
            counts = Counter(nuc for nuc in column if nuc != '-')
            
            # If all positions are gaps, use '-'
            if not counts:
                consensus.append('-')
                continue
            
            max_count = max(counts.values())
            most_common = [nuc for nuc, count in counts.items() if count == max_count]
            
            # Resolve the consensus for this position
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
        
        # Clear memory for the chunk
        del seq_array
        gc.collect()
    
    return ''.join(consensus)