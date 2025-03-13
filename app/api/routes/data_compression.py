from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.dna import CompressionRequest, CompressionResponse
from app.services.data_compression.run_length import run_length_encoding
from app.services.data_compression.delta_compression import delta_compress
from app.services.data_compression.consensus import generate_consensus, read_fasta

router = APIRouter(
    prefix="/data_compression",
    tags=["data compression"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=CompressionResponse)
async def compress_data(request: CompressionRequest):
    """
    Compress DNA sequence data using the specified method.
    """
    original_length = len(request.sequence)

    if original_length == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty sequence provided"
        )

    try:
        if request.method == "run_length":
            compressed = run_length_encoding(request.sequence)
        elif request.method == "delta":
            if not request.reference:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reference sequence required for delta compression",
                )
            compressed = delta_compress(request.sequence, request.reference)
        elif request.method == "consensus":
            sequences = read_fasta(request.sequence)
            if len(sequences) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Multiple sequences required for consensus",
                )
            compressed = generate_consensus(sequences)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown compression method: {request.method}",
            )

        # Calculate compression ratio
        compressed_length = len(compressed)
        ratio = 0 if compressed_length == 0 else original_length / compressed_length

        return {
            "original": request.sequence,
            "compressed": compressed,
            "method": request.method,
            "compression_ratio": ratio,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compression error: {str(e)}",
        )
