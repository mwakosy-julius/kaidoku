from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import functions

router = APIRouter(
    prefix="/pairwise_alignment",
)


class PairwiseAlignment(BaseModel):
    sequence1: str
    sequence2: str
    alignment_type: str = "Global_Alignment"


@router.post("/")
def pairwise_alignment(request: PairwiseAlignment):
    sequence1 = request.sequence1
    sequence2 = request.sequence2
    alignment_type = request.alignment_type

    if sequence1 and sequence2:
        seq1 = functions.format_sequence(sequence1)
        seq2 = functions.format_sequence(sequence2)

        if functions.is_dna(seq1) and functions.is_dna(seq2):
            matrix = functions.matrix_subs()
            if alignment_type == "Global_Alignment":
                path_matrix = functions.lcs_global(seq1, seq2, matrix)
                results = functions.global_alignment(seq1, seq2, path_matrix, matrix)
            elif alignment_type == "Local_Alignment":
                score_matrix, path_matrix = functions.lcs_local(seq1, seq2, matrix)
                results = functions.local_alignment(
                    seq1, seq2, score_matrix, path_matrix, matrix
                )
            # similarity = round(results[0]/(results[0]+results[2]+results[3])*100)
            df = functions.table(sequence1, sequence2)
            bar_chart = functions.bar_chart(sequence1, sequence2)
            return {
                "results": {
                    "match_score": results[0],
                    "gap_open": results[1],
                    "gap_extend": results[2],
                    "alignment_score": results[3],
                    "similarity": round(results[0]/(results[0]+results[2]+results[3])*100),
                    "sequence1_aligned": results[4],
                    "sequence2_aligned": results[5],
                },
                "df": df.to_html(),
                "bar_chart": bar_chart.to_html(),
                "alignment_type": alignment_type,
            }
        else:
            raise HTTPException(
                status_code=400, detail="Sequences must be DNA sequences"
            )
    else:
        raise HTTPException(status_code=400, detail="Sequences cannot be empty")
