from django.urls import path
from . import views

urlpatterns = [
    path('', views.consensus_maker, name='consensus_maker'),
]