def format_sequence(sequence):
    sequence = sequence.upper()
    if sequence[0] == ">":
        sequence = sequence.splitlines()[1:]
        sequence = "".join(sequence).strip()
    else:
        sequence = "".join(sequence.splitlines()).strip()
    return sequence


def is_dna(seq):
    return set(seq).issubset({"A", "C", "G", "T"})

def calculate_gc_content(sequence, window_size=100):
    gc_content = []
    positions = []
    for i in range(0, len(sequence) - window_size + 1, window_size):
        window = sequence[i : i + window_size]
        gc_count = window.count("G") + window.count("C")
        gc_content.append((gc_count / window_size) * 100)
        positions.append(i)
    return positions, gc_content


def calculate_nucleotide_counts(sequence):
    total_length = len(sequence)
    counts = {
        "A": {
            "count": sequence.count("A"),
            "percentage": (sequence.count("A") / total_length) * 100,
        },
        "T": {
            "count": sequence.count("T"),
            "percentage": (sequence.count("T") / total_length) * 100,
        },
        "G": {
            "count": sequence.count("G"),
            "percentage": (sequence.count("G") / total_length) * 100,
        },
        "C": {
            "count": sequence.count("C"),
            "percentage": (sequence.count("C") / total_length) * 100,
        },
    }
    # percentages = {nuc: (count / total_length) * 100 for nuc, count in counts.items()}
    return total_length, counts
