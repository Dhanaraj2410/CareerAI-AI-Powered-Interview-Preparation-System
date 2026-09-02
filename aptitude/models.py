from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
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

    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1)  # 'A', 'B', 'C', or 'D'
    explanation = models.TextField(blank=True, default='')
    formula = models.CharField(max_length=255, blank=True, null=True)
    solution_steps = models.TextField(blank=True, null=True)
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
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.difficulty} - {self.percentage}%"

class AptitudeAnswer(models.Model):
    result = models.ForeignKey(AptitudeResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, blank=True, default='')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Q{self.question.id} - Correct: {self.is_correct}"
