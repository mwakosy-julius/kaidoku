from django.urls import path
from . import views

urlpatterns = [
    path('', views.multiple_alignment, name='multiple_alignment'),
]