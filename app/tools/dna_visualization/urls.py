from django.urls import path
from . import views

urlpatterns = [
    path('', views.dna_visualization, name='dna_visualization'),
]