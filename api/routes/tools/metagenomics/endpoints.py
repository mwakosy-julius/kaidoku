from fastapi import APIRouter, HTTPException, UploadFile, File, HTTPException, Form
from . import functions
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import StreamingResponse
import io

class Taxon(BaseModel):
    species: str
    abundance: float

class Stats(BaseModel):
    total_reads: int
    classified_kmers: int
    unique_species: int

class AnalysisResponse(BaseModel):
    taxa: List[Taxon]
    stats: Stats
    details: List[Dict]

router = APIRouter(
    prefix="/metagenomics",
)

@router.post("/analyze, response_model=AnalysisResponse")
async def analyze_metagenome(file: UploadFile = File(None), fasta_text: str = Form("")):
    """Analyze metagenomic FASTA."""
    try:
        if file:
            fasta_content = (await file.read()).decode("utf-8")
        elif fasta_text.strip():
            fasta_content = fasta_text
        else:
            raise HTTPException(status_code=400, detail="Provide FASTA file or text")
        
        taxa, stats, details_df = functions.profile_taxa(fasta_content)
        
        return {
            "taxa": taxa,
            "stats": stats,
            "details": details_df.to_dict(orient="records")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/download-csv")
async def download_csv(file: UploadFile = File(None), fasta_text: str = Form("")):
    """Generate and download CSV of analysis results."""
    try:
        if file:
            fasta_content = (await file.read()).decode("utf-8")
        elif fasta_text.strip():
            fasta_content = fasta_text
        else:
            raise HTTPException(status_code=400, detail="Provide FASTA file or text")
        
        _, _, details_df = functions.profile_taxa(fasta_content)
        if details_df.empty:
            raise HTTPException(status_code=400, detail="No taxa identified")
        
        csv_buffer = io.StringIO()
        details_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(csv_buffer.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=metasimple_results.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")