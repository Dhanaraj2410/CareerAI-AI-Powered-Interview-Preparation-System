"""Derived progress metrics shared by the dashboard and feedback flows."""

from datetime import timedelta

from django.utils import timezone

from aptitude.models import AptitudeResult, CodingSubmission
from interview.models import GDSession, InterviewSession
from resumes.models import UploadedResume


def latest_scores(user):
    """Return the latest real score for each practice dimension.

    ``None`` means that the candidate has not completed that activity yet.
    Keeping that distinction prevents the UI from presenting placeholder scores
    as if they were measured performance.
    """
    aptitude = AptitudeResult.objects.filter(user=user).order_by('-created_at').first()
    resume = UploadedResume.objects.filter(user=user).order_by('-uploaded_at').first()
    interview = InterviewSession.objects.filter(user=user, completed=True).order_by('-created_at').first()

    return {
        'aptitude': round(aptitude.percentage, 1) if aptitude else None,
        'resume': round(resume.resume_score, 1) if resume else None,
        'technical': round(interview.total_score, 1) if interview else None,
        'communication': round(interview.avg_confidence, 1) if interview else None,
    }


def _activity_dates(user):
    """Return activity counts for today and the six preceding calendar days."""
    today = timezone.localdate()
    dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    start = dates[0]

    activity_dates = {
        'aptitude': AptitudeResult.objects.filter(user=user, created_at__date__gte=start)
        .values_list('created_at', flat=True),
        'coding': CodingSubmission.objects.filter(user=user, created_at__date__gte=start)
        .values_list('created_at', flat=True),
        'interviews': InterviewSession.objects.filter(user=user, created_at__date__gte=start)
        .values_list('created_at', flat=True),
        'gd': GDSession.objects.filter(user=user, created_at__date__gte=start)
        .values_list('created_at', flat=True),
        'resumes': UploadedResume.objects.filter(user=user, uploaded_at__date__gte=start)
        .values_list('uploaded_at', flat=True),
    }

    counts = {date: 0 for date in dates}
    for timestamps in activity_dates.values():
        for timestamp in timestamps:
            activity_date = timezone.localdate(timestamp)
            if activity_date in counts:
                counts[activity_date] += 1

    return [
        {
            'date': date.isoformat(),
            'label': date.strftime('%a'),
            'count': counts[date],
        }
        for date in dates
    ]


def progress_snapshot(user):
    """Build the user-facing progress payload used by HTML and JSON clients."""
    scores = latest_scores(user)
    measured_scores = [value for value in scores.values() if value is not None]
    overall = round(sum(measured_scores) / len(measured_scores), 1) if measured_scores else None
    activity = _activity_dates(user)
    streak = 0
    for day in reversed(activity):
        if day['count'] == 0:
            break
        streak += 1

    if scores['aptitude'] is None:
        next_action = {'label': 'Take an aptitude assessment', 'url_name': 'aptitude_home', 'reason': 'Build your first measurable baseline.'}
    elif scores['resume'] is None:
        next_action = {'label': 'Upload your resume', 'url_name': 'resume_analyzer', 'reason': 'Get an ATS score and skill-gap analysis.'}
    elif scores['technical'] is None:
        next_action = {'label': 'Complete a mock interview', 'url_name': 'interview_home', 'reason': 'Measure technical depth and communication.'}
    elif scores['communication'] is not None and scores['communication'] < 60:
        next_action = {'label': 'Practice a group discussion', 'url_name': 'gd_home', 'reason': 'Strengthen clarity and structured communication.'}
    else:
        weakest = min(((value, name) for name, value in scores.items() if value is not None), default=(None, 'aptitude'))
        labels = {'aptitude': 'aptitude', 'resume': 'resume', 'technical': 'technical', 'communication': 'communication'}
        next_action = {'label': f"Improve your {labels[weakest[1]]} score", 'url_name': 'job_recommendations', 'reason': 'Review your targeted roadmap and keep progressing.'}

    return {
        'scores': scores,
        'overall': overall,
        'activity': activity,
        'streak': streak,
        'active_days': sum(1 for day in activity if day['count']),
        'next_action': next_action,
    }
