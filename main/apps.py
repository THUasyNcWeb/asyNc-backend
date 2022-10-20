"""
    apps.py in django frame work
"""
from django.apps import AppConfig


class MainConfig(AppConfig):
    """
        MainConfig of Django App
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
