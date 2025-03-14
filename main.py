from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth
from app.tools.blast import router as blast_router
from app.tools.dna_assembler import router as dna_assembler
from app.tools.codon_usage import router as codon_usage_router
from app.tools.consensus_maker import router as consensus_maker_router
from app.tools.data_compression import router as data_compression_router

app = FastAPI(
    title="Kaidoku DNA API",
    description="API for DNA analysis tools including assembly and compression",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dna_assembler.router)
app.include_router(blast_router.router)
app.include_router(codon_usage_router.router)
app.include_router(consensus_maker_router.router)
app.include_router(data_compression_router.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Kaidoku DNA API",
        "docs": "/docs",
        "available_tools": [
            "Pairwise Alignment",
            "Multiple Sequence Alignment",
            "GC Content Calculator",
            "Codon Usage Calculator",
            "Data Compression Tool",
            "MusicDNA",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
