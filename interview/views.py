import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InterviewQuestionBank, InterviewSession, InterviewQuestion, InterviewAnswer
from .evaluator import evaluate_answer_learning, get_adaptive_difficulty

INTERVIEW_SECTIONS = {
    "python": {
        1: "Python Fundamentals",
        2: "OOP & Advanced Python",
        3: "Django & APIs",
        4: "SQL & Database",
        5: "Problem Solving"
    },
    "data_science": {
        1: "Python & Data Wrangling",
        2: "Statistics & Probability",
        3: "Machine Learning",
        4: "Deep Learning",
        5: "SQL & Data Projects"
    },
    "ml_engineer": {
        1: "Python & Numerics",
        2: "Machine Learning Models",
        3: "Deep Learning & PyTorch",
        4: "NLP & LLMs",
        5: "MLOps & Deployment"
    },
    "data_analyst": {
        1: "Excel & Business Analytics",
        2: "SQL & Databases",
        3: "Python for Analytics",
        4: "Data Visualization",
        5: "Case Studies & Metrics"
    },
    "django": {
        1: "Python Core",
        2: "Django ORM & Models",
        3: "REST APIs & DRF",
        4: "Authentication & Security",
        5: "Deployment & Architecture"
    }
}

ROLE_MAP = {
    "Python Developer": "python",
    "Data Scientist": "data_science",
    "ML Engineer": "ml_engineer",
    "Data Analyst": "data_analyst",
    "Django Developer": "django"
}

def ensure_seed_questions():
    """Ensure interview question bank is seeded."""
    if InterviewQuestionBank.objects.exists():
        return
    try:
        from .seed_questions import seed_interview_questions
        seed_interview_questions()
    except Exception:
        pass

@login_required
def interview_home(request):
    ensure_seed_questions()
    past_sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'interview/home.html', {
        'roles': list(ROLE_MAP.keys()),
        'past_sessions': past_sessions
    })

@login_required
def start_interview(request):
    ensure_seed_questions()
    if request.method == 'POST':
        role_label = request.POST.get('role', 'Python Developer')
        role_key = ROLE_MAP.get(role_label, 'python')
        section_num = int(request.POST.get('section', 1))
        difficulty = request.POST.get('difficulty', 'medium')
        mode = request.POST.get('mode', 'text')
        total_q = int(request.POST.get('total_questions', 5))

        section_title = INTERVIEW_SECTIONS.get(role_key, {}).get(section_num, "Technical Assessment")

        session = InterviewSession.objects.create(
            user=request.user,
            role=role_label,
            mode=mode,
            difficulty=difficulty,
            total_questions=total_q,
            current_section=section_num,
            status='Active'
        )

        # Draw random questions from bank for this role & section
        bank_qs = list(InterviewQuestionBank.objects.filter(
            role=role_key,
            section=section_num
        ).order_by('?'))

        if not bank_qs:
            bank_qs = list(InterviewQuestionBank.objects.filter(role=role_key).order_by('?'))
        if not bank_qs:
            bank_qs = list(InterviewQuestionBank.objects.order_by('?'))

        selected_qs = bank_qs[:total_q]

        for q in selected_qs:
            InterviewQuestion.objects.create(
                session=session,
                section=section_num,
                section_title=section_title,
                question_text=q.question_text,
                expected_concepts=q.expected_concepts,
                keywords=q.keywords,
                hint=q.hint,
                explanation=q.explanation
            )

        return redirect('active_question', session_id=session.id, q_index=0)

    return redirect('interview_home')

