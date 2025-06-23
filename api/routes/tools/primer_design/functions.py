import re

def gc_content(seq):
    gc = seq.count('G') + seq.count('C')
    return gc / len(seq) * 100

def melting_temp(seq):
    # Wallace rule: Tm = 2(A+T) + 4(G+C)
    a = seq.count('A')
    t = seq.count('T')
    g = seq.count('G')
    c = seq.count('C')
    return 2 * (a + t) + 4 * (g + c)

def reverse_complement(seq):
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    return ''.join(complement[base] for base in reversed(seq))

def design_primers(sequence, primer_len=20, tm_min=50, tm_max=65, gc_min=40, gc_max=60):
    sequence = sequence.upper()
    # Remove any non-ATGC characters
    sequence = re.sub(r'[^ATGC]', '', sequence)

    for i in range(0, len(sequence) - primer_len * 2):
        fwd = sequence[i:i+primer_len]
        rev = reverse_complement(sequence[i+primer_len:i+primer_len*2])

        fwd_gc = gc_content(fwd)
        rev_gc = gc_content(rev)
        fwd_tm = melting_temp(fwd)
        rev_tm = melting_temp(rev)

        if (gc_min <= fwd_gc <= gc_max and gc_min <= rev_gc <= gc_max and
            tm_min <= fwd_tm <= tm_max and tm_min <= rev_tm <= tm_max):
            return {
                'forward_primer': fwd,
                'reverse_primer': rev,
                'forward_tm': fwd_tm,
                'reverse_tm': rev_tm,
                'forward_gc': fwd_gc,
                'reverse_gc': rev_gc
            }
    return None
