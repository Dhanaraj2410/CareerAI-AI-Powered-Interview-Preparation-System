"""
CareerAI Resumes Admin Configuration
"""

from django.contrib import admin
from .models import Resume, UploadedResume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at']


@admin.register(UploadedResume)
class UploadedResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'resume_score', 'uploaded_at']
    list_filter = ['target_role', 'uploaded_at']
    search_fields = ['user__username']
    readonly_fields = ['uploaded_at']
