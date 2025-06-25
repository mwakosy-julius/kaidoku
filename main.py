from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from api.main import routing

# from core.db import create_db_and_tables
from core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: create database and tables
#     create_db_and_tables()
#     yield
#     # Shutdown: cleanup would go here


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
    generate_unique_id_function=custom_generate_unique_id,
)

# origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routing, prefix=settings.API_V_STR)
# app.include_router(auth_router)
# app.include_router(tools_router)
# app.include_router(dashboard_router)
# app.include_router(blogs_router)
# app.include_router(docs_router)
# app.include_router(testimonials_router)


# @app.get("/")
# async def root():
#     return {
#         "message": "Welcome to Kaidoku DNA API",
#         "docs": "/docs",
#         "available_tools": [
#             "Pairwise Alignment",
#             "Multiple Sequence Alignment",
#             "GC Content Calculator",
#             "Codon Usage Calculator",
#             "Data Compression Tool",
#             "MusicDNA",
#         ],
#     }


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
