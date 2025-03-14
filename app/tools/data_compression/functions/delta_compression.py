def delta_compress(sequence, reference):
    differences = []
    for i, (ref_base, seq_base) in enumerate(zip(reference, sequence)):
        if ref_base != seq_base:
            differences.append(f"{i}:{seq_base}")
    return "|".join(differences)


def delta_decompress(compressed, reference):
    sequence = list(reference)
    for diff in compressed.split("|"):
        if diff:
            pos, base = diff.split(":")
            sequence[int(pos)] = base
    return "".join(sequence)
