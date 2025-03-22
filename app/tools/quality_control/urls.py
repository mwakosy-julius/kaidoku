from django.urls import path
from . import views

urlpatterns = [
    path('', views.quality_control, name='quality_control'),
]