import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Question, AptitudeResult, AptitudeAnswer

CATEGORY_LABELS = {
    'quantitative': 'Quantitative Aptitude',
    'reasoning': 'Logical Reasoning',
    'verbal': 'Verbal Ability',
    'data_interpretation': 'Data Interpretation'
}

def seed_sample_questions():
    """Ensure baseline aptitude questions exist in database."""
    if Question.objects.exists():
        return
    try:
        from .seed_questions import seed_aptitude_questions
        seed_aptitude_questions()
    except Exception:
        pass

@login_required
def aptitude_home(request):
    seed_sample_questions()
    user_results = AptitudeResult.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'aptitude/home.html', {'results': user_results})

@login_required
def aptitude_test(request, difficulty):
    seed_sample_questions()
    session_key = f'aptitude_questions_{difficulty.lower()}'
    
    if request.GET.get('new') == 'true' or session_key not in request.session:
        easy_qs = list(Question.objects.filter(difficulty='easy').order_by('?')[:4])
        med_qs = list(Question.objects.filter(difficulty='medium').order_by('?')[:3])
        hard_qs = list(Question.objects.filter(difficulty='hard').order_by('?')[:3])
        
        sampled = easy_qs + med_qs + hard_qs
        if len(sampled) < 5:
            sampled = list(Question.objects.order_by('?')[:10])
            
        q_ids = [q.id for q in sampled]
        request.session[session_key] = q_ids

    q_ids = request.session.get(session_key, [])
    questions = list(Question.objects.filter(id__in=q_ids))
    
    time_limit_seconds = 300  # 5 minutes
    
    return render(request, 'aptitude/test.html', {
        'questions': questions,
        'difficulty': difficulty,
        'time_limit_seconds': time_limit_seconds,
    })

@login_required
def aptitude_submit(request):
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty', 'medium')
        question_ids = request.POST.getlist('question_ids')
        
        score = 0
        total = len(question_ids)
        
        result = AptitudeResult.objects.create(
            user=request.user,
            difficulty=difficulty,
            score=0,
            total_questions=total,
            percentage=0.0
        )
        
        for q_id in question_ids:
            user_ans = request.POST.get(f'question_{q_id}', '').strip().upper()
            try:
                question = Question.objects.get(id=q_id)
                is_correct = bool(user_ans and user_ans == question.correct_answer.strip().upper())
                if is_correct:
                    score += 1
                
                AptitudeAnswer.objects.create(
                    result=result,
                    question=question,
                    selected_answer=user_ans,
                    is_correct=is_correct
                )
            except Question.DoesNotExist:
                continue
                
        percentage = round((score / total * 100), 2) if total > 0 else 0.0
        result.score = score
        result.percentage = percentage
        result.save()
        
        # Clear session key so next attempt gets fresh random questions
        session_key = f'aptitude_questions_{difficulty.lower()}'
        if session_key in request.session:
            del request.session[session_key]
        
        messages.success(request, f"Aptitude test completed! Score: {score}/{total} ({percentage}%)")
        return redirect('aptitude_result', result_id=result.id)
        
    return redirect('aptitude_home')

@login_required
def aptitude_result(request, result_id):
    result = get_object_or_404(AptitudeResult, id=result_id, user=request.user)
    answers = result.answers.all().select_related('question')
    
    answer_details = []
    category_stats = {}
    wrong_count = 0
    correct_count = 0
    
    for ans in answers:
        q = ans.question
        cat = q.category
        if cat not in category_stats:
            category_stats[cat] = {'label': CATEGORY_LABELS.get(cat, cat.title()), 'total': 0, 'correct': 0}
            
        category_stats[cat]['total'] += 1
        
        if ans.is_correct:
            correct_count += 1
            category_stats[cat]['correct'] += 1
        else:
            wrong_count += 1

        answer_details.append({
            'question': q,
            'selected_answer': ans.selected_answer,
            'selected_answer_text': q.get_option_text(ans.selected_answer),
            'correct_answer': q.correct_answer,
            'correct_answer_text': q.get_option_text(q.correct_answer),
            'is_correct': ans.is_correct,
            'explanation': q.explanation,
            'formula': q.formula,
            'solution_steps': q.solution_steps
        })

    # Calculate percentage for each category & identify weak categories
    weak_categories = []
    category_breakdown = []
    for cat, stats in category_stats.items():
        pct = round((stats['correct'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
        category_breakdown.append({
            'name': stats['label'],
            'score': stats['correct'],
            'total': stats['total'],
            'percentage': pct
        })
        if pct < 60:
            weak_categories.append(stats['label'])

    return render(request, 'aptitude/result.html', {
        'result': result,
        'answer_details': answer_details,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'category_breakdown': category_breakdown,
        'weak_categories': weak_categories
    })

@login_required
def aptitude_retry_wrong(request, result_id):
    """Creates a new test attempt containing only the incorrect/unanswered questions from previous attempt."""
    prev_result = get_object_or_404(AptitudeResult, id=result_id, user=request.user)
    wrong_answers = prev_result.answers.filter(is_correct=False)
    
    if not wrong_answers.exists():
        messages.success(request, "Excellent! You scored 100% on this test — no wrong questions to retry.")
        return redirect('aptitude_result', result_id=prev_result.id)

    q_ids = [wa.question.id for wa in wrong_answers]
    session_key = f'aptitude_questions_{prev_result.difficulty.lower()}'
    request.session[session_key] = q_ids

    messages.info(request, f"Retrying {len(q_ids)} incorrect questions!")
    return redirect('aptitude_test', difficulty=prev_result.difficulty)
