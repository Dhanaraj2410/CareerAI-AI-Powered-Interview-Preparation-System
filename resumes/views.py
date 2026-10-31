import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Resume, UploadedResume
from .forms import ResumeForm, ResumeUploadForm
from .utils import extract_resume_text, analyze_resume_nlp
from .pdf_generator import generate_resume_pdf
from careerai.gemini_service import is_gemini_configured, generate_ai_resume_summary

@login_required
def resume_home(request):
    user_resumes = Resume.objects.filter(user=request.user).order_by('-created_at')
    user_uploads = UploadedResume.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'resumes/home.html', {
        'resumes': user_resumes,
        'uploads': user_uploads,
        'gemini_active': is_gemini_configured()
    })

@login_required
def resume_builder(request, pk=None):
    if pk:
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
    else:
        resume = None
        
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            new_resume = form.save(commit=False)
            new_resume.user = request.user
            new_resume.save()
            messages.success(request, "Resume saved successfully!")
            return redirect('resume_preview', pk=new_resume.pk)
    else:
        form = ResumeForm(instance=resume)
        
    return render(request, 'resumes/builder.html', {
        'form': form,
        'resume': resume,
        'gemini_active': is_gemini_configured()
    })

@login_required
def resume_preview(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    skills_list = [s.strip() for s in resume.skills.split(',') if s.strip()]
    return render(request, 'resumes/preview.html', {
        'resume': resume,
        'skills_list': skills_list
    })

@login_required
def resume_download_pdf(request, pk):
    """Generates and streams an ATS-formatted PDF resume."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    pdf_bytes = generate_resume_pdf(resume)
    
    filename = f"Resume_{request.user.username}_{resume.id}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def api_generate_ai_summary(request):
    """AJAX endpoint to generate high-impact executive summary using Gemini."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    target_role = data.get('target_role') or getattr(getattr(request.user, 'profile', None), 'target_role', 'Python Developer')
    skills = data.get('skills', '')
    experience = data.get('experience', '')
    education = data.get('education', '')
    name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username

    summary = generate_ai_resume_summary(
        name=name,
        target_role=target_role,
        skills=skills,
        experience=experience,
        education=education
    )

    return JsonResponse({'summary': summary})

@login_required
def resume_analyzer(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_obj = form.save(commit=False)
            uploaded_obj.user = request.user
            uploaded_obj.save()
            
            # NLP & Gemini Processing
            file_path = uploaded_obj.file.path
            raw_text = extract_resume_text(file_path)
            nlp_res = analyze_resume_nlp(raw_text, target_role=uploaded_obj.target_role)
            
            uploaded_obj.raw_text = raw_text
            uploaded_obj.extracted_skills = ", ".join(nlp_res['extracted_skills'])
            uploaded_obj.resume_score = nlp_res['resume_score']
            uploaded_obj.missing_skills = ", ".join(nlp_res['missing_skills'])
            uploaded_obj.save()
            
            messages.success(request, f"Resume analyzed! ATS NLP Score: {nlp_res['resume_score']}%")
            return render(request, 'resumes/analyzer_result.html', {
                'upload': uploaded_obj,
                'nlp': nlp_res
            })
    else:
        form = ResumeUploadForm()
        
    return render(request, 'resumes/analyzer.html', {'form': form})
