"""
CareerAI Aptitude Admin Configuration
"""

from django.contrib import admin
from .models import Question, AptitudeResult, AptitudeAnswer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_short', 'category', 'difficulty', 'correct_answer']
    list_filter = ['category', 'difficulty']
    search_fields = ['question']
    
    def question_short(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_short.short_description = 'Question'


@admin.register(AptitudeResult)
class AptitudeResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'difficulty', 'category', 'score', 'total_questions', 'percentage', 'created_at']
    list_filter = ['difficulty', 'category', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(AptitudeAnswer)
class AptitudeAnswerAdmin(admin.ModelAdmin):
    list_display = ['result', 'question_short', 'selected_option', 'is_correct']
    
    def question_short(self, obj):
        return obj.question.question[:50]
    question_short.short_description = 'Question'
