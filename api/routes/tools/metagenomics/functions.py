from typing import List, Dict, Tuple
from collections import defaultdict
import re
import pandas as pd

import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_fasta(fasta: str) -> Tuple[List[str], List[str]]:
    """
    Parse FASTA string, returning valid DNA sequences and errors for invalid ones.
    
    Args:
        fasta: FASTA-formatted string (e.g., ">Seq1\nATGCC\n>Seq2\nGCTAA").
    
    Returns:
        Tuple of (valid_sequences, errors):
        - valid_sequences: List of DNA sequences (A, T, C, G, N, >= 21 bases).
        - errors: List of error messages for invalid sequences.
    """
    valid_sequences = []
    errors = []
    current_seq = []
    current_header = None
    dna_pattern = re.compile(r'^[ATCGNatcgn]+$')  # Case-insensitive DNA

    lines = fasta.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        if line.startswith('>'):
            # Process previous sequence
            if current_seq:
                seq = ''.join(current_seq).upper()
                if not seq:
                    errors.append(f"Empty sequence for header: {current_header}")
                elif not dna_pattern.match(seq):
                    errors.append(f"Invalid DNA sequence for {current_header}: {seq[:20]}...")
                elif len(seq) < 21:
                    errors.append(f"Sequence too short for {current_header}: {len(seq)} bases")
                else:
                    valid_sequences.append(seq)
                current_seq = []
            current_header = line
        else:
            # Validate line before appending
            if dna_pattern.match(line):
                current_seq.append(line)
            else:
                errors.append(f"Invalid characters in line for {current_header}: {line[:20]}...")

    # Process final sequence
    if current_seq:
        seq = ''.join(current_seq).upper()
        if not seq:
            errors.append(f"Empty sequence for header: {current_header}")
        elif not dna_pattern.match(seq):
            errors.append(f"Invalid DNA sequence for {current_header}: {seq[:20]}...")
        elif len(seq) < 21:
            errors.append(f"Sequence too short for {current_header}: {len(seq)} bases")
        else:
            valid_sequences.append(seq)

    logger.info(f"Parsed {len(valid_sequences)} valid sequences, {len(errors)} errors")
    return valid_sequences, errors

# def parse_fasta(fasta: str) -> List[str]:
#     """Parse FASTA string, skipping invalid sequences."""
#     sequences = []
#     current_seq = []
#     lines = fasta.strip().split('\n')
#     header = False
    
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
#         if line.startswith('>'):
#             if current_seq:
#                 seq = ''.join(current_seq).upper()
#                 if re.match(r'^[ATCGN]+$', seq):
#                     sequences.append(seq)
#                 current_seq = []
#             header = True
#         elif header:
#             current_seq.append(line)
    
#     if current_seq:
#         seq = ''.join(current_seq).upper()
#         if re.match(r'^[ATCGN]+$', seq):
#             sequences.append(seq)
    
#     return [seq for seq in sequences if len(seq) >= 21]

def get_kmers(sequence: str, k: int = 21) -> List[str]:
    """Extract k-mers, skipping ambiguous regions."""
    kmers = []
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        if 'N' not in kmer and len(kmer) == k:
            kmers.append(kmer)
    return kmers

