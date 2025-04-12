from fastapi import APIRouter, HTTPException
from . import functions

router = APIRouter(
    prefix="/variant_calling",
)

@router.get("/")
def hgjfghfj():
    return {""}