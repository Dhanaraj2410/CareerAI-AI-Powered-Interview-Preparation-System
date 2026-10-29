"""
CareerAI Aptitude Models - Database Schema Definitions
------------------------------------------------------
Defines database entities for aptitude question banks, step-by-step solution math,
formulas, historical user test results, and question-by-question user answer choices.
"""

from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Aptitude Question entity supporting Quantitative, Logical Reasoning,
    Verbal Ability, and Data Interpretation domains with step-by-step math solutions.
    """
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    CATEGORY_CHOICES = (
        ('quantitative', 'Quantitative Aptitude'),
        ('reasoning', 'Logical Reasoning'),
        ('verbal', 'Verbal Ability'),
        ('data_interpretation', 'Data Interpretation'),
    )

    question = models.TextField(help_text="Primary aptitude question statement")
    option_a = models.CharField(max_length=255, help_text="Option choice A")
    option_b = models.CharField(max_length=255, help_text="Option choice B")
    option_c = models.CharField(max_length=255, help_text="Option choice C")
    option_d = models.CharField(max_length=255, help_text="Option choice D")
    correct_answer = models.CharField(max_length=1, help_text="Correct option key: A, B, C, or D")
    explanation = models.TextField(blank=True, default='', help_text="Conceptual explanation of why this answer is correct")
    formula = models.CharField(max_length=255, blank=True, null=True, help_text="Math formula used to solve problem")
    solution_steps = models.TextField(blank=True, null=True, help_text="Step-by-step numerical calculation steps")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='quantitative')
    topic = models.CharField(max_length=100, default='General Aptitude')

    def get_option_text(self, option_key):
        """
        Maps option key ('A', 'B', 'C', 'D') to actual option choice text.
        Example: 'B' -> '60 km/h'
        """
        options = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }
        return options.get(option_key.upper() if option_key else '', 'Not Answered')

    def __str__(self):
        return f"[{self.category.upper()}] [{self.difficulty.upper()}] {self.question[:50]}..."


class AptitudeResult(models.Model):
    """
    Summary entity recording overall test performance, percentage accuracy,
    difficulty level, and category breakdown.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aptitude_results')
    difficulty = models.CharField(max_length=10)
    category = models.CharField(max_length=30, default='all')
    score = models.IntegerField(help_text="Number of questions answered correctly")
    total_questions = models.IntegerField(help_text="Total number of questions in test")
    percentage = models.FloatField(help_text="Percentage accuracy score")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.difficulty} - {self.percentage}%"


class AptitudeAnswer(models.Model):
    """
    Question-by-question answer record linking user's selected choice to AptitudeResult.
    """
    result = models.ForeignKey(AptitudeResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, help_text="Option selected by candidate: A, B, C, or D")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to Q{self.question.id} - {'Correct' if self.is_correct else 'Wrong'}"
