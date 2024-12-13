from django.urls import path
from . import views

urlpatterns = [
    path('', views.pairwise_alignment, name='pairwise_alignment'),
]