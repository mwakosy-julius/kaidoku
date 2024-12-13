from django.urls import path
from . import views

urlpatterns = [
    path('', views.codon_usage, name='codon_usage'),
]