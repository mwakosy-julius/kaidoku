from fastapi import APIRouter, HTTPException
from . import functions
from ...schema.schema import Consensus

router = APIRouter(
    prefix="/gc_content",
)

@router.post("/")
def gc_content(request: Consensus):
    context = {'sequence': '', 'window_size': 100, 'summary': '', 'plot': ''}

    sequence_input = request.sequence.strip()
    window_size = int(request.POST.get('window_size', 100))

    if sequence_input.startswith(">"):
        lines = sequence_input.splitlines()
        sequence = "".join(lines[1:]).upper()
    else:
        sequence = sequence_input.upper()

    positions, gc_content = functions.calculate_gc_content(sequence, window_size)
    plot = functions.plot_gc_content(positions, gc_content, window_size)

    total_length, counts, percentages = functions.calculate_nucleotide_counts(sequence)
    summary = (
        f"Summary: Full Length({total_length} bp) | "
        f"A({percentages['A']:.1f}% {counts['A']}) | "
        f"T({percentages['T']:.1f}% {counts['T']}) | "
        f"G({percentages['G']:.1f}% {counts['G']}) | "
        f"C({percentages['C']:.1f}% {counts['C']})"
    )

    context.update({
        'sequence': sequence_input,
        'window_size': window_size,
        'summary': summary,
        'plot': plot
    })
