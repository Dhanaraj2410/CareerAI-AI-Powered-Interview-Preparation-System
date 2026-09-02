from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InterviewQuestionBank(models.Model):
    ROLE_CHOICES = (
        ('python', 'Python Developer'),
        ('data_science', 'Data Scientist'),
        ('ml_engineer', 'ML Engineer'),
        ('data_analyst', 'Data Analyst'),
        ('django', 'Django Developer'),
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    section = models.IntegerField(default=1)  # 1 to 5
    section_title = models.CharField(max_length=100, default='Fundamentals')
    topic = models.CharField(max_length=100, default='General')
    difficulty = models.CharField(max_length=20, default='medium')  # easy, medium, hard
    question_text = models.TextField()
    expected_concepts = models.TextField()
    keywords = models.TextField(help_text="Comma-separated key technical terms")
    hint = models.TextField(blank=True, default='')
    explanation = models.TextField(blank=True, default='')

    def __str__(self):
        return f"[{self.role.upper()}] Sec {self.section} ({self.difficulty}): {self.question_text[:50]}"

class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    role = models.CharField(max_length=100)
    mode = models.CharField(max_length=20, default='text')  # text or voice
    difficulty = models.CharField(max_length=20, default='medium')
    total_questions = models.IntegerField(default=10)
    current_section = models.IntegerField(default=1)
    current_question_index = models.IntegerField(default=0)
    total_score = models.FloatField(default=0.0)
    avg_confidence = models.FloatField(default=70.0)
    status = models.CharField(max_length=50, default='Active')  # Active, Completed, Revision
    completed = models.BooleanField(default=False)
    weak_topics = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    section = models.IntegerField(default=1)
    section_title = models.CharField(max_length=100, default='Fundamentals')
    question_text = models.TextField()
    expected_concepts = models.TextField()
    keywords = models.TextField(default='')
    hint = models.TextField(blank=True, default='')
    explanation = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Q (Sec {self.section}): {self.question_text[:50]}"

class InterviewAnswer(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='user_answers')
    user_answer = models.TextField()
    similarity_score = models.FloatField(default=0.0)
    keyword_score = models.FloatField(default=0.0)
    completeness_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=70.0)
    final_score = models.FloatField(default=0.0)
    missing_keywords = models.TextField(blank=True, default='')
    status_tier = models.CharField(max_length=50, default='Needs Improvement')  # Excellent, Good, Average, Needs Improvement
    sentiment = models.CharField(max_length=50, default='Neutral')
    feedback = models.TextField(blank=True, default='')
    hint_used = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Answer Q{self.question.id} - Final Score: {self.final_score}%"
