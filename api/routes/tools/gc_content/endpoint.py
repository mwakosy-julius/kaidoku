from fastapi import APIRouter
from . import functions
from pydantic import BaseModel


class Consensus(BaseModel):
    sequence: str
    window_size: int = 100


router = APIRouter(
    prefix="/gc_content",
)


@router.post("/")
def gc_content(request: Consensus):
    context = {"sequence": "", "window_size": 100, "summary": "", "plot": ""}

    sequence_input = request.sequence.strip()
    window_size = request.window_size

    if sequence_input.startswith(">"):
        lines = sequence_input.splitlines()
        sequence = "".join(lines[1:]).upper()
    else:
        sequence = sequence_input.upper()

    positions, gc_content = functions.calculate_gc_content(sequence, window_size)
    # plot = functions.plot_gc_content(positions, gc_content, window_size)

    total_length, counts = functions.calculate_nucleotide_counts(sequence)

    plot_data = [
        {"position": pos, "gc_content": gc} for pos, gc in zip(positions, gc_content)
    ]

    context.update(
        {
            "sequence": sequence_input,
            "window_size": window_size,
            "total_length": total_length,
            "nucleotides": counts,
            "gc_content": gc_content,
            "positions": positions,
            "plot_data": plot_data,
        }
    )

    return context  # Make sure to return the context
