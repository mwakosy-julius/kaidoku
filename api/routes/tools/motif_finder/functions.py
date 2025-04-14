from typing import List, Tuple, Dict
import random
from collections import Counter
import math

# Parse FASTA sequences
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

# Calculate background frequencies
def background_frequencies(sequences: List[str]) -> Dict[str, float]:
    all_bases = "".join(sequences)
    counter = Counter(all_bases)
    total = sum(counter.values())
    return {base: count / total for base, count in counter.items() if base in "ACGT"}

# Build position weight matrix (PWM) from motifs
def build_pwm(motifs: List[str], pseudocount: float = 0.01) -> List[Dict[str, float]]:
    pwm = []
    motif_length = len(motifs[0])
    for pos in range(motif_length):
        counter = Counter(motif[pos] for motif in motifs)
        total = sum(counter.values()) + 4 * pseudocount
        pwm.append({
            'A': (counter.get('A', 0) + pseudocount) / total,
            'C': (counter.get('C', 0) + pseudocount) / total,
            'G': (counter.get('G', 0) + pseudocount) / total,
            'T': (counter.get('T', 0) + pseudocount) / total
        })
    return pwm

# Score a motif against PWM
def score_motif(motif: str, pwm: List[Dict[str, float]], background: Dict[str, float]) -> float:
    score = 0.0
    for i, base in enumerate(motif):
        if base in pwm[i]:
            score += math.log2(pwm[i][base] / background.get(base, 0.01))
    return score

# Gibbs Sampling for motif finding
def gibbs_sampling(sequences: List[str], motif_length: int, iterations: int = 200) -> Tuple[List[str], float]:
    if not sequences or motif_length < 1:
        return [], 0.0
    
    seq_lengths = [len(seq) for seq in sequences]
    positions = [random.randint(0, max(0, l - motif_length)) for l in seq_lengths]
    motifs = [sequences[i][pos:pos + motif_length] for i, pos in enumerate(positions) if pos + motif_length <= len(sequences[i])]
    
    if len(motifs) != len(sequences):
        return [], 0.0
    
    background = background_frequencies(sequences)
    best_motifs = motifs[:]
    best_score = -float("inf")
    
    for _ in range(iterations):
        idx = random.randint(0, len(sequences) - 1)
        other_motifs = motifs[:idx] + motifs[idx + 1:]
        pwm = build_pwm(other_motifs)
        
        scores = []
        possible_positions = []
        seq = sequences[idx]
        for pos in range(max(0, len(seq) - motif_length + 1)):
            motif = seq[pos:pos + motif_length]
            if len(motif) == motif_length:
                score = score_motif(motif, pwm, background)
                scores.append(score)
                possible_positions.append(pos)
        
        if not scores:
            continue
        
        max_score = max(scores)
        scores = [math.exp(s - max_score) for s in scores]
        total = sum(scores)
        if total == 0:
            continue
        probs = [s / total for s in scores]
        
        new_pos = random.choices(possible_positions, weights=probs, k=1)[0]
        motifs[idx] = seq[new_pos:new_pos + motif_length]
        
        pwm = build_pwm(motifs)
        current_score = sum(score_motif(m, pwm, background) for m in motifs)
        if current_score > best_score:
            best_score = current_score
            best_motifs = motifs[:]
    
    return best_motifs, best_score

# Estimate maximum motif length
def estimate_max_motif_length(sequences: List[str], max_test_length: int = 20, iterations: int = 50) -> int:
    if not sequences:
        return 8  # Fallback
    min_seq_length = min(len(seq) for seq in sequences)
    max_length = min(min_seq_length, max_test_length)  # Cap for efficiency
    
    best_length = 4
    best_score = -float("inf")
    
    # Test lengths from 4 to max_length
    for length in range(4, max_length + 1):
        motifs, score = gibbs_sampling(sequences, length, iterations=iterations)
        if motifs and score > best_score:
            best_score = score
            best_length = length
    
    return best_length

# Generate consensus from motifs
def motifs_to_consensus(motifs: List[str]) -> str:
    if not motifs:
        return ""
    motif_length = len(motifs[0])
    consensus = []
    for pos in range(motif_length):
        bases = Counter(motif[pos] for motif in motifs)
        consensus.append(bases.most_common(1)[0][0])
    return "".join(consensus)

# Find motif positions in sequences
def find_motif_positions(sequences: List[str], motif: str) -> List[Dict]:
    positions = []
    for i, seq in enumerate(sequences):
        for pos in range(len(seq) - len(motif) + 1):
            if seq[pos:pos + len(motif)] == motif:
                positions.append({
                    "sequence": f"seq{i + 1}",
                    "position": pos + 1,  # 1-based
                    "motif": motif
                })
    return positions
    