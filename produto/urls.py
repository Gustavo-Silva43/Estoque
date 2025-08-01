# produto/urls.py
from django.urls import path

from core.views import index
from . import views

urlpatterns = [
    path('', index, name='index'),
]