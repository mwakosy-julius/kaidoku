from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.db.database import create_db_and_tables
from app.routes.auth import router as auth_router
from app.tools.main import router as tools_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database and tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup would go here


app = FastAPI(
    title="Kaidoku DNA API",
    description="API for DNA analysis tools including assembly and compression",
    version="1.0.0",
    lifespan=lifespan,
)

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tools_router)


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
