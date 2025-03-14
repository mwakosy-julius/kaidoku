from django.urls import path
from . import views

urlpatterns = [
    path('', views.phylogenetic_trees, name='phylogenetic_trees'),
]