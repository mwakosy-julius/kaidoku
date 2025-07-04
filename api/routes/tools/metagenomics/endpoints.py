from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from . import functions
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.responses import StreamingResponse
import io
import pandas as pd

class Taxon(BaseModel):
    genus: str
    abundance: float
    confidence: float  # Added to match functions.py

class Stats(BaseModel):
    total_reads: int
    classified_kmers: int
    unique_genera: int

class AnalysisResponse(BaseModel):
    taxa: List[Taxon]
    stats: Stats
    details: Optional[List[Dict]]  # Made optional for empty results

class MetagenomicsRequest(BaseModel):
    fasta_text: str
    description: Optional[str] = None

router = APIRouter(prefix="/metagenomics")

@router.post("/", response_model=AnalysisResponse)
async def analyze_metagenome(request: MetagenomicsRequest):
    """Analyze metagenomic FASTA for microbial taxa."""
    try:
        if not request.fasta_text.strip():
            raise HTTPException(status_code=400, detail="FASTA text cannot be empty")
        
        taxa, stats, details_df = functions.profile_taxa(request.fasta_text)
        
        # Handle empty details_df
        details = details_df.to_dict(orient="records") if not details_df.empty else []
        
        return {
            "taxa": taxa,
            "stats": stats,
            "details": details
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
            raise HTTPException(status_code=400, detail="No taxa identified for CSV export")

        csv_buffer = io.StringIO()
        details_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        return StreamingResponse(
            io.BytesIO(csv_buffer.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=metasimple_results.csv"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV generation failed: {str(e)}")