@login_required
def active_question(request, session_id, q_index=0):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = session.questions.all().order_by('id')

    if q_index >= len(questions):
        return redirect('section_summary', session_id=session.id)

    current_q = questions[q_index]
    existing_answer = InterviewAnswer.objects.filter(session=session, question=current_q).first()

    show_hint = request.GET.get('hint') == 'true'

    # Per-question time limit based on difficulty
    if session.difficulty == 'easy':
        timer_seconds = 60
    elif session.difficulty == 'hard':
        timer_seconds = 180
    else:
        timer_seconds = 120

    section_title = current_q.section_title or INTERVIEW_SECTIONS.get(ROLE_MAP.get(session.role, 'python'), {}).get(session.current_section, "Technical Assessment")

    return render(request, 'interview/active.html', {
        'session': session,
        'question': current_q,
        'q_index': q_index,
        'total_questions': len(questions),
        'existing_answer': existing_answer,
        'timer_seconds': timer_seconds,
        'section_title': section_title,
        'show_hint': show_hint,
        'progress_percent': int((q_index + 1) / len(questions) * 100)
    })

@login_required
def submit_answer(request, session_id, q_index):
    if request.method == 'POST':
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
        questions = session.questions.all().order_by('id')

        if q_index >= len(questions):
            return redirect('section_summary', session_id=session.id)

        current_q = questions[q_index]
        user_ans = request.POST.get('user_answer', '').strip()
        hint_used = request.POST.get('hint_used') == 'true'

        # Multi-factor Learning Evaluator
        eval_res = evaluate_answer_learning(
            expected_concepts=current_q.expected_concepts,
            keywords_str=current_q.keywords,
            user_answer=user_ans,
            hint_used=hint_used
        )

        ans_obj, created = InterviewAnswer.objects.get_or_create(
            session=session,
            question=current_q,
            defaults={
                'user_answer': user_ans,
                'similarity_score': eval_res['similarity_score'],
                'keyword_score': eval_res['keyword_score'],
                'completeness_score': eval_res['completeness_score'],
                'confidence_score': eval_res['confidence_score'],
                'final_score': eval_res['final_score'],
                'missing_keywords': ", ".join(eval_res['missing_keywords']),
                'status_tier': eval_res['status_tier'],
                'sentiment': eval_res['sentiment'],
                'feedback': eval_res['feedback'],
                'hint_used': hint_used
            }
        )

        if not created:
            ans_obj.user_answer = user_ans
            ans_obj.similarity_score = eval_res['similarity_score']
            ans_obj.keyword_score = eval_res['keyword_score']
            ans_obj.completeness_score = eval_res['completeness_score']
            ans_obj.confidence_score = eval_res['confidence_score']
            ans_obj.final_score = eval_res['final_score']
            ans_obj.missing_keywords = ", ".join(eval_res['missing_keywords'])
            ans_obj.status_tier = eval_res['status_tier']
            ans_obj.sentiment = eval_res['sentiment']
            ans_obj.feedback = eval_res['feedback']
            ans_obj.hint_used = hint_used
            ans_obj.attempt_number += 1
            ans_obj.save()

        # Adaptive difficulty scaling
        next_difficulty = get_adaptive_difficulty(eval_res['final_score'])
        session.difficulty = next_difficulty
        session.save()

        return redirect('answer_feedback', session_id=session.id, q_index=q_index)

    return redirect('interview_home')

@login_required
def try_again(request, session_id, q_index):
    """Allows candidate to re-attempt question."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    return redirect(f"/interview/active/{session.id}/{q_index}/?retry=true")

@login_required
def toggle_bookmark(request, session_id, q_index):
    """Toggles bookmark status on an answer."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = session.questions.all().order_by('id')
    if q_index < len(questions):
        q = questions[q_index]
        ans = InterviewAnswer.objects.filter(session=session, question=q).first()
        if ans:
            ans.bookmarked = not ans.bookmarked
            ans.save()
            messages.info(request, "Bookmark updated for revision!")
    return redirect('answer_feedback', session_id=session.id, q_index=q_index)

@login_required
def answer_feedback(request, session_id, q_index):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = session.questions.all().order_by('id')

    if q_index >= len(questions):
        return redirect('section_summary', session_id=session.id)

    current_q = questions[q_index]
    answer = get_object_or_404(InterviewAnswer, session=session, question=current_q)

    missing_kw_list = [k.strip() for k in answer.missing_keywords.split(',') if k.strip()]
    next_q_index = q_index + 1
    is_last_question = (next_q_index >= len(questions))

    return render(request, 'interview/feedback_step.html', {
        'session': session,
        'question': current_q,
        'answer': answer,
        'q_index': q_index,
        'next_q_index': next_q_index,
        'is_last_question': is_last_question,
        'total_questions': len(questions),
        'missing_keywords': missing_kw_list
    })

