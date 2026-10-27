"""
CareerAI Interview API Views - REST API for Interview Module
------------------------------------------------------------
Provides JSON endpoints for interview flow, answer submission,
evaluation, and session management.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewQuestionBank
from .evaluator import evaluate_answer_learning, analyze_sentiment
from .views import ROLE_MAP

def parse_json(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except Exception:
        return {}

@csrf_exempt
def api_interview_setup(request):
    data = parse_json(request)
    role = data.get('role', 'Python Developer')
    return JsonResponse({
        'status': 'success',
        'role': role,
        'availableRoles': list(ROLE_MAP.keys())
    })

@csrf_exempt
def api_interview_history(request):
    user = request.user if request.user.is_authenticated else None
    if user:
        sessions = InterviewSession.objects.filter(user=user).order_by('-created_at')
    else:
        sessions = InterviewSession.objects.all().order_by('-created_at')[:10]

    history = []
    for s in sessions:
        history.append({
            'id': s.id,
            '_id': str(s.id),
            'role': s.role,
            'totalScore': s.total_score,
            'avgConfidence': s.avg_confidence,
            'status': s.status,
            'createdAt': s.created_at.isoformat() if s.created_at else ''
        })

    return JsonResponse({'history': history, 'sessions': history})

@csrf_exempt
def api_interview_start(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    data = parse_json(request)
    role_label = data.get('role', 'Python Developer')
    role_key = ROLE_MAP.get(role_label, 'python')
    user = request.user if request.user.is_authenticated else None
    if not user:
        from django.contrib.auth.models import User
        user = User.objects.first()

    session = InterviewSession.objects.create(
        user=user,
        role=role_label,
        mode=data.get('mode', 'text'),
        difficulty=data.get('difficulty', 'medium'),
        status='Active'
    )

    bank_qs = list(InterviewQuestionBank.objects.filter(role=role_key).order_by('?'))
    if not bank_qs:
        bank_qs = list(InterviewQuestionBank.objects.order_by('?'))

    created_q = []
    for q in bank_qs[:5]:
        obj = InterviewQuestion.objects.create(
            session=session,
            section=q.section,
            section_title=q.section_title,
            question_text=q.question_text,
            expected_concepts=q.expected_concepts,
            keywords=q.keywords
        )
        created_q.append(obj)

    first_q = created_q[0]
    return JsonResponse({
        'status': 'success',
        'sessionId': session.id,
        'questionIndex': 0,
        'totalQuestions': len(created_q),
        'question': {
            'id': first_q.id,
            'questionText': first_q.question_text
        }
    })

@csrf_exempt
def api_interview_reply(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    data = parse_json(request)
    session_id = data.get('sessionId')
    q_index = data.get('questionIndex', 0)
    user_answer = data.get('userAnswer', '').strip()

    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({'message': 'Interview session not found'}, status=404)

    questions = list(session.questions.all().order_by('id'))
    if q_index < len(questions):
        curr_q = questions[q_index]
        eval_res = evaluate_answer_learning(curr_q.expected_concepts, curr_q.keywords, user_answer)

        InterviewAnswer.objects.create(
            session=session,
            question=curr_q,
            user_answer=user_answer,
            similarity_score=eval_res['similarity_score'],
            keyword_score=eval_res['keyword_score'],
            completeness_score=eval_res['completeness_score'],
            confidence_score=eval_res['confidence_score'],
            final_score=eval_res['final_score'],
            sentiment=eval_res['sentiment'],
            feedback=eval_res['feedback']
        )

    next_index = q_index + 1
    if next_index < len(questions):
        next_q = questions[next_index]
        return JsonResponse({
            'status': 'success',
            'isFinished': False,
            'sessionId': session.id,
            'questionIndex': next_index,
            'totalQuestions': len(questions),
            'question': {
                'id': next_q.id,
                'questionText': next_q.question_text
            }
        })
    else:
        answers = session.answers.all()
        if answers.exists():
            session.total_score = round(sum(a.final_score for a in answers) / len(answers), 1)
            session.avg_confidence = round(sum(a.confidence_score for a in answers) / len(answers), 1)
        session.status = 'Completed'
        session.completed = True
        session.save()

        return JsonResponse({
            'status': 'success',
            'isFinished': True,
            'sessionId': session.id,
            'totalScore': session.total_score,
            'avgConfidence': session.avg_confidence,
            'message': 'Interview session completed successfully!'
        })

@csrf_exempt
def api_interview_end(request):
    data = parse_json(request)
    session_id = data.get('sessionId')
    if session_id:
        try:
            session = InterviewSession.objects.get(id=session_id)
            answers = session.answers.all()
            if answers.exists():
                session.total_score = round(sum(a.final_score for a in answers) / len(answers), 1)
                session.avg_confidence = round(sum(a.confidence_score for a in answers) / len(answers), 1)
            session.status = 'Completed'
            session.completed = True
            session.save()
            return JsonResponse({'status': 'success', 'totalScore': session.total_score})
        except Exception:
            pass
    return JsonResponse({'status': 'success'})
