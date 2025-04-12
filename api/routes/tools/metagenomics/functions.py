from collections import Counter
import matplotlib.pyplot as plt
import io
import base64

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

def count_kmers(sequence, k=3):
    counts = Counter()
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        counts[kmer] += 1
    total = sum(counts.values())
    percentages = {k: (v / total) * 100 for k, v in counts.items()}
    return counts, percentages

def calculate_gc_content(sequence):
    if not sequence:
        return 0
    gc_count = sequence.count("G") + sequence.count("C")
    return (gc_count / len(sequence)) * 100

def generate_kmer_bar_chart(kmer_counts, k=3):
    kmers = list(kmer_counts.keys())
    counts = list(kmer_counts.values())
    
    plt.figure(figsize=(8, 4))
    plt.bar(kmers, counts, color="skyblue")
    plt.xlabel(f"{k}-mers")
    plt.ylabel("Count")
    plt.title(f"{k}-mer Distribution")
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return image_base64
