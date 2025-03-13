from typing import List, Optional
from pydantic import BaseModel


class DNASequence(BaseModel):
    sequence: str


class DNASequences(BaseModel):
    sequences: List[str]


class CompressionRequest(BaseModel):
    sequence: str
    method: str
    reference: Optional[str] = None


class CompressionResponse(BaseModel):
    original: str
    compressed: str
    method: str
    compression_ratio: float