@login_required
def section_summary(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answers = session.answers.all().select_related('question')

    strong_topics = []
    weak_topics = []

    if answers.exists():
        avg_score = sum(a.final_score for a in answers) / len(answers)
        avg_conf = sum(a.confidence_score for a in answers) / len(answers)
        session.total_score = round(avg_score, 1)
        session.avg_confidence = round(avg_conf, 1)

        for a in answers:
            if a.final_score >= 65:
                strong_topics.append(a.question.question_text[:40] + "...")
            else:
                weak_topics.append(a.question.question_text[:40] + "...")

    session.weak_topics = json.dumps(weak_topics)

    next_section = session.current_section + 1
    role_key = ROLE_MAP.get(session.role, 'python')
    has_next_section = next_section in INTERVIEW_SECTIONS.get(role_key, {})

    if not has_next_section:
        session.status = 'Completed'
        session.completed = True

    session.save()

    return render(request, 'interview/section_summary.html', {
        'session': session,
        'answers': answers,
        'current_section_title': INTERVIEW_SECTIONS.get(role_key, {}).get(session.current_section, "Section"),
        'next_section': next_section,
        'has_next_section': has_next_section,
        'next_section_title': INTERVIEW_SECTIONS.get(role_key, {}).get(next_section, "Next Section"),
        'strong_topics': strong_topics,
        'weak_topics': weak_topics
    })

@login_required
def interview_report(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answers = session.answers.all().select_related('question')

    # Readiness status calculation
    if session.total_score >= 80:
        readiness_status = "EXCELLENT PROFILE"
        readiness_badge = "badge-prediction-pass"
    elif session.total_score >= 65:
        readiness_status = "HIGH READINESS"
        readiness_badge = "badge-prediction-pass"
    elif session.total_score >= 50:
        readiness_status = "MODERATE READINESS"
        readiness_badge = "badge-prediction-warn"
    else:
        readiness_status = "NEEDS IMPROVEMENT"
        readiness_badge = "badge-prediction-danger"

    weak_answers = [a for a in answers if a.final_score < 60]
    strong_answers = [a for a in answers if a.final_score >= 60]

    return render(request, 'interview/report.html', {
        'session': session,
        'answers': answers,
        'readiness_status': readiness_status,
        'readiness_badge': readiness_badge,
        'weak_answers': weak_answers,
        'strong_answers': strong_answers
    })

@login_required
def start_revision(request, session_id):
    """Creates a targeted revision session containing only weak/incorrect questions (score < 60%)."""
    prev_session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    weak_answers = prev_session.answers.filter(final_score__lt=60)

    if not weak_answers.exists():
        messages.success(request, "Great job! You have no weak questions under 60% score to revise.")
        return redirect('interview_report', session_id=prev_session.id)

    new_session = InterviewSession.objects.create(
        user=request.user,
        role=f"{prev_session.role} (Revision Mode)",
        mode=prev_session.mode,
        difficulty='easy',
        total_questions=weak_answers.count(),
        status='Active'
    )

    for wa in weak_answers:
        q = wa.question
        InterviewQuestion.objects.create(
            session=new_session,
            section=q.section,
            section_title=f"Revision: {q.section_title}",
            question_text=q.question_text,
            expected_concepts=q.expected_concepts,
            keywords=q.keywords,
            hint=q.hint,
            explanation=q.explanation
        )

    messages.info(request, f"Targeted Revision Mode launched with {weak_answers.count()} practice questions!")
    return redirect('active_question', session_id=new_session.id, q_index=0)

@login_required
def interview_history(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'interview/history.html', {'sessions': sessions})
