def assemble_dna(sequences):
    while len(sequences) > 1:
        best_pair = None
        best_overlap = ""
        for i in range(len(sequences)):
            for j in range(len(sequences)):
                if i != j:
                    overlap = find_overlap(sequences[i], sequences[j])
                    if len(overlap) > len(best_overlap):
                        best_overlap = overlap
                        best_pair = (i, j)

        if best_pair:
            i, j = best_pair
            merged = sequences[i] + sequences[j][len(best_overlap) :]
            sequences.pop(j)
            sequences[i] = merged
        else:
            break

    return sequences[0] if sequences else ""


def find_overlap(seq1, seq2):
    min_overlap = 3
    for i in range(min_overlap, len(seq1)):
        if seq2.startswith(seq1[i:]):
            return seq1[i:]
    return ""
