"""
CareerAI Accounts Admin Configuration
"""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'experience_level', 'phone', 'created_at']
    list_filter = ['target_role', 'experience_level']
    search_fields = ['user__username', 'user__email', 'user__first_name']
    readonly_fields = ['created_at']
    fieldsets = (
        ('User Info', {'fields': ('user', 'target_role', 'experience_level')}),
        ('Contact & Bio', {'fields': ('phone', 'bio')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
