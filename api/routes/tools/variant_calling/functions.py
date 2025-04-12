import random

def parse_fasta_sequences(fasta_input):
    sequences = []
    current_sequence = ""
    lines = fasta_input.strip().splitlines()
    for line in lines:
        if line.startswith(">"):
            if current_sequence:
                sequences.append(current_sequence)
                current_sequence = ""
        else:
            current_sequence += line.strip()
    if current_sequence:
        sequences.append(current_sequence)
    return sequences

def generate_reads(sequences, read_length=10, coverage=3):
    
    reads = []

    for sequence in sequences:
        seq_len = len(sequence)
        num_reads = (seq_len * coverage) // read_length  
        
        for _ in range(num_reads):
            start = random.randint(0, seq_len - read_length)  
            read_seq = sequence[start: start + read_length]
            reads.append((start, read_seq)) 

    return reads

def call_variants(reference, reads, threshold=0.7):
    
    base_counts = {i: {'A': 0, 'T': 0, 'C': 0, 'G': 0} for i in range(len(reference))}

    for start_pos, read in reads:
        for i, base in enumerate(read):
            genome_pos = start_pos + i  
            if genome_pos < len(reference):  
                base_counts[genome_pos][base] += 1  

    variants = []
    
    for pos, counts in base_counts.items():
        total_reads = sum(counts.values())
        if total_reads == 0:
            continue  

        most_common_base = max(counts, key=counts.get)
        most_common_freq = counts[most_common_base] / total_reads

        ref_base = reference[pos]
        if most_common_base != ref_base and most_common_freq >= threshold:
            variants.append((pos, ref_base, most_common_base, round(most_common_freq * 100, 2)))

    return variants