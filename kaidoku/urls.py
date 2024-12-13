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
]
