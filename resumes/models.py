"""
CareerAI Resumes Models - Resume Storage Schema
-----------------------------------------------
Defines resume builder records and uploaded resume files
with NLP analysis and ATS scoring results.
"""

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default='My Professional Resume')
    objective = models.TextField(blank=True, default='')
    skills = models.TextField(help_text="Comma-separated skills e.g., Python, Django, SQL, Machine Learning")
    education = models.TextField(blank=True, default='')
    experience = models.TextField(blank=True, default='')
    projects = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class UploadedResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resumes')
    file = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True, default='')
    extracted_skills = models.TextField(blank=True, default='')
    target_role = models.CharField(max_length=100, default='Python Developer')
    resume_score = models.FloatField(default=0.0)
    missing_skills = models.TextField(blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Resume Score: {self.resume_score}% ({self.target_role})"
