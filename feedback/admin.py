"""
CareerAI Feedback Admin Configuration
"""

from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_rating', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Scores', {'fields': ('overall_rating', 'aptitude_score', 'resume_score', 'technical_score', 'communication_score')}),
        ('Feedback', {'fields': ('strengths', 'areas_for_improvement', 'recommendation')}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
