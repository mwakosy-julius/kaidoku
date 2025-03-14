from django.urls import path
from . import views

urlpatterns = [
    path('', views.gc_content, name='gc_content'),
]