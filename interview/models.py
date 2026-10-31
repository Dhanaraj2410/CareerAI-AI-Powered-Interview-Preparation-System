"""
CareerAI Interview Models - Database Schema Definitions
---------------------------------------------------------
Defines database entities for question banks, live interview sessions,
per-question tracking, answer evaluation metrics, revision records,
and Group Discussion (GD) practice sessions.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InterviewQuestionBank(models.Model):
    """
    Central repository of section-based technical interview questions
    categorized by role, section number, difficulty level, and expected concepts.
    """
    ROLE_CHOICES = (
        ('python', 'Python Developer'),
        ('data_science', 'Data Scientist'),
        ('ml_engineer', 'ML Engineer'),
        ('data_analyst', 'Data Analyst'),
        ('django', 'Django Developer'),
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, help_text="Target job role")
    section = models.IntegerField(default=1, help_text="Curriculum section index (1 to 5)")
    section_title = models.CharField(max_length=100, default='Fundamentals', help_text="Name of section module")
    topic = models.CharField(max_length=100, default='General', help_text="Specific domain topic")
    difficulty = models.CharField(max_length=20, default='medium', help_text="Adaptive difficulty level: easy, medium, hard")
    question_text = models.TextField(help_text="Primary technical interview question prompt")
    expected_concepts = models.TextField(help_text="Core technical concepts expected in candidate answer")
    keywords = models.TextField(help_text="Comma-separated key technical terms for keyword scoring")
    hint = models.TextField(blank=True, default='', help_text="Conceptual hint revealed upon candidate request")
    explanation = models.TextField(blank=True, default='', help_text="Detailed reference explanation for educational review")

    def __str__(self):
        return f"[{self.role.upper()}] Sec {self.section} ({self.difficulty}): {self.question_text[:50]}"

class InterviewSession(models.Model):
    """
    Tracks an active or completed user interview attempt including role,
    interview type, difficulty, mode, section progress, overall score, and weak topics.
    """
    INTERVIEW_TYPE_CHOICES = (
        ('Technical', 'Technical Deep-Dive'),
        ('HR', 'HR & Behavioral'),
        ('Coding', 'Coding & System Design'),
        ('Mixed', 'Comprehensive Mixed'),
    )

    DIFFICULTY_CHOICES = (
        ('Beginner', 'Beginner (0-1 yrs)'),
        ('Intermediate', 'Intermediate (1-3 yrs)'),
        ('Advanced', 'Advanced (3+ yrs)'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    role = models.CharField(max_length=100)
    interview_type = models.CharField(max_length=50, choices=INTERVIEW_TYPE_CHOICES, default='Technical')
    difficulty = models.CharField(max_length=50, default='Intermediate', help_text="Interview difficulty level")
    mode = models.CharField(max_length=20, default='text', help_text="Interview mode: text or voice-to-text")
    total_questions = models.IntegerField(default=5, help_text="Total number of questions in current session")
    current_section = models.IntegerField(default=1, help_text="Current section module index")
    current_question_index = models.IntegerField(default=0, help_text="Index of current question in session")
    total_score = models.FloatField(default=0.0, help_text="Aggregated percentage score")
    avg_confidence = models.FloatField(default=70.0, help_text="Average speech/text confidence rating")
    status = models.CharField(max_length=50, default='Active', help_text="Session status: Active, Completed, Revision")
    completed = models.BooleanField(default=False)
    weak_topics = models.TextField(blank=True, default='', help_text="JSON list of low-scoring question topics (< 60%)")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.role} [{self.interview_type}] ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class InterviewQuestion(models.Model):
    """
    Instance of a specific question bound to an active InterviewSession.
    """
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    section = models.IntegerField(default=1)
    section_title = models.CharField(max_length=100, default='Technical Assessment')
    question_text = models.TextField()
    expected_concepts = models.TextField()
    keywords = models.TextField(default='')
    hint = models.TextField(blank=True, default='')
    explanation = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Q (Sec {self.section}): {self.question_text[:50]}"

class InterviewAnswer(models.Model):
    """
    Stores multi-factor and Gemini AI evaluation metrics for a candidate's response.
    """
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='user_answers')
    user_answer = models.TextField(help_text="Raw text or transcribed voice response from candidate")
    similarity_score = models.FloatField(default=0.0, help_text="TF-IDF / Semantic similarity score")
    keyword_score = models.FloatField(default=0.0, help_text="Technical keyword match percentage")
    completeness_score = models.FloatField(default=0.0, help_text="Response completeness score")
    confidence_score = models.FloatField(default=70.0, help_text="Communication & confidence score")
    final_score = models.FloatField(default=0.0, help_text="Weighted final score percentage")
    missing_keywords = models.TextField(blank=True, default='', help_text="Extracted technical keywords missed")
    status_tier = models.CharField(max_length=50, default='Needs Improvement')
    sentiment = models.CharField(max_length=50, default='Neutral')
    feedback = models.TextField(blank=True, default='', help_text="Dynamic AI evaluator guidance feedback")
    strengths = models.TextField(blank=True, default='', help_text="Identified strengths in candidate answer")
    weaknesses = models.TextField(blank=True, default='', help_text="Identified weak points or conceptual gaps")
    improved_answer = models.TextField(blank=True, default='', help_text="Model ideal answer provided by Gemini")
    hint_used = models.BooleanField(default=False, help_text="Indicates if candidate requested a hint")
    bookmarked = models.BooleanField(default=False, help_text="Bookmarked by candidate for review")
    attempt_number = models.IntegerField(default=1, help_text="Number of attempts for this question")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Answer Q{self.question.id} - Final Score: {self.final_score}%"


class GDTopic(models.Model):
    """
    Predefined or Gemini-generated Group Discussion topics.
    """
    CATEGORY_CHOICES = (
        ('Tech Trends', 'Technology Trends & Disruption'),
        ('AI & Ethics', 'AI Ethics & Automation'),
        ('Corporate Culture', 'Workplace & Leadership Culture'),
        ('Current Affairs', 'Current Affairs & Industry Economics'),
    )

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Tech Trends')
    description = models.TextField(help_text="Contextual background and significance")
    pro_arguments = models.TextField(blank=True, default='', help_text="JSON or bullet list of supporting arguments")
    con_arguments = models.TextField(blank=True, default='', help_text="JSON or bullet list of counter arguments")
    key_discussion_points = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"


class GDSession(models.Model):
    """
    Candidate's practice attempt on a Group Discussion topic with AI evaluation.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gd_sessions')
    topic = models.ForeignKey(GDTopic, on_delete=models.CASCADE, related_name='attempts')
    candidate_response = models.TextField()
    overall_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    clarity_score = models.FloatField(default=0.0)
    structure_score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True, default='')
    strengths = models.TextField(blank=True, default='')
    improvements = models.TextField(blank=True, default='')
    key_takeaway = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - GD: {self.topic.title[:30]} ({self.overall_score}%)"
