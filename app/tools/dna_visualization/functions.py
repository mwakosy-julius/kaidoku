import pandas as pd
import altair as alt

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

def transcription(sequence):
    transcript = ''
    for nucleotide in sequence:
        if nucleotide == 'A':
            nucleotide = 'U'
        elif nucleotide == 'T':
            nucleotide = 'A'
        elif nucleotide == 'C':
            nucleotide = 'G'
        elif nucleotide == 'G':
            nucleotide = 'C'
        else:
            break
        transcript+=nucleotide
    return transcript

def translation(sequence):
    sequence2 = ''
    for nucleotide in sequence:
        if nucleotide == 'A':
            nucleotide = 'U'
        elif nucleotide == 'T':
            nucleotide = 'A'
        elif nucleotide == 'C':
            nucleotide = 'G'
        elif nucleotide == 'G':
            nucleotide = 'C'
        sequence2 += nucleotide

    RNA_sequence = []
    n = 0
    k = 1
    for seq in sequence2:
        RNA_sequence.append(sequence2[n]+sequence2[n+1]+sequence2[n+2])
        if len(sequence2)//3 > k:
            n += 3
            k += 1
        else:
            break

    amino_sequence = ''
    for codon in RNA_sequence:
        if codon == 'UUU' or codon == 'UUC':
            codon = 'Phe-'
        elif codon == 'UUA' or codon == 'UUG' or codon == 'CUU' or codon == 'CUC' or codon == 'CUA' or codon == 'CUG':
            codon = 'Leu-'
        elif codon == 'AUU' or codon == 'AUC' or codon == 'AUA':
            codon = 'Ile-'
        elif codon == 'AUG':
            codon = 'Met-'
        elif codon == 'GUU' or codon == 'GUC' or codon == 'GUA' or codon == 'GUG':
            codon = 'Val-'
        elif codon == 'UCU' or codon == 'UCC' or codon == 'UCA' or codon == 'UCG' or codon == 'AGU' or codon == 'AGC':
            codon = 'Ser-'
        elif codon == 'CCU' or codon == 'CCC' or codon == 'CCA' or codon == 'CCG':
            codon = 'Pro-'
        elif codon == 'ACU' or codon == 'ACC' or codon == 'ACA' or codon == 'ACG':
            codon = 'Thr-'
        elif codon == 'GCU' or codon == 'GCC' or codon == 'GCA' or codon == 'GCG':
            codon = 'Ala-'
        elif codon == 'UAU' or codon == 'UAC':
            codon = 'Tyr-'
        elif codon == 'UAA' or codon == 'UAG' or codon == 'UGA':
            codon = 'STOP'
            break
        elif codon == 'UAU' or codon == 'UAC':
            codon = 'Tyr-'
        elif codon == 'CAU' or codon == 'CAC':
            codon = 'His-'
        elif codon == 'CAA' or codon == 'CAG':
            codon = 'Gln-'
        elif codon == 'AAU' or codon == 'AAC':
            codon = 'Asn-'
        elif codon == 'AAA' or codon == 'AAG':
            codon = 'Lys-'
        elif codon == 'GAU' or codon == 'GAC':
            codon = 'Asp-'
        elif codon == 'GAA' or codon == 'GAG':
            codon = 'Glu-'
        elif codon == 'UGU' or codon == 'UGC':
            codon = 'Cys-'
        elif codon == 'UGG':
            codon = 'Trp-'
        elif codon == 'CGU' or codon == 'CGC' or codon == 'CGA' or codon == 'CGG' or codon == 'AGA' or codon == 'AGG':
            codon = 'Arg-'
        elif codon == 'GGU' or codon == 'GGC' or codon == 'GGA' or codon == 'GGG':
            codon = 'Gly-'
        amino_sequence+=codon
    return amino_sequence

def gc_content(sequence):
    gc = sequence.count('G') + sequence.count('C')
    total = len(sequence)
    content = ''
    try:
        content = str(int(gc/total*100))+'%'
    except ZeroDivisionError:
        pass
    return content

def nucleotide_counts(sequence):
    total_length = len(sequence)
    counts = {
        'A': sequence.count('A'),
        'T': sequence.count('T'),
        'G': sequence.count('G'),
        'C': sequence.count('C')
    }
    percentages = {nuc: (count * 100 ) // total_length  for nuc, count in counts.items()}
    return counts, percentages

def dna_table(sequence):
    counts, percentages = nucleotide_counts(sequence)
    data = {
        'nucleotide': counts.keys(),
        'count': counts.values(),
        'percentage': percentages.values()
    }
    df = pd.DataFrame(data)
    return df

def dna_chart(sequence):
    counts, percentages = nucleotide_counts(sequence)

    data = {
        'nucleotide': counts.keys(),
        'percentage': percentages.values()
    }
    df = pd.DataFrame(data)

    p = alt.Chart(df).mark_bar().encode(
        x = 'nucleotide',
        y = 'percentage'
    )

    p = p.properties(
        width = alt.Step(80)
    )
    return p

def amino_acid_counts(sequence):
    total_length = len(translation(sequence))//4
    amino_sequence = translation(sequence)
    counts = dict([
    ('Phe ', amino_sequence.count('Phe')),
    ('Leu ', amino_sequence.count('Leu')),
    ('Ile ', amino_sequence.count('Ile')),
    ('Met ', amino_sequence.count('Met')),
    ('Val ', amino_sequence.count('Val')),
    ('Ser ', amino_sequence.count('Ser')),
    ('Pro ', amino_sequence.count('Pro')),
    ('Thr ', amino_sequence.count('Thr')),
    ('Ala ', amino_sequence.count('Ala')),
    ('Tyr ', amino_sequence.count('Tyr')),
    ('His ', amino_sequence.count('HIs')),
    ('Gln ', amino_sequence.count('Gln')),
    ('Asn ', amino_sequence.count('Asn')),
    ('Lys ', amino_sequence.count('Lys')),
    ('Asp ', amino_sequence.count('Asp')),
    ('Glu ', amino_sequence.count('Glu')),
    ('Cys ', amino_sequence.count('Cys')),
    ('Trp ', amino_sequence.count('Trp')),
    ('Arg ', amino_sequence.count('Arg')),
    ('Gly ', amino_sequence.count('Gly'))
    ])
    percentages = {amino_acids: (count * 100 )// total_length for amino_acids, count in counts.items()}
    return counts, percentages

def amino_acid_chart(sequence):
    counts, percentages = amino_acid_counts(sequence)
    data = {
        'amino_acids': counts.keys(),
        'percentage': percentages.values()
    }
    df = pd.DataFrame(data)

    p = alt.Chart(df).mark_bar().encode(
        x = 'amino_acids',
        y = 'percentage'
    )

    p = p.properties(
        width = alt.Step(20)
    )
    return p