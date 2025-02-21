from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('musicdna/', include('musicdna.urls')),
    path('gc_content/', include('gc_content.urls')),
    path('codon_usage/', include('codon_usage.urls')),
    path('pairwise_alignment/', include('pairwise_alignment.urls')),
    path('multiple_alignment/', include('multiple_alignment.urls')),
    path('data_compression/', include('data_compression.urls')),
    path('blast/', include('blast.urls')),
    path('motif_finder/', include('motif_finder.urls')),
    path('dna_visualization/', include('dna_visualization.urls')),
    path('phylogenetic_trees/', include('phylogenetic_trees.urls')),
    path('consensus_maker/', include('consensus_maker.urls')),
    path('variant_calling/', include('variant_calling.urls')),
    path('quality_control/', include('quality_control.urls')),
    path('dna_assembler/', include('dna_assembler.urls')),
    path('primer_design/', include('primer_design.urls')),
    path('metagenomics/', include('metagenomics.urls')),
]
