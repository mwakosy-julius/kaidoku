from fastapi import APIRouter, Depends

from core.security import get_current_active_user
from api.routes.tools.sequence_search import router as sequence_search_router
from api.routes.tools.blast import endpoint as blast_router
from api.routes.tools.codon_usage import router as codon_usage_router
from api.routes.tools.consensus_maker import router as consensus_maker_router
from api.routes.tools.data_compression import router as data_compression_router
from api.routes.tools.dna_visualization import endpoint as dna_visualization_router
from api.routes.tools.gc_content import endpoint as gc_content_router
from api.routes.tools.metagenomics import endpoints as metagenomics_router
from api.routes.tools.motif_finder import endpoint as motif_finder_router
from api.routes.tools.multiple_alignment import endpoint as multiple_alignment_router
from api.routes.tools.musicdna import endpoint as musicdna_router
from api.routes.tools.pairwise_alignment import endpoint as pairwise_alignment_router
from api.routes.tools.phylogenetic_trees import endpoint as phylogenetic_trees_router
from api.routes.tools.variant_calling import endpoint as variant_calling_router
from api.routes.tools.protein_structure import endpoint as protein_structure_router
from api.routes.tools.sequence_mutator import endpoint as sequence_mutator_router

router = APIRouter(
    prefix="/tools",
    dependencies=[Depends(get_current_active_user)]
)

router.include_router(blast_router.router)
router.include_router(codon_usage_router.router)
router.include_router(consensus_maker_router.router)
router.include_router(data_compression_router.router)
router.include_router(dna_visualization_router.router)
router.include_router(gc_content_router.router)
router.include_router(metagenomics_router.router)
router.include_router(motif_finder_router.router)
router.include_router(multiple_alignment_router.router)
router.include_router(musicdna_router.router)
router.include_router(pairwise_alignment_router.router)
router.include_router(phylogenetic_trees_router.router)
router.include_router(variant_calling_router.router)
router.include_router(sequence_search_router.router)
router.include_router(protein_structure_router.router)
router.include_router(sequence_mutator_router.router)