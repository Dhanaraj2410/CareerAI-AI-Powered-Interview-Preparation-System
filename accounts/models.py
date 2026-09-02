from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    JOB_ROLE_CHOICES = (
        ('Python Developer', 'Python Developer'),
        ('Data Scientist', 'Data Scientist'),
        ('Machine Learning Engineer', 'Machine Learning Engineer'),
        ('Data Analyst', 'Data Analyst'),
        ('Web Developer', 'Web Developer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    target_role = models.CharField(max_length=100, choices=JOB_ROLE_CHOICES, default='Python Developer')
    bio = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    experience_level = models.CharField(max_length=50, default='Fresher / Entry Level')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - {self.target_role}"
