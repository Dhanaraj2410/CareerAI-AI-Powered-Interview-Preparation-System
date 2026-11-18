from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Feedback
from .ai_service import generate_ai_career_feedback
from accounts.models import UserProfile
from aptitude.models import AptitudeResult
from resumes.models import UploadedResume
from interview.models import InterviewSession
from accounts.progress import latest_scores

@login_required
def generate_feedback_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    scores = latest_scores(user)
    aptitude_score = scores['aptitude'] or 0
    resume_score = scores['resume'] or 0
    technical_score = scores['technical'] or 0
    communication_score = scores['communication'] or 0

    # Call AI Feedback Service
    res = generate_ai_career_feedback(
        aptitude_score=aptitude_score,
        resume_score=resume_score,
        technical_score=technical_score,
        communication_score=communication_score,
        target_role=profile.target_role
    )

    feedback_obj = Feedback.objects.create(
        user=user,
        overall_rating=res['overall_rating'],
        strengths=res['strengths'],
        areas_for_improvement=res['areas_for_improvement'],
        recommendation=res['recommendation'],
        aptitude_score=aptitude_score,
        resume_score=resume_score,
        technical_score=technical_score,
        communication_score=communication_score
    )

    messages.success(request, "AI Personalized Career Feedback Report Generated!")
    return redirect('view_feedback', feedback_id=feedback_obj.id)

@login_required
def view_feedback_view(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    return render(request, 'feedback/detail.html', {'feedback': feedback})

@login_required
def feedback_history_view(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'feedback/history.html', {'feedbacks': feedbacks})
