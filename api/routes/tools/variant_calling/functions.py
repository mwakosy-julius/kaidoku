from typing import List, Tuple


# Simple pairwise alignment (Needleman-Wunsch-like, pure Python)
def align_sequences(ref: str, sample: str) -> Tuple[str, str]:
    # Scoring parameters
    match_score = 1
    mismatch_penalty = -1
    gap_penalty = -2

    # Initialize scoring matrix
    m, n = len(ref), len(sample)
    score = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize first row and column
    for i in range(m + 1):
        score[i][0] = i * gap_penalty
    for j in range(n + 1):
        score[0][j] = j * gap_penalty

    # Fill scoring matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + (
                match_score if ref[i - 1] == sample[j - 1] else mismatch_penalty
            )
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)

    # Traceback to get aligned sequences
    aligned_ref, aligned_sample = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and score[i][j]
            == score[i - 1][j - 1]
            + (match_score if ref[i - 1] == sample[j - 1] else mismatch_penalty)
        ):
            aligned_ref.append(ref[i - 1])
            aligned_sample.append(sample[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and score[i][j] == score[i - 1][j] + gap_penalty:
            aligned_ref.append(ref[i - 1])
            aligned_sample.append("-")
            i -= 1
        else:
            aligned_ref.append("-")
            aligned_sample.append(sample[j - 1])
            j -= 1

    return "".join(aligned_ref[::-1]), "".join(aligned_sample[::-1])


# Variant calling function
def call_variants(ref: str, sample: str) -> List[dict]:
    aligned_ref, aligned_sample = align_sequences(ref, sample)
    variants = []
    ref_pos = 0  # Position in original reference (ignoring gaps)

    for i, (r, s) in enumerate(zip(aligned_ref, aligned_sample)):
        if r != "-":
            ref_pos += 1
        if r != s and r != "-" and s != "-":
            # SNP detected
            variants.append(
                {"position": ref_pos, "reference": r, "variant": s, "type": "SNP"}
            )
        elif r == "-" and s != "-":
            # Insertion
            variants.append(
                {
                    "position": ref_pos,
                    "reference": "",
                    "variant": s,
                    "type": "Insertion",
                }
            )
        elif r != "-" and s == "-":
            # Deletion
            variants.append(
                {"position": ref_pos, "reference": r, "variant": "", "type": "Deletion"}
            )

    return variants


# Parse FASTA (single sequence per input for simplicity)
def parse_fasta(fasta: str) -> str:
    lines = fasta.strip().split("\n")
    sequence = "".join(line for line in lines if not line.startswith(">"))
    return sequence
