import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile
from aptitude.models import AptitudeResult, CodingSubmission
from resumes.models import Resume, UploadedResume
from interview.models import InterviewSession, GDSession
from feedback.models import Feedback
from ml_engine.predictor import predict_candidate_performance
from careerai.gemini_service import (
    is_gemini_configured,
    check_gemini_health,
    chat_with_gemini_assistant,
    generate_ai_career_roadmap
)

logger = logging.getLogger('careerai.accounts')

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create UserProfile
            target_role = form.cleaned_data.get('target_role', 'Python Developer')
            UserProfile.objects.create(user=user, target_role=target_role)
            
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to CareerAI.")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'dashboard'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Calculate scores from user's actual sessions
    latest_aptitude = AptitudeResult.objects.filter(user=user).order_by('-created_at').first()
    aptitude_score = round(latest_aptitude.percentage, 1) if latest_aptitude else 75.0
    
    latest_resume = UploadedResume.objects.filter(user=user).order_by('-uploaded_at').first()
    resume_score = round(latest_resume.resume_score, 1) if latest_resume else 78.0
    
    latest_interview = InterviewSession.objects.filter(user=user).order_by('-created_at').first()
    technical_score = round(latest_interview.total_score, 1) if latest_interview else 82.0
    communication_score = round(latest_interview.avg_confidence, 1) if latest_interview else 72.0
    
    # Run ML Prediction
    ml_result = predict_candidate_performance(
        aptitude_score=aptitude_score,
        resume_score=resume_score,
        technical_score=technical_score,
        communication_score=communication_score
    )
    
    # Overall Performance
    overall_score = round((aptitude_score + resume_score + technical_score + communication_score) / 4.0, 1)
    
    latest_feedback = Feedback.objects.filter(user=user).order_by('-created_at').first()
    recent_interviews = InterviewSession.objects.filter(user=user).order_by('-created_at')[:5]
    coding_solved = CodingSubmission.objects.filter(user=user, status='Passed').values('question_id').distinct().count()
    gd_count = GDSession.objects.filter(user=user).count()
    
    context = {
        'profile': profile,
        'aptitude_score': aptitude_score,
        'resume_score': resume_score,
        'technical_score': technical_score,
        'communication_score': communication_score,
        'overall_score': overall_score,
        'ml_result': ml_result,
        'latest_feedback': latest_feedback,
        'recent_interviews': recent_interviews,
        'coding_solved': coding_solved,
        'gd_count': gd_count,
        'gemini_active': is_gemini_configured()
    }
    
    return render(request, 'dashboard.html', context)

# -------------------------------------------------------------------
# AI Learning Assistant / Chatbot Module
# -------------------------------------------------------------------

@login_required
def assistant_view(request):
    """Interactive AI Chatbot for technical domains, interview prep, and questions."""
    chat_history = request.session.get('ai_chat_history', [])
    return render(request, 'accounts/assistant.html', {
        'chat_history': chat_history,
        'gemini_active': is_gemini_configured()
    })

@login_required
def api_assistant_send(request):
    """Processes user chat messages and returns Markdown-formatted AI responses."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        user_message = body.get('message', '').strip()
    except Exception:
        user_message = request.POST.get('message', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Empty message provided'}, status=400)

    chat_history = request.session.get('ai_chat_history', [])
    
    # Query Gemini
    response_text, err = chat_with_gemini_assistant(user_message, history=chat_history)

    # Append to session history (capped at last 10 messages)
    chat_history.append({'role': 'user', 'text': user_message})
    chat_history.append({'role': 'model', 'text': response_text})
    if len(chat_history) > 12:
        chat_history = chat_history[-12:]
    request.session['ai_chat_history'] = chat_history

    return JsonResponse({
        'status': 'success',
        'reply': response_text,
        'error': err
    })

@login_required
def api_assistant_clear(request):
    """Clears conversation history."""
    if 'ai_chat_history' in request.session:
        del request.session['ai_chat_history']
    return JsonResponse({'status': 'cleared'})

# -------------------------------------------------------------------
# Job Recommendation & Career Roadmap Module
# -------------------------------------------------------------------

@login_required
def job_recommendations_view(request):
    """
    Recommends career paths, analyzes user skill gaps, and provides
    dynamic step-by-step roadmaps generated with Gemini AI.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Gather all extracted skills from user's latest resume or builder
    user_skills = set()
    latest_upload = UploadedResume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    if latest_upload and latest_upload.extracted_skills:
        for s in latest_upload.extracted_skills.split(','):
            if s.strip():
                user_skills.add(s.strip().title())

    latest_resume = Resume.objects.filter(user=request.user).order_by('-created_at').first()
    if latest_resume and latest_resume.skills:
        for s in latest_resume.skills.split(','):
            if s.strip():
                user_skills.add(s.strip().title())

    if not user_skills:
        user_skills = {'Python', 'Django', 'SQL', 'Git'}

    # Benchmark requirements for top software roles
    ROLE_BENCHMARKS = {
        'Python Developer': ['Python', 'Django', 'Flask', 'Sql', 'Rest Api', 'Git', 'Oop', 'Docker'],
        'Data Scientist': ['Python', 'Machine Learning', 'Data Analysis', 'Pandas', 'Numpy', 'Scikit-Learn', 'Statistics', 'Sql'],
        'Machine Learning Engineer': ['Python', 'Machine Learning', 'Deep Learning', 'Pytorch', 'Scikit-Learn', 'Nlp', 'Sql', 'Docker'],
        'Data Analyst': ['Python', 'Sql', 'Data Analysis', 'Pandas', 'Numpy', 'Tableau', 'Power Bi', 'Excel'],
        'Full Stack Developer': ['Javascript', 'React', 'Python', 'Django', 'Html', 'Css', 'Rest Api', 'Git']
    }

    user_skills_lower = {s.lower() for s in user_skills}
    recommendations = []

    for role_name, req_skills in ROLE_BENCHMARKS.items():
        matched = [s for s in req_skills if s.lower() in user_skills_lower]
        missing = [s for s in req_skills if s.lower() not in user_skills_lower]
        match_pct = round((len(matched) / len(req_skills)) * 100) if req_skills else 50
        
        recommendations.append({
            'role': role_name,
            'match_pct': match_pct,
            'matched_skills': matched,
            'missing_skills': missing,
            'total_skills': len(req_skills),
            'is_target': (role_name.lower() == profile.target_role.lower())
        })

    # Sort by match percentage descending
    recommendations.sort(key=lambda x: (x['is_target'], x['match_pct']), reverse=True)

    # Active selected roadmap (default to target role)
    selected_role = request.GET.get('role', profile.target_role)
    roadmap = generate_ai_career_roadmap(
        role=selected_role,
        current_skills=", ".join(user_skills)
    )

    return render(request, 'accounts/recommendations.html', {
        'profile': profile,
        'user_skills': sorted(list(user_skills)),
        'recommendations': recommendations,
        'selected_role': selected_role,
        'roadmap': roadmap,
        'gemini_active': is_gemini_configured()
    })

# -------------------------------------------------------------------
# Admin Gemini API Health-Check
# -------------------------------------------------------------------

@login_required
def gemini_health_view(request):
    """Administrative health-check view verifying Gemini SDK configuration."""
    health_data = check_gemini_health()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse(health_data)
        
    return render(request, 'accounts/health_check.html', {
        'health': health_data
    })
