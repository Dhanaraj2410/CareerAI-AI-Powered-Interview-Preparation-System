"""
CareerAI AI Mock Interview & Group Discussion (GD) Engine
---------------------------------------------------------
Powered by Google Gemini API and Multi-Factor NLP Evaluator.
Handles role-specific question generation, single-question flow,
answer evaluation with strengths/weaknesses, final report generation,
and corporate Group Discussion practice sessions.
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import InterviewQuestionBank, InterviewSession, InterviewQuestion, InterviewAnswer, GDTopic, GDSession
from .evaluator import evaluate_answer_learning, get_adaptive_difficulty
from careerai.gemini_service import (
    is_gemini_configured,
    generate_ai_interview_questions,
    evaluate_ai_interview_answer,
    generate_ai_gd_topic,
    evaluate_ai_gd_response
)

logger = logging.getLogger('careerai.interview')

AVAILABLE_ROLES = [
    "Python Developer",
    "Data Scientist",
    "ML Engineer",
    "Data Analyst",
    "Django Developer",
    "Full Stack Developer",
    "DevOps Engineer"
]

ROLE_MAP = {
    "Python Developer": "python",
    "Data Scientist": "data_science",
    "ML Engineer": "ml_engineer",
    "Data Analyst": "data_analyst",
    "Django Developer": "django",
    "Full Stack Developer": "python",
    "DevOps Engineer": "python"
}

INTERVIEW_SECTIONS = {
    "python": {
        1: "Python Fundamentals & Internals",
        2: "OOP & Advanced Design Patterns",
        3: "Django, REST APIs & Backend Architecture",
        4: "SQL, Relational Databases & ORM Optimization",
        5: "Data Structures & Algorithmic Problem Solving"
    },
    "data_science": {
        1: "Python & Data Wrangling",
        2: "Statistics & Probability",
        3: "Machine Learning Algorithms",
        4: "Deep Learning & Neural Networks",
        5: "SQL & Production Data Pipelines"
    },
    "ml_engineer": {
        1: "Python & Numerics",
        2: "Machine Learning System Design",
        3: "Deep Learning & PyTorch/TensorFlow",
        4: "NLP & Large Language Models (LLMs)",
        5: "MLOps, Monitoring & Deployment"
    },
    "data_analyst": {
        1: "Excel & Business Analytics",
        2: "SQL & Advanced Queries",
        3: "Python for Analytics (Pandas/NumPy)",
        4: "Data Visualization & Dashboards",
        5: "Case Studies & Key Metrics"
    },
    "django": {
        1: "Python Core & Asynchronous Execution",
        2: "Django ORM & Model Relationships",
        3: "REST APIs, DRF & Authentication",
        4: "Security, Caching & Performance",
        5: "Deployment & Microservices Architecture"
    }
}

def ensure_seed_questions():
    """Ensure interview question bank is seeded."""
    if not InterviewQuestionBank.objects.exists():
        try:
            from .seed_questions import seed_interview_questions
            seed_interview_questions()
        except Exception:
            pass

def ensure_seed_gd():
    """Ensure GD topics are seeded."""
    if not GDTopic.objects.exists():
        try:
            from .seed_gd import seed_gd_topics
            seed_gd_topics()
        except Exception:
            pass

# -------------------------------------------------------------------
# Mock Interview Views
# -------------------------------------------------------------------

@login_required
def interview_home(request):
    ensure_seed_questions()
    ensure_seed_gd()
    past_sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    recent_gd = GDSession.objects.filter(user=request.user).order_by('-created_at')[:3]

    return render(request, 'interview/home.html', {
        'roles': AVAILABLE_ROLES,
        'past_sessions': past_sessions,
        'recent_gd': recent_gd,
        'gemini_active': is_gemini_configured()
    })

@login_required
def start_interview(request):
    ensure_seed_questions()
    if request.method == 'POST':
        role_label = request.POST.get('role', 'Python Developer')
        role_key = ROLE_MAP.get(role_label, 'python')
        difficulty = request.POST.get('difficulty', 'Intermediate')
        interview_type = request.POST.get('interview_type', 'Technical')
        mode = request.POST.get('mode', 'text')
        total_q = int(request.POST.get('total_questions', 5))

        section_num = int(request.POST.get('section', 1))
        section_title = INTERVIEW_SECTIONS.get(role_key, {}).get(section_num, f"{interview_type} Assessment")

        session = InterviewSession.objects.create(
            user=request.user,
            role=role_label,
            interview_type=interview_type,
            difficulty=difficulty,
            mode=mode,
            total_questions=total_q,
            current_section=section_num,
            status='Active'
        )

        # 1. Attempt to generate dynamic questions via Gemini AI
        ai_questions = []
        if is_gemini_configured():
            try:
                ai_questions = generate_ai_interview_questions(
                    role=role_label,
                    difficulty=difficulty,
                    interview_type=interview_type,
                    count=total_q
                )
            except Exception as e:
                logger.warning("Gemini question generation error: %s", str(e))
                ai_questions = []

        if ai_questions:
            for item in ai_questions[:total_q]:
                InterviewQuestion.objects.create(
                    session=session,
                    section=section_num,
                    section_title=item.get('topic', section_title),
                    question_text=item.get('question_text', ''),
                    expected_concepts=item.get('expected_concepts', ''),
                    keywords=item.get('keywords', ''),
                    hint=item.get('hint', ''),
                    explanation=item.get('explanation', '')
                )
        else:
            # 2. Fallback to Curated Question Bank
            diff_filter = 'easy' if difficulty == 'Beginner' else ('hard' if difficulty == 'Advanced' else 'medium')
            bank_qs = list(InterviewQuestionBank.objects.filter(role=role_key, section=section_num).order_by('?'))
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

    # Adaptive Timer
    if session.difficulty.lower() in ['beginner', 'easy']:
        timer_seconds = 90
    elif session.difficulty.lower() in ['advanced', 'hard']:
        timer_seconds = 180
    else:
        timer_seconds = 120

    section_title = current_q.section_title or f"Question {q_index + 1}"

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

        # 1. NLP baseline evaluation
        nlp_eval = evaluate_answer_learning(
            expected_concepts=current_q.expected_concepts,
            keywords_str=current_q.keywords,
            user_answer=user_ans,
            hint_used=hint_used
        )

        # 2. Gemini AI Deep Evaluation
        ai_eval = evaluate_ai_interview_answer(
            role=session.role,
            question_text=current_q.question_text,
            user_answer=user_ans,
            expected_concepts=current_q.expected_concepts,
            keywords=current_q.keywords
        )

        # Blend scores (Gemini takes precedence if active, else NLP)
        if is_gemini_configured():
            final_score = round(ai_eval['score'], 1)
            feedback = ai_eval['feedback']
            status_tier = ai_eval['status_tier']
            strengths = "\n".join([f"✓ {s.lstrip('✓').strip()}" for s in ai_eval.get('strengths', [])])
            weaknesses = "\n".join([f"⚠ {w.lstrip('⚠').strip()}" for w in ai_eval.get('weaknesses', [])])
            improved_answer = ai_eval.get('improved_answer', current_q.expected_concepts)
        else:
            final_score = nlp_eval['final_score']
            feedback = nlp_eval['feedback']
            status_tier = nlp_eval['status_tier']
            strengths = "✓ " + "\n✓ ".join(ai_eval.get('strengths', ["Relevant attempt demonstrated"]))
            weaknesses = "⚠ " + "\n⚠ ".join(ai_eval.get('weaknesses', ["Could include additional technical depth"]))
            improved_answer = current_q.explanation or current_q.expected_concepts

        ans_obj, created = InterviewAnswer.objects.get_or_create(
            session=session,
            question=current_q,
            defaults={
                'user_answer': user_ans,
                'similarity_score': nlp_eval['similarity_score'],
                'keyword_score': nlp_eval['keyword_score'],
                'completeness_score': nlp_eval['completeness_score'],
                'confidence_score': nlp_eval['confidence_score'],
                'final_score': final_score,
                'missing_keywords': ", ".join(nlp_eval['missing_keywords']),
                'status_tier': status_tier,
                'sentiment': nlp_eval['sentiment'],
                'feedback': feedback,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'improved_answer': improved_answer,
                'hint_used': hint_used
            }
        )

        if not created:
            ans_obj.user_answer = user_ans
            ans_obj.similarity_score = nlp_eval['similarity_score']
            ans_obj.keyword_score = nlp_eval['keyword_score']
            ans_obj.completeness_score = nlp_eval['completeness_score']
            ans_obj.confidence_score = nlp_eval['confidence_score']
            ans_obj.final_score = final_score
            ans_obj.missing_keywords = ", ".join(nlp_eval['missing_keywords'])
            ans_obj.status_tier = status_tier
            ans_obj.sentiment = nlp_eval['sentiment']
            ans_obj.feedback = feedback
            ans_obj.strengths = strengths
            ans_obj.weaknesses = weaknesses
            ans_obj.improved_answer = improved_answer
            ans_obj.hint_used = hint_used
            ans_obj.attempt_number += 1
            ans_obj.save()

        return redirect('answer_feedback', session_id=session.id, q_index=q_index)

    return redirect('interview_home')

@login_required
def try_again(request, session_id, q_index):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    return redirect(f"/interview/active/{session.id}/{q_index}/?retry=true")

@login_required
def toggle_bookmark(request, session_id, q_index):
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
    strengths_list = [s.strip() for s in answer.strengths.split('\n') if s.strip()]
    weaknesses_list = [w.strip() for w in answer.weaknesses.split('\n') if w.strip()]

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
        'missing_keywords': missing_kw_list,
        'strengths_list': strengths_list,
        'weaknesses_list': weaknesses_list
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
    session.status = 'Completed'
    session.completed = True
    session.save()

    return render(request, 'interview/section_summary.html', {
        'session': session,
        'answers': answers,
        'strong_topics': strong_topics,
        'weak_topics': weak_topics
    })

@login_required
def interview_report(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answers = session.answers.all().select_related('question')

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
    """Creates a targeted revision session with weak questions (< 60%)."""
    prev_session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    weak_answers = prev_session.answers.filter(final_score__lt=60)

    if not weak_answers.exists():
        messages.success(request, "Great job! You have no weak questions under 60% score to revise.")
        return redirect('interview_report', session_id=prev_session.id)

    new_session = InterviewSession.objects.create(
        user=request.user,
        role=f"{prev_session.role} (Revision)",
        interview_type=prev_session.interview_type,
        difficulty='Beginner',
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

    messages.info(request, f"Targeted Revision launched with {weak_answers.count()} practice questions!")
    return redirect('active_question', session_id=new_session.id, q_index=0)

@login_required
def interview_history(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'interview/history.html', {'sessions': sessions})

# -------------------------------------------------------------------
# Group Discussion (GD) Module Views
# -------------------------------------------------------------------

@login_required
def gd_home(request):
    ensure_seed_gd()
    category = request.GET.get('category', 'all')
    topics = GDTopic.objects.all().order_by('-created_at')
    if category != 'all':
        topics = topics.filter(category=category)

    user_sessions = GDSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'interview/gd_home.html', {
        'topics': topics,
        'user_sessions': user_sessions,
        'active_category': category,
        'gemini_active': is_gemini_configured()
    })

@login_required
def gd_detail(request, topic_id):
    ensure_seed_gd()
    topic = get_object_or_404(GDTopic, id=topic_id)
    user_attempts = GDSession.objects.filter(user=request.user, topic=topic).order_by('-created_at')

    return render(request, 'interview/gd_detail.html', {
        'topic': topic,
        'attempts': user_attempts
    })

@login_required
def gd_submit(request, topic_id):
    if request.method != 'POST':
        return redirect('gd_detail', topic_id=topic_id)

    topic = get_object_or_404(GDTopic, id=topic_id)
    response_text = request.POST.get('response_text', '').strip()

    if not response_text:
        messages.error(request, "Please enter or speak your response before submitting.")
        return redirect('gd_detail', topic_id=topic_id)

    # Evaluate GD contribution with Gemini AI
    eval_res = evaluate_ai_gd_response(
        topic_title=topic.title,
        topic_description=topic.description,
        candidate_text=response_text
    )

    strengths_str = "\n".join([f"✓ {s.lstrip('✓').strip()}" for s in eval_res.get('strengths', [])])
    improvements_str = "\n".join([f"⚠ {i.lstrip('⚠').strip()}" for i in eval_res.get('improvements', [])])

    gd_session = GDSession.objects.create(
        user=request.user,
        topic=topic,
        candidate_response=response_text,
        overall_score=eval_res.get('overall_score', 75.0),
        relevance_score=eval_res.get('relevance_score', 75.0),
        clarity_score=eval_res.get('clarity_score', 75.0),
        structure_score=eval_res.get('structure_score', 75.0),
        feedback=eval_res.get('feedback', ''),
        strengths=strengths_str,
        improvements=improvements_str,
        key_takeaway=eval_res.get('key_takeaway', '')
    )

    messages.success(request, f"GD response evaluated! Score: {gd_session.overall_score}%")
    return redirect('gd_result', session_id=gd_session.id)

@login_required
def gd_result(request, session_id):
    session = get_object_or_404(GDSession, id=session_id, user=request.user)
    strengths_list = [s.strip() for s in session.strengths.split('\n') if s.strip()]
    improvements_list = [i.strip() for i in session.improvements.split('\n') if i.strip()]

    return render(request, 'interview/gd_result.html', {
        'session': session,
        'strengths_list': strengths_list,
        'improvements_list': improvements_list
    })

@login_required
def gd_generate_new(request):
    """Generates a dynamic new GD topic using Gemini AI."""
    category = request.GET.get('category', 'Tech Trends')
    topic_data = generate_ai_gd_topic(category=category)

    pro_str = "\n".join([f"- {p.lstrip('-').strip()}" for p in topic_data.get('pro_arguments', [])])
    con_str = "\n".join([f"- {c.lstrip('-').strip()}" for c in topic_data.get('con_arguments', [])])
    points_str = ", ".join(topic_data.get('key_discussion_points', []))

    topic = GDTopic.objects.create(
        title=topic_data.get('title', 'Contemporary Tech Leadership Debate'),
        category=topic_data.get('category', category),
        description=topic_data.get('description', ''),
        pro_arguments=pro_str,
        con_arguments=con_str,
        key_discussion_points=points_str
    )

    messages.success(request, f"New GD Topic generated with Gemini AI: '{topic.title}'")
    return redirect('gd_detail', topic_id=topic.id)
