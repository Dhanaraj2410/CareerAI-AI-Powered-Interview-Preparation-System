from django import forms
from .models import Resume, UploadedResume
from accounts.models import UserProfile

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'objective', 'skills', 'education', 'experience', 'projects']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python Developer Resume'}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Career Objective'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, SQL, Machine Learning'}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'B.Tech in Computer Science...'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Software Engineering Intern at ABC Corp...'}),
            'projects': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'CareerAI Mock Interview System...'}),
        }

class ResumeUploadForm(forms.ModelForm):
    target_role = forms.ChoiceField(
        choices=UserProfile.JOB_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = UploadedResume
        fields = ['file', 'target_role']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }
