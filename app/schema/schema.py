from pydantic import BaseModel

class Sequence(BaseModel):
    sequence: str

class Consensus(BaseModel):
    sequence: str
    window_size: int