from fastapi import APIRouter

from api.routes.index import index_routing
from api.routes.tools.main import router as tools_router

routing = APIRouter()

routing.include_router(index_routing, tags=["Index Route"])
routing.include_router(tools_router, tags=["Tools"])