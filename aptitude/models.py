"""
CareerAI Aptitude & Coding Models - Database Schema Definitions
--------------------------------------------------------------
Defines database entities for aptitude question banks, step-by-step solution math,
formulas, historical user test results, and coding practice challenges for Python,
SQL, and Data Structures & Algorithms (DSA).
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
    result = models.ForeignKey(AptitudeResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, default='A', help_text="Option selected by candidate: A, B, C, or D")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to Q{self.question.id} - {'Correct' if self.is_correct else 'Wrong'}"


class CodingQuestion(models.Model):
    """
    Coding practice challenges for Python, SQL, and DSA with automated test cases.
    """
    CATEGORY_CHOICES = (
        ('python', 'Python Programming'),
        ('sql', 'SQL & Databases'),
        ('dsa', 'Data Structures & Algorithms'),
    )

    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='python')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    description = models.TextField(help_text="Full problem statement with constraints and examples")
    sample_input = models.TextField(blank=True, default='')
    sample_output = models.TextField(blank=True, default='')
    starter_code = models.TextField(blank=True, default='')
    solution_code = models.TextField(blank=True, default='')
    explanation = models.TextField(blank=True, default='')
    test_cases_json = models.TextField(default='[]', help_text="JSON list of test cases with inputs and expected outputs")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title) or "coding-question"
            self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.category.upper()}] {self.title} ({self.difficulty})"


class CodingSubmission(models.Model):
    """
    User submission attempt for a coding challenge with test evaluation results.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coding_submissions')
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    status = models.CharField(max_length=30, default='Pending') # 'Passed', 'Failed', 'Error'
    passed_tests = models.IntegerField(default=0)
    total_tests = models.IntegerField(default=0)
    output_log = models.TextField(blank=True, default='')
    ai_feedback = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.title} ({self.status})"
