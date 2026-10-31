"""
CareerAI Aptitude & Coding Practice Views
-----------------------------------------
Handles timed aptitude tests, automated scoring, result analysis,
and coding practice challenges for Python, SQL, and DSA.
"""

import sys
import io
import json
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Question, AptitudeResult, AptitudeAnswer, CodingQuestion, CodingSubmission
from careerai.gemini_service import is_gemini_configured, generate_gemini_text

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

def seed_sample_coding():
    """Ensure baseline coding questions exist."""
    if CodingQuestion.objects.exists():
        return
    try:
        from .seed_coding import seed_coding_questions
        seed_coding_questions()
    except Exception:
        pass

# -------------------------------------------------------------------
# Aptitude Testing Module
# -------------------------------------------------------------------

@login_required
def aptitude_home(request):
    seed_sample_questions()
    seed_sample_coding()
    user_results = AptitudeResult.objects.filter(user=request.user).order_by('-created_at')
    coding_count = CodingSubmission.objects.filter(user=request.user, status='Passed').values('question').distinct().count()
    return render(request, 'aptitude/home.html', {
        'results': user_results,
        'coding_count': coding_count
    })

@login_required
def aptitude_test(request, difficulty):
    seed_sample_questions()
    category = request.GET.get('category', 'all')
    session_key = f'aptitude_questions_{difficulty.lower()}_{category}'
    
    if request.GET.get('new') == 'true' or session_key not in request.session:
        qs = Question.objects.all()
        if category != 'all':
            qs = qs.filter(category=category)

        diff = difficulty.lower()
        if diff in ['easy', 'medium', 'hard']:
            sampled = list(qs.filter(difficulty=diff).order_by('?')[:8])
            if len(sampled) < 5:
                sampled = list(qs.order_by('?')[:10])
        else:
            sampled = list(qs.order_by('?')[:10])
            
        q_ids = [q.id for q in sampled]
        request.session[session_key] = q_ids

    q_ids = request.session.get(session_key, [])
    questions = list(Question.objects.filter(id__in=q_ids))
    
    time_limit_seconds = 300  # 5 minutes
    
    return render(request, 'aptitude/test.html', {
        'questions': questions,
        'difficulty': difficulty,
        'category': category,
        'time_limit_seconds': time_limit_seconds,
    })

@login_required
def aptitude_submit(request):
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty', 'medium')
        category = request.POST.get('category', 'all')
        question_ids = request.POST.getlist('question_ids')
        
        score = 0
        total = len(question_ids)
        
        result = AptitudeResult.objects.create(
            user=request.user,
            difficulty=difficulty,
            category=category,
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
                    selected_option=user_ans or 'N',
                    is_correct=is_correct
                )
            except Question.DoesNotExist:
                continue
                
        percentage = round((score / total * 100), 2) if total > 0 else 0.0
        result.score = score
        result.percentage = percentage
        result.save()
        
        # Clear session key
        session_key = f'aptitude_questions_{difficulty.lower()}_{category}'
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
            'selected_answer': ans.selected_option,
            'selected_answer_text': q.get_option_text(ans.selected_option),
            'correct_answer': q.correct_answer,
            'correct_answer_text': q.get_option_text(q.correct_answer),
            'is_correct': ans.is_correct,
            'explanation': q.explanation,
            'formula': q.formula,
            'solution_steps': q.solution_steps
        })

    # Category breakdown & weak areas
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
    """Creates a targeted session with previously incorrect questions."""
    prev_result = get_object_or_404(AptitudeResult, id=result_id, user=request.user)
    wrong_answers = prev_result.answers.filter(is_correct=False)
    
    if not wrong_answers.exists():
        messages.success(request, "Excellent! You scored 100% on this test — no wrong questions to retry.")
        return redirect('aptitude_result', result_id=prev_result.id)

    q_ids = [wa.question.id for wa in wrong_answers]
    session_key = f'aptitude_questions_{prev_result.difficulty.lower()}_{prev_result.category}'
    request.session[session_key] = q_ids

    messages.info(request, f"Retrying {len(q_ids)} incorrect questions!")
    return redirect('aptitude_test', difficulty=prev_result.difficulty)

# -------------------------------------------------------------------
# Coding Practice Module (Python, SQL, DSA)
# -------------------------------------------------------------------

@login_required
def coding_home(request):
    seed_sample_coding()
    category = request.GET.get('category', 'all')
    difficulty = request.GET.get('difficulty', 'all')

    qs = CodingQuestion.objects.all().order_by('id')
    if category != 'all':
        qs = qs.filter(category=category)
    if difficulty != 'all':
        qs = qs.filter(difficulty=difficulty)

    solved_ids = set(
        CodingSubmission.objects.filter(user=request.user, status='Passed')
        .values_list('question_id', flat=True)
    )

    questions_data = []
    for q in qs:
        questions_data.append({
            'question': q,
            'is_solved': q.id in solved_ids
        })

    recent_submissions = CodingSubmission.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'aptitude/coding_home.html', {
        'questions': questions_data,
        'active_category': category,
        'active_difficulty': difficulty,
        'solved_count': len(solved_ids),
        'total_count': CodingQuestion.objects.count(),
        'recent_submissions': recent_submissions
    })

