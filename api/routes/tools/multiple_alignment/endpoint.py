from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import io
from functions import align_sequences

router = APIRouter(
    prefix="/multiple_alignment",
)

# Models
class Taxon(BaseModel):
    position: int
    conservation: float

class Stats(BaseModel):
    num_sequences: int
    alignment_length: int
    avg_conservation: float

class AnalysisResponse(BaseModel):
    taxa: List[Taxon]
    stats: Stats
    details: List[Dict]
    clustal: str

# Endpoints
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_sequences(
    file: UploadFile = File(None),
    fasta_text: str = Form(""),
    seq_type: str = Form("nucleotide")
):
    """Perform multiple sequence alignment."""
    try:
        if seq_type not in ["nucleotide", "protein"]:
            raise HTTPException(status_code=400, detail="Sequence type must be 'nucleotide' or 'protein'")
        
        if file:
            content = (await file.read()).decode("utf-8")
        elif fasta_text.strip():
            content = fasta_text
        else:
            raise HTTPException(status_code=400, detail="Provide FASTA file or text")
        
        taxa, stats, details_df, clustal = align_sequences(content, seq_type)
        
        return {
            "taxa": taxa,
            "stats": stats,
            "details": details_df.to_dict(orient="records"),
            "clustal": clustal
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/download-csv")
async def download_csv(
    file: UploadFile = File(None),
    fasta_text: str = Form(""),
    seq_type: str = Form("nucleotide")
):
    """Download CSV of identity matrix."""
    try:
        if seq_type not in ["nucleotide", "protein"]:
            raise HTTPException(status_code=400, detail="Sequence type must be 'nucleotide' or 'protein'")
        
        if file:
            content = (await file.read()).decode("utf-8")
        elif fasta_text.strip():
            content = fasta_text
        else:
            raise HTTPException(status_code=400, detail="Provide FASTA file or text")
        
        _, _, details_df, _ = align_sequences(content, seq_type)
        if details_df.empty:
            raise HTTPException(status_code=400, detail="No alignment generated")
        
        csv_buffer = io.StringIO()
        details_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(csv_buffer.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=metaalign_identity.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

