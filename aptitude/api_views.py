"""
CareerAI Aptitude API Views - REST API for Aptitude Tests
--------------------------------------------------------
Provides JSON endpoints for starting aptitude tests, submitting
answers, and retrieving results.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, AptitudeResult
from .views import seed_sample_questions

@csrf_exempt
def api_get_questions(request, difficulty):
    seed_sample_questions()
    diff = difficulty.lower()
    questions_qs = Question.objects.filter(difficulty=diff)
    if not questions_qs.exists():
        questions_qs = Question.objects.all()
        
    formatted = []
    for q in questions_qs[:5]:
        formatted.append({
            '_id': str(q.id),
            'id': q.id,
            'question': q.question,
            'options': [q.option_a, q.option_b, q.option_c, q.option_d],
            'correctAnswer': q.correct_answer,
            'difficulty': q.difficulty,
            'topic': q.topic,
        })

    return JsonResponse({'questions': formatted})

@csrf_exempt
def api_submit_aptitude(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    answers = data.get('answers', {})
    difficulty = data.get('difficulty', 'medium')
    score = 0
    total = len(answers) if answers else 5

    for q_id, user_ans in answers.items():
        try:
            q = Question.objects.get(id=q_id)
            if str(user_ans).strip().upper() == q.correct_answer.strip().upper():
                score += 1
        except Exception:
            pass

    percentage = round((score / max(total, 1)) * 100, 2)

    user = request.user if request.user.is_authenticated else None
    if user:
        result = AptitudeResult.objects.create(
            user=user,
            difficulty=difficulty,
            score=score,
            total_questions=total,
            percentage=percentage
        )

    return JsonResponse({
        'status': 'success',
        'score': score,
        'totalQuestions': total,
        'percentage': percentage,
        'difficulty': difficulty,
        'message': f'Quiz submitted! Score: {score}/{total} ({percentage}%)'
    })
