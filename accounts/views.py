from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile
from aptitude.models import AptitudeResult
from resumes.models import Resume, UploadedResume
from interview.models import InterviewSession
from feedback.models import Feedback
from ml_engine.predictor import predict_candidate_performance

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
                return redirect('dashboard')
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
    
    context = {
        'profile': profile,
        'aptitude_score': aptitude_score,
        'resume_score': resume_score,
        'technical_score': technical_score,
        'communication_score': communication_score,
        'overall_score': overall_score,
        'ml_result': ml_result,
        'latest_feedback': latest_feedback,
        'recent_interviews': InterviewSession.objects.filter(user=user).order_by('-created_at')[:5],
    }
    
    return render(request, 'dashboard.html', context)
