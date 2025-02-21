def calculate_gc_content(seq):
    gc_count = sum(1 for base in seq if base in "GC")
    return (gc_count / len(seq)) * 100 if seq else 0

def melting_temperature(seq):
    A_T = seq.count("A") + seq.count("T")
    G_C = seq.count("G") + seq.count("C")
    return (2 * A_T) + (4 * G_C)

def find_primers(dna_sequence, primer_length=20, min_gc=40, max_gc=60, min_tm=50, max_tm=65):
    primers = []

    for i in range(len(dna_sequence) - primer_length + 1):
        primer = dna_sequence[i:i + primer_length]
        gc_content = calculate_gc_content(primer)
        tm = melting_temperature(primer)

        if min_gc <= gc_content <= max_gc and min_tm <= tm <= max_tm:
            primers.append(primer)

    if primers:
        forward_primer = primers[0]
        reverse_primer = primers[-1][::-1].translate(str.maketrans("ATGC", "TACG"))
        return {"forward": forward_primer, "reverse": reverse_primer}
    
    return {"error": "No suitable primers found."}