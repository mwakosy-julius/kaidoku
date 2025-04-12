from fastapi import APIRouter

from api.routes.index import index_routing
from api.routes.tools.main import router as tools_router
from api.routes.auth.main import router as auth_router

routing = APIRouter()

routing.include_router(index_routing, tags=["Index Route"])
routing.include_router(tools_router, tags=["Tools"])
routing.include_router(auth_router, tags=["Authentication"])