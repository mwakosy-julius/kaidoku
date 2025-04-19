from fastapi import APIRouter, HTTPException
from . import functions
from pydantic import BaseModel


class Sequence(BaseModel):
    sequence: str


router = APIRouter(
    prefix="/dna_visualization",
)


@router.post("/")
def dna_visualization(request: Sequence):
    if request.sequence:
        sequence = functions.format_sequence(request.sequence)
        if functions.is_dna(sequence):
            transcript = functions.transcription(sequence)
            amino_acids = functions.translation(sequence)
            gc_content = functions.gc_content(sequence)
            dna_counts, dna_percentages = functions.nucleotide_counts(sequence)
            amino_acid_counts, amino_acid_percentages = functions.amino_acid_counts(
                sequence
            )

            context = {
                "transcript": transcript,
                "amino_acids": amino_acids,
                "gc_content": gc_content,
                "dna_counts": dna_counts,
                "dna_percentages": dna_percentages,
                "amino_acid_counts": amino_acid_counts,
                "amino_acid_percentages": amino_acid_percentages,
            }
            return context
        else:
            raise HTTPException(status_code=400, detail="Invalid DNA sequence")
    else:
        raise HTTPException(status_code=400, detail="No sequence provided")
