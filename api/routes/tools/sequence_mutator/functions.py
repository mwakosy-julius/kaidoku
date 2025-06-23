import random
from typing import Dict

def format_sequence(sequence):
    sequence = sequence.upper()
    if sequence[0] == ">":
        sequence = sequence.splitlines()[1:]
        sequence = "".join(sequence).strip()
    else:
        sequence = "".join(sequence.splitlines()).strip()
    return sequence

def validate_sequence(sequence: str, seq_type: str) -> bool:
    """Validate DNA or protein sequence."""
    sequence = sequence.strip().upper()
    if seq_type == "dna":
        return all(c in "ACGT" for c in sequence)
    elif seq_type == "protein":
        return all(c in "ACDEFGHIKLMNPQRSTVWY" for c in sequence)
    return False

def mutate_sequence(sequence: str, seq_type: str, mutation_type: str, mutation_rate: float) -> Dict:
    """
    Apply mutations to a DNA or protein sequence.
    Returns original sequence, mutated sequence, and mutation positions.
    """
    if not sequence:
        return {"error": "Sequence is required"}

    sequence = format_sequence(sequence)

    sequence = sequence.strip().upper()
    if not validate_sequence(sequence, seq_type):
        return {"error": f"Invalid {seq_type} sequence. Use {'ACGT' if seq_type == 'dna' else 'ACDEFGHIKLMNPQRSTVWY'}."}

    mutated = list(sequence)
    mutations = []
    bases = "ACGT" if seq_type == "dna" else "ACDEFGHIKLMNPQRSTVWY"

    if mutation_type == "substitution":
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                new_base = random.choice([b for b in bases if b != mutated[i]])
                mutations.append({"position": i, "from": mutated[i], "to": new_base})
                mutated[i] = new_base
    elif mutation_type == "insertion":
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                new_base = random.choice(bases)
                mutations.append({"position": i, "inserted": new_base})
                mutated.insert(i, new_base)
    elif mutation_type == "deletion":
        for i in range(len(mutated) - 1, -1, -1):
            if random.random() < mutation_rate:
                mutations.append({"position": i, "deleted": mutated[i]})
                mutated.pop(i)

    return {
        "original_sequence": sequence,
        "mutated_sequence": "".join(mutated),
        "mutations": mutations,
        "mutation_count": len(mutations)
    }

# genetic_code = {
#     'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M', 'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
#     'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K', 'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
#     'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L', 'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
#     'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q', 'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
#     'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V', 'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
#     'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E', 'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
#     'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S', 'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
#     'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*', 'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W'
# }

# def translate(sequence: str) -> str:
#     """Translate a DNA sequence into an amino acid sequence."""
#     aa_seq = ''
#     # Process in steps of 3 (codons), ignoring incomplete codons at the end
#     for i in range(0, len(sequence) - 2, 3):
#         codon = sequence[i:i+3]
#         aa = genetic_code.get(codon, 'X')  # 'X' for unknown codons
#         aa_seq += aa
#     return aa_seq

# def compare_sequences(seq1: str, seq2: str) -> List[Dict]:
#     """Compare two sequences and return a list of differences."""
#     changes = []
#     min_len = min(len(seq1), len(seq2))
#     # Check each position up to the shorter sequence length
#     for i in range(min_len):
#         if seq1[i] != seq2[i]:
#             changes.append({"position": i, "from": seq1[i], "to": seq2[i]})
#     # Handle length differences
#     if len(seq1) > len(seq2):
#         changes.append({"deletion_from_position": min_len, "deleted": seq1[min_len:]})
#     elif len(seq2) > len(seq1):
#         changes.append({"insertion_from_position": min_len, "inserted": seq2[min_len:]})
#     return changes

# def mutate_sequence(
#     sequence: str,
#     seq_type: str,
#     mutation_operations: List[Dict],
#     coding: bool = False,
#     seed: Optional[int] = None
# ) -> Dict:
#     """
#     Mutate a sequence and show the effect on the protein sequence if applicable.

#     Parameters:
#     - sequence: The original DNA or protein sequence.
#     - seq_type: 'dna' or 'protein'.
#     - mutation_operations: List of mutation operations (e.g., substitution, insertion, deletion).
#     - coding: True if the DNA sequence codes for a protein (default: False).
#     - seed: Random seed for reproducibility (optional).

#     Returns:
#     - Dictionary with original sequence, mutated sequence, mutations, and amino acid changes (if applicable).
#     """
#     # Basic validation
#     if not sequence:
#         return {"error": "Sequence is required"}
#     sequence = sequence.strip().upper()
#     bases = "ACGT" if seq_type == "dna" else "ACDEFGHIKLMNPQRSTVWY"
#     if not all(c in bases for c in sequence):
#         return {"error": f"Invalid {seq_type} sequence. Use {bases}."}

#     # Set random seed if provided
#     if seed is not None:
#         random.seed(seed)

#     # Apply mutations (simplified example; replace with your actual mutation logic)
#     mutated = list(sequence)
#     all_mutations = []
#     for op in mutation_operations:
#         op_type = op.get("type", "substitution")
#         mutations = []
#         if op_type == "substitution" and op.get("rate", 0) > 0:
#             for i in range(len(mutated)):
#                 if random.random() < op["rate"]:
#                     new_base = random.choice([b for b in bases if b != mutated[i]])
#                     mutations.append({"position": i, "from": mutated[i], "to": new_base})
#                     mutated[i] = new_base
#         all_mutations.append(mutations)
#     mutated_sequence = "".join(mutated)

#     # Prepare result
#     result = {
#         "original_sequence": sequence,
#         "mutated_sequence": mutated_sequence,
#         "mutations_by_operation": all_mutations,
#         "total_mutation_count": sum(len(m) for m in all_mutations)
#     }

#     # Analyze effect on protein sequence
#     if seq_type == "dna" and coding:
#         # Translate both sequences to amino acids
#         original_aa = translate(sequence)
#         mutated_aa = translate(mutated_sequence)
#         # Compare amino acid sequences
#         aa_changes = compare_sequences(original_aa, mutated_aa)
#         # Add to result
#         result["original_aa"] = original_aa
#         result["mutated_aa"] = mutated_aa
#         result["aa_changes"] = aa_changes
#     elif seq_type == "protein":
#         # Directly compare protein sequences
#         aa_changes = compare_sequences(sequence, mutated_sequence)
#         result["aa_changes"] = aa_changes

#     return result

# # Example usage
# dna_sequence = "ATGGACTCTAA"  # Codes for "MDS" (Methionine, Aspartic Acid, Serine)
# operations = [{"type": "substitution", "rate": 0.2}]
# result = mutate_sequence(dna_sequence, "dna", operations, coding=True, seed=42)
# print(result)
