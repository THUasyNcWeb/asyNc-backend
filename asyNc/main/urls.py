"""
urls.py for main
created by sxx
2022.10.5
"""

from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('index/', views.index),
]