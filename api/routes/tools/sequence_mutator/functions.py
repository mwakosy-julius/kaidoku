from typing import Dict, Optional
import random

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