def mock_reference_db() -> Dict[str, Dict[str, str]]:
    """Expanded k-mer database for microbiome taxa."""
    taxa = [
        ("Escherichia", "Proteobacteria", ["ATGCCATGCTAGCTAGCTAGC", "CCATGCTAGCTAGCTAGCTAG"]),
        ("Bacteroides", "Bacteroidetes", ["CGTACGTACGTACGTACGTAC", "GTACGTACGTACGTACGTACG"]),
        ("Staphylococcus", "Firmicutes", ["GCTAGCTAGCTAGCTAGCTAG", "AGCTAGCTAGCTAGCTAGCTA"]),
        ("Pseudomonas", "Proteobacteria", ["TACGTACGTACGTACGTACGT", "ACGTACGTACGTACGTACGTA"]),
        ("Lactobacillus", "Firmicutes", ["AATTGAATTGAATTGAATTGA", "TTGAATTGAATTGAATTGAAT"]),
        ("Clostridium", "Firmicutes", ["TGCATGCTAGCTAGCTAGCTA", "GCATGCTAGCTAGCTAGCTAG"]),
        ("Bifidobacterium", "Actinobacteria", ["ACTGACTGACTGACTGACTGA", "CTGACTGACTGACTGACTGAC"]),
        ("Salmonella", "Proteobacteria", ["ATGCTAGCTAGCTAGCTAGCT", "TGCTAGCTAGCTAGCTAGCTA"]),
        ("Klebsiella", "Proteobacteria", ["CGTAGCTAGCTAGCTAGCTAG", "GTAGCTAGCTAGCTAGCTAGC"]),
        ("Enterococcus", "Firmicutes", ["GATTGATTGATTGATTGATTG", "ATTGATTGATTGATTGATTGA"]),
        ("Vibrio", "Proteobacteria", ["TACGCTAGCTAGCTAGCTAGC", "ACGCTAGCTAGCTAGCTAGCT"]),
        ("Corynebacterium", "Actinobacteria", ["CATGCTAGCTAGCTAGCTAGC", "ATGCTAGCTAGCTAGCTAGCA"]),
        ("Mycobacterium", "Actinobacteria", ["GCTGACTGACTGACTGACTGA", "CTGACTGACTGACTGACTGAC"]),
        ("Listeria", "Firmicutes", ["TAGCTAGCTAGCTAGCTAGCT", "AGCTAGCTAGCTAGCTAGCTT"]),
        ("Campylobacter", "Proteobacteria", ["ATGCGTAGCTAGCTAGCTAGC", "TGCGTAGCTAGCTAGCTAGCT"]),
        ("Helicobacter", "Proteobacteria", ["CGTGACTGACTGACTGACTGA", "GTGACTGACTGACTGACTGAC"]),
        ("Acinetobacter", "Proteobacteria", ["TGCGAATTGAATTGAATTGAA", "GCGAATTGAATTGAATTGAAT"]),
        ("Prevotella", "Bacteroidetes", ["ACTGCTAGCTAGCTAGCTAGC", "CTGCTAGCTAGCTAGCTAGCT"]),
        ("Fusobacterium", "Fusobacteria", ["GATTGCTAGCTAGCTAGCTAG", "ATTGCTAGCTAGCTAGCTAGC"]),
        ("Ruminococcus", "Firmicutes", ["CATGAATTGAATTGAATTGAA", "ATGAATTGAATTGAATTGAAT"])
    ]
    db = {}
    for genus, phylum, kmers in taxa:
        for kmer in kmers:
            db[kmer] = {"genus": genus, "phylum": phylum}
    # Simulate 1,000 k-mers
    for i in range(45):
        genus = f"Genus_{i+6}"
        phylum = ["Proteobacteria", "Firmicutes", "Bacteroidetes", "Actinobacteria"][i % 4]
        for j in range(20):
            kmer = f"{'ATCG'[i % 4]}{'ATCG'[j % 4]}" * 10 + "A"
            db[kmer] = {"genus": genus, "phylum": phylum}
    return db

def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance for approximate matching."""
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def profile_taxa(fasta: str) -> Tuple[List[Dict[str, float]], Dict[str, int], pd.DataFrame]:
    """Profile taxa with approximate k-mer matching."""
    sequences = parse_fasta(fasta)
    if not sequences:
        raise ValueError("Invalid FASTA format or reads too short (min 21bp)")
    
    kmer_db = mock_reference_db()
    taxa_counts = defaultdict(int)
    total_kmers = 0
    taxon_details = []
    
    for seq in sequences:
        kmers = get_kmers(seq)
        for kmer in kmers:
            best_match = None
            min_dist = 3  # Allow up to 2 mismatches
            for ref_kmer, taxon in kmer_db.items():
                dist = hamming_distance(kmer, ref_kmer)
                if dist < min_dist:
                    best_match = taxon
                    min_dist = dist
            if best_match:
                genus = best_match["genus"]
                taxa_counts[genus] += 1
                total_kmers += 1
                taxon_details.append({
                    "genus": genus,
                    "phylum": best_match["phylum"],
                    "kmer": kmer,
                    "distance": min_dist
                })
    
    if total_kmers == 0:
        raise ValueError("No taxa identified; try reads with common microbial k-mers")
    
    taxa = [
        {"genus": genus, "abundance": count / total_kmers * 100}
        for genus, count in taxa_counts.items()
    ]
    taxa = sorted(taxa, key=lambda x: x["abundance"], reverse=True)[:10]
    
    stats = {
        "total_reads": len(sequences),
        "classified_kmers": total_kmers,
        "unique_genera": len(taxa_counts)
    }
    
    details_df = pd.DataFrame(taxon_details)
    if not details_df.empty:
        details_df = details_df.groupby(["genus", "phylum"]).agg({
            "kmer": "count",
            "distance": "mean"
        }).reset_index()
        details_df.rename(columns={"kmer": "kmer_count"}, inplace=True)
        details_df["confidence"] = details_df["kmer_count"] / details_df["kmer_count"].sum() * 100
    
    return taxa, stats, details_df