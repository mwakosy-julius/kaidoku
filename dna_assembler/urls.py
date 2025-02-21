from django.urls import path
from . import views

urlpatterns = [
    path('', views.dna_assembler, name='dna_assembler'),
]