from fastapi import APIRouter, HTTPException
from . import functions
import random

from ...schema.schema import Sequence

router = APIRouter(
    prefix="/musicdna",
)



@router.post('/')
def musicdna(request: Sequence):
    result = ''
    sequence = request.sequence
    if sequence:
        sequence = functions.sequence_validator(sequence)
        if functions.is_dna(sequence):
            melody = functions.melody_maker(sequence)
            functions.play_melody(melody)
        else:
            return HTTPException(404, "Invalid sequence")

    context = {'result': result}
    return context
