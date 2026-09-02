from django.db import models
from django.contrib.auth.models import User

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    overall_rating = models.FloatField(default=7.5)
    strengths = models.TextField(help_text="Bullet points or newline separated strengths")
    areas_for_improvement = models.TextField(help_text="Bullet points or newline separated weak areas")
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Feedback for {self.user.username} - Rating: {self.overall_rating}/10"
