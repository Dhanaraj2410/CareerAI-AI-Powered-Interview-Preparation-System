"""
CareerAI Feedback Models - AI Feedback Storage
----------------------------------------------
Stores AI-generated personalized career feedback reports
linked to user profiles and assessment scores.
"""

from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_reports')
    overall_rating = models.FloatField(default=0.0)
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    recommendation = models.TextField()
    aptitude_score = models.FloatField(default=0.0)
    resume_score = models.FloatField(default=0.0)
    technical_score = models.FloatField(default=0.0)
    communication_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Feedback ({self.created_at.strftime('%Y-%m-%d')})"
