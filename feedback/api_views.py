import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Feedback
from .ai_service import generate_ai_career_feedback
from accounts.models import UserProfile
from aptitude.models import AptitudeResult
from resumes.models import UploadedResume
from interview.models import InterviewSession
from ml_engine.predictor import predict_candidate_performance

@csrf_exempt
def api_feedback_list_or_generate(request):
    user = request.user if request.user.is_authenticated else None
    if not user:
        from django.contrib.auth.models import User
        user = User.objects.first()

    if request.method == 'GET':
        feedbacks = Feedback.objects.filter(user=user).order_by('-created_at') if user else []
        res_list = []
        for fb in feedbacks:
            res_list.append({
                'id': fb.id,
                '_id': str(fb.id),
                'overallRating': fb.overall_rating,
                'strengths': fb.strengths,
                'areasForImprovement': fb.areas_for_improvement,
                'recommendation': fb.recommendation,
                'createdAt': fb.created_at.isoformat() if fb.created_at else ''
            })
        return JsonResponse({'feedbacks': res_list, 'data': res_list})

    elif request.method == 'POST':
        profile, _ = UserProfile.objects.get_or_create(user=user)

        latest_aptitude = AptitudeResult.objects.filter(user=user).order_by('-created_at').first()
        aptitude_score = round(latest_aptitude.percentage, 1) if latest_aptitude else 75.0

        latest_resume = UploadedResume.objects.filter(user=user).order_by('-uploaded_at').first()
        resume_score = round(latest_resume.resume_score, 1) if latest_resume else 78.0

        latest_interview = InterviewSession.objects.filter(user=user).order_by('-created_at').first()
        technical_score = round(latest_interview.total_score, 1) if latest_interview else 82.0
        communication_score = round(latest_interview.avg_confidence, 1) if latest_interview else 72.0

        res = generate_ai_career_feedback(
            aptitude_score=aptitude_score,
            resume_score=resume_score,
            technical_score=technical_score,
            communication_score=communication_score,
            target_role=profile.target_role
        )

        ml_pred = predict_candidate_performance(
            aptitude_score=aptitude_score,
            resume_score=resume_score,
            technical_score=technical_score,
            communication_score=communication_score
        )

        fb_obj = Feedback.objects.create(
            user=user,
            overall_rating=res['overall_rating'],
            strengths=res['strengths'],
            areas_for_improvement=res['areas_for_improvement'],
            recommendation=res['recommendation']
        )

        return JsonResponse({
            'status': 'success',
            'feedback': {
                'id': fb_obj.id,
                '_id': str(fb_obj.id),
                'overallRating': fb_obj.overall_rating,
                'strengths': fb_obj.strengths,
                'areasForImprovement': fb_obj.areas_for_improvement,
                'recommendation': fb_obj.recommendation,
                'selectionProbability': ml_pred['probability'],
                'selectionStatus': ml_pred['status'],
            }
        })

@csrf_exempt
def api_feedback_detail(request, pk):
    try:
        fb = Feedback.objects.get(pk=pk)
    except Feedback.DoesNotExist:
        return JsonResponse({'message': 'Feedback not found'}, status=404)

    if request.method == 'DELETE':
        fb.delete()
        return JsonResponse({'message': 'Feedback deleted successfully'})
    
    return JsonResponse({
        'feedback': {
            'id': fb.id,
            '_id': str(fb.id),
            'overallRating': fb.overall_rating,
            'strengths': fb.strengths,
            'areasForImprovement': fb.areas_for_improvement,
            'recommendation': fb.recommendation,
        }
    })
