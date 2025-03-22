from fastapi import APIRouter, Depends

from app.core.security import get_current_active_user
from app.tools.blast import router as blast_router
from app.tools.codon_usage import router as codon_usage_router
from app.tools.consensus_maker import router as consensus_maker_router
from app.tools.data_compression import router as data_compression_router
from app.tools.dna_assembler import router as dna_assembler_router
from app.tools.dna_visualization import endpoint as dna_visualization_router
from app.tools.gc_content import endpoint as gc_content_router
from app.tools.metagenomics import endpoints as metagenomics_router
from app.tools.motif_finder import endpoint as motif_finder_router
from app.tools.multiple_alignment import endpoint as multiple_alignment_router
from app.tools.musicdna import endpoint as musicdna_router
router = APIRouter(
    prefix="/tools",
    tags=["BioInformatics Tools"],
    dependencies=[Depends(get_current_active_user)]
)

router.include_router(blast_router.router)
router.include_router(codon_usage_router.router)
router.include_router(consensus_maker_router.router)
router.include_router(data_compression_router.router)
router.include_router(dna_assembler_router.router)
router.include_router(dna_visualization_router.router)
router.include_router(gc_content_router.router)
router.include_router(metagenomics_router.router)
router.include_router(motif_finder_router.router)
router.include_router(multiple_alignment_router.router)
router.include_router(musicdna_router.router)