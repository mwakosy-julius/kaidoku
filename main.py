from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, dna_assembler, data_compression

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
app.include_router(data_compression.router)


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
