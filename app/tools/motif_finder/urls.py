from django.urls import path
from . import views

urlpatterns = [
    path('', views.motif_finder, name='motif_finder'),
]