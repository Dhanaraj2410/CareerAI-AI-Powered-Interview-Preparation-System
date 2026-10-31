"""
CareerAI Aptitude App Configuration
"""

from django.apps import AppConfig


class AptitudeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aptitude'
    verbose_name = 'Aptitude Tests'