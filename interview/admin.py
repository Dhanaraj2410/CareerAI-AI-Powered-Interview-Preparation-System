"""
CareerAI Interview Admin Configuration
"""

from django.contrib import admin
from .models import InterviewQuestionBank, InterviewSession, InterviewQuestion, InterviewAnswer


@admin.register(InterviewQuestionBank)
class InterviewQuestionBankAdmin(admin.ModelAdmin):
    list_display = ['role', 'section', 'section_title', 'topic', 'difficulty']
    list_filter = ['role', 'section', 'difficulty']
    search_fields = ['question_text', 'topic']


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'mode', 'status', 'total_score', 'completed', 'created_at']
    list_filter = ['role', 'mode', 'status', 'completed']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['session', 'section', 'section_title', 'question_short']
    
    def question_short(self, obj):
        return obj.question_text[:50]
    question_short.short_description = 'Question'


@admin.register(InterviewAnswer)
class InterviewAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question_short', 'final_score', 'status_tier', 'created_at']
    list_filter = ['status_tier', 'sentiment']
    readonly_fields = ['created_at']
    
    def question_short(self, obj):
        return obj.question.question_text[:40]
    question_short.short_description = 'Question'
