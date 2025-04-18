from fastapi import APIRouter, HTTPException
from . import functions
from pydantic import BaseModel

class Sequence(BaseModel):
    sequence: str

router = APIRouter(
    prefix="/dna_visualization",
)


@router.post("/")
def dna_visualization(sequence: Sequence):
    if sequence:
        sequence = functions.format_sequence(sequence)
        if functions.is_dna(sequence):
            transcript = functions.transcription(sequence)
            amino_acids = functions.translation(sequence)
            gc_content = functions.gc_content(sequence)
            dna_counts = functions.nucleotide_counts(sequence)
            dna_table = functions.dna_table(sequence)
            dna_chart = functions.dna_chart(sequence)
            amino_acid_counts = functions.amino_acid_counts(sequence)
            amino_acid_chart = functions.amino_acid_chart(sequence)

            context = {
                "transcript": transcript,
                "amino_acids": amino_acids,
                "gc_content": gc_content,
                "dna_counts": dna_counts,
                "dna_table": dna_table.to_html(),
                "dna_chart": dna_chart.to_html(),
                "amino_acid_counts": amino_acid_counts,
                "amino_acid_chart": amino_acid_chart.to_html()
            }
            return context
        else:
            error = "One or both sequences contain invalid DNA characters."
            return HTTPException(500, error)
