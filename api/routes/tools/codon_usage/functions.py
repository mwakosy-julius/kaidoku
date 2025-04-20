from collections import defaultdict
from pydantic import BaseModel


class Sequence(BaseModel):
    sequence: str


GENETIC_CODE = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

GENETIC_CODE_TABLE_ORDER = [
    ["TTT", "TCT", "TAT", "TGT"],
    ["TTC", "TCC", "TAC", "TGC"],
    ["TTA", "TCA", "TAA", "TGA"],
    ["TTG", "TCG", "TAG", "TGG"],
    ["CTT", "CCT", "CAT", "CGT"],
    ["CTC", "CCC", "CAC", "CGC"],
    ["CTA", "CCA", "CAA", "CGA"],
    ["CTG", "CCG", "CAG", "CGG"],
    ["ATT", "ACT", "AAT", "AGT"],
    ["ATC", "ACC", "AAC", "AGC"],
    ["ATA", "ACA", "AAA", "AGA"],
    ["ATG", "ACG", "AAG", "AGG"],
    ["GTT", "GCT", "GAT", "GGT"],
    ["GTC", "GCC", "GAC", "GGC"],
    ["GTA", "GCA", "GAA", "GGA"],
    ["GTG", "GCG", "GAG", "GGG"],
]


def calculate_codon_usage(sequence: str):
    sequence = sequence.upper()
    codon_count = defaultdict(int)
    amino_acid_count = defaultdict(int)

    for i in range(0, len(sequence) - 2, 3):
        codon = sequence[i : i + 3]
        if codon in GENETIC_CODE:
            amino_acid = GENETIC_CODE[codon]
            codon_count[codon] += 1
            amino_acid_count[amino_acid] += 1

    codon_usage = {}
    for codon, amino_acid in GENETIC_CODE.items():
        count = codon_count[codon]
        total_usage = amino_acid_count[amino_acid]
        relative_usage = count / total_usage if total_usage > 0 else 0
        percentage = (
            (count / sum(codon_count.values()) * 100)
            if sum(codon_count.values()) > 0
            else 0.0
        )
        codon_usage[codon] = {
            "amino_acid": amino_acid,
            "relative_usage": round(relative_usage, 2),
            "percentage": round(percentage, 1),
            "count": count,
        }
    return codon_usage


def generate_codon_usage_table(result):
    html = '<table border="1" style="width:100%; text-align:center;">'
    for row in GENETIC_CODE_TABLE_ORDER:
        html += "<tr>"
        for codon in row:
            usage = result.get(
                codon,
                {
                    "amino_acid": "",
                    "relative_usage": 0.0,
                    "percentage": 0.0,
                    "count": 0,
                },
            )
            html += (
                f"<td>{codon}<br>{usage['amino_acid']}<br>"
                f"{usage['relative_usage']:.2f}<br>{usage['percentage']:.1f}%<br>{usage['count']}</td>"
            )
        html += "</tr>"
    html += "</table>"
    return html
