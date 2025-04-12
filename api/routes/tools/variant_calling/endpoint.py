from fastapi import APIRouter
# from . import functions

router = APIRouter(
    prefix="/variant_calling",
)

# @router.get("/")
# async def variant_calling(request: Request):
#     summary = None

#     if request.method == 'POST':
#         reference = request.get('reference', '') 
#         sequence_input = request.get('sequence', '').strip()
#         sequences = functions.parse_fasta_sequences(sequence_input)
#         reads = functions.generate_reads(sequences, read_length=10, coverage=3)
#         summary = functions.call_variants(reference, reads, threshold=0.7)
    
#     return render(request, "variant_calling.html", {"summary": summary})