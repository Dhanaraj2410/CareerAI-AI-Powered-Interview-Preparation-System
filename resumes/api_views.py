import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Resume, UploadedResume
from .utils import extract_resume_text, analyze_resume_nlp

def format_resume_obj(r):
    return {
        '_id': str(r.id),
        'id': r.id,
        'title': r.title,
        'personalInfo': {
            'fullName': f"{r.user.first_name} {r.user.last_name}".strip() or r.user.username,
            'email': r.user.email,
        },
        'objective': r.objective,
        'skills': r.skills,
        'education': [{'institution': r.education}] if r.education else [],
        'experience': [{'company': r.experience}] if r.experience else [],
        'projects': [{'name': r.projects}] if r.projects else [],
        'createdAt': r.created_at.isoformat() if r.created_at else '',
    }

@csrf_exempt
def api_resume_list(request):
    user = request.user if request.user.is_authenticated else None
    if request.method == 'GET':
        if user:
            qs = Resume.objects.filter(user=user)
        else:
            qs = Resume.objects.all()[:10]
        return JsonResponse({'resumes': [format_resume_obj(r) for r in qs]})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}

        title = data.get('title', 'Untitled Resume')
        skills = data.get('skills', '')
        if isinstance(skills, list):
            skills = ", ".join(skills)

        if not user:
            from django.contrib.auth.models import User
            user = User.objects.first()

        res_obj = Resume.objects.create(
            user=user,
            title=title,
            objective=data.get('objective', ''),
            skills=skills,
            education=str(data.get('education', '')),
            experience=str(data.get('experience', '')),
            projects=str(data.get('projects', '')),
        )
        return JsonResponse({'resume': format_resume_obj(res_obj)})

@csrf_exempt
def api_resume_detail(request, pk):
    try:
        r = Resume.objects.get(pk=pk)
    except Resume.DoesNotExist:
        return JsonResponse({'message': 'Resume not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'resume': format_resume_obj(r)})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}

        if 'title' in data: r.title = data['title']
        if 'objective' in data: r.objective = data['objective']
        if 'skills' in data:
            s = data['skills']
            r.skills = ", ".join(s) if isinstance(s, list) else str(s)
        if 'education' in data: r.education = str(data['education'])
        if 'experience' in data: r.experience = str(data['experience'])
        if 'projects' in data: r.projects = str(data['projects'])
        r.save()
        return JsonResponse({'resume': format_resume_obj(r)})

    elif request.method == 'DELETE':
        r.delete()
        return JsonResponse({'message': 'Resume deleted'})

@csrf_exempt
def api_resume_duplicate(request, pk):
    try:
        r = Resume.objects.get(pk=pk)
        dup = Resume.objects.create(
            user=r.user,
            title=f"{r.title} (Copy)",
            objective=r.objective,
            skills=r.skills,
            education=r.education,
            experience=r.experience,
            projects=r.projects,
        )
        return JsonResponse({'resume': format_resume_obj(dup)})
    except Resume.DoesNotExist:
        return JsonResponse({'message': 'Resume not found'}, status=404)

@csrf_exempt
def api_resume_analyze(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    target_role = request.POST.get('target_role', 'Python Developer')
    text = ""
    if 'file' in request.FILES:
        up_file = request.FILES['file']
        user = request.user if request.user.is_authenticated else None
        if not user:
            from django.contrib.auth.models import User
            user = User.objects.first()

        up_obj = UploadedResume.objects.create(
            user=user,
            file=up_file,
            target_role=target_role
        )
        text = extract_resume_text(up_obj.file.path)
    else:
        text = request.POST.get('resume_text', '')

    nlp_res = analyze_resume_nlp(text, target_role=target_role)

    return JsonResponse({
        'status': 'success',
        'resume_score': nlp_res['resume_score'],
        'extracted_skills': nlp_res['extracted_skills'],
        'missing_skills': nlp_res['missing_skills'],
        'coverage_score': nlp_res['coverage_score'],
        'tfidf_score': nlp_res['tfidf_score'],
    })
