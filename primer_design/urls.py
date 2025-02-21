from django.urls import path
from . import views

urlpatterns = [
    path('', views.primer_design, name='primer_design'),
]