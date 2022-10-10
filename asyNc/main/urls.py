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
    path('all_news/', views.news_response),
    path('login/', views.user_login),
    path('register/', views.user_register),
    path('modify_password/', views.user_modify_password),
]