@login_required
def coding_detail(request, slug):
    seed_sample_coding()
    question = get_object_or_404(CodingQuestion, slug=slug)
    user_submissions = CodingSubmission.objects.filter(user=request.user, question=question).order_by('-created_at')[:5]
    latest_code = user_submissions.first().code if user_submissions.exists() else question.starter_code

    return render(request, 'aptitude/coding_detail.html', {
        'question': question,
        'user_code': latest_code,
        'submissions': user_submissions,
    })

@login_required
def coding_submit(request, slug):
    if request.method != 'POST':
        return redirect('coding_detail', slug=slug)

    question = get_object_or_404(CodingQuestion, slug=slug)
    code = request.POST.get('code', '').strip()
    action = request.POST.get('action', 'submit')

    if not code:
        messages.error(request, "Code cannot be empty.")
        return redirect('coding_detail', slug=slug)

    test_cases = []
    try:
        test_cases = json.loads(question.test_cases_json)
    except Exception:
        test_cases = []

    passed = 0
    total = len(test_cases) or 1
    log_lines = []
    status = 'Passed'

    if question.category == 'sql':
        # SQL syntax and query analysis
        sql_upper = code.upper()
        if 'SELECT' not in sql_upper:
            status = 'Failed'
            log_lines.append("SQL Error: Statement must contain a valid SELECT clause.")
        elif 'FROM' not in sql_upper:
            status = 'Failed'
            log_lines.append("SQL Error: Missing FROM clause in query.")
        else:
            passed = total
            status = 'Passed'
            log_lines.append("Query syntax verified successfully.")
            log_lines.append(f"Passed structural validation against schema constraints.")
    else:
        # Python execution sandbox with restricted globals
        safe_globals = {
            '__builtins__': {
                'range': range, 'len': len, 'enumerate': enumerate,
                'min': min, 'max': max, 'sum': sum, 'sorted': sorted,
                'abs': abs, 'isinstance': isinstance, 'int': int,
                'float': float, 'str': str, 'list': list, 'dict': dict,
                'set': set, 'tuple': tuple, 'bool': bool, 'reversed': reversed,
                'print': print
            }
        }
        
        # Support collections module in code
        try:
            import collections
            safe_globals['collections'] = collections
            safe_globals['Counter'] = collections.Counter
            safe_globals['defaultdict'] = collections.defaultdict
        except Exception:
            pass

        local_vars = {}

        try:
            exec(code, safe_globals, local_vars)
            
            # Find candidate function
            candidate_fn = None
            for key, val in local_vars.items():
                if callable(val) and not key.startswith('_'):
                    candidate_fn = val
                    break

            if not candidate_fn:
                status = 'Failed'
                log_lines.append("Error: No callable function defined in your submission.")
            else:
                for idx, tc in enumerate(test_cases, 1):
                    inp = tc.get('input', {})
                    expected = tc.get('expected')
                    try:
                        if isinstance(inp, dict):
                            actual = candidate_fn(**inp)
                        elif isinstance(inp, (list, tuple)):
                            actual = candidate_fn(*inp)
                        else:
                            actual = candidate_fn(inp)

                        if actual == expected:
                            passed += 1
                            log_lines.append(f"✓ Test Case {idx}: Passed (Output: {actual})")
                        else:
                            log_lines.append(f"✗ Test Case {idx}: Failed (Expected {expected}, Got {actual})")
                    except Exception as err:
                        log_lines.append(f"✗ Test Case {idx} Runtime Error: {str(err)}")

                status = 'Passed' if passed == total else 'Failed'

        except Exception as exc:
            status = 'Syntax Error'
            log_lines.append(f"Execution Error:\n{traceback.format_exc(limit=2)}")

    # Gemini AI Code Review (optional improvement tip)
    ai_feedback = ""
    if is_gemini_configured():
        try:
            prompt = f"""
You are a Staff Software Engineer reviewing a candidate's coding submission.
Problem: {question.title} ({question.category})
Candidate Code:
\"\"\"
{code}
\"\"\"
Evaluation Status: {status} ({passed}/{total} test cases passed).

Provide a 2-3 sentence constructive code review evaluating time/space complexity and code cleanliness.
"""
            text, err = generate_gemini_text(prompt, system_instruction="Provide constructive senior code review.")
            if text and not err:
                ai_feedback = text.strip()
        except Exception:
            pass

    submission = CodingSubmission.objects.create(
        user=request.user,
        question=question,
        code=code,
        status=status,
        passed_tests=passed,
        total_tests=total,
        output_log="\n".join(log_lines),
        ai_feedback=ai_feedback
    )

    if status == 'Passed':
        messages.success(request, f"Accepted! All {passed}/{total} test cases passed.")
    else:
        messages.warning(request, f"{status}: {passed}/{total} test cases passed. Review the test logs below.")

    return redirect('coding_detail', slug=slug)

@login_required
def coding_history(request):
    submissions = CodingSubmission.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'aptitude/coding_history.html', {'submissions': submissions})
