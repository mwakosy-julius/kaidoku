from django.urls import path
from . import views

urlpatterns = [
    path('', views.variant_calling, name='variant_calling'),
]