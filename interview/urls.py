from django.urls import path
from . import views, api_views

urlpatterns = [
    # Mock Interview System
    path('', views.interview_home, name='interview_home'),
    path('start/', views.start_interview, name='start_interview'),
    path('active/<int:session_id>/<int:q_index>/', views.active_question, name='active_question'),
    path('active_compat/<int:session_id>/<int:q_index>/', views.active_question, name='active_interview'),
    path('submit/<int:session_id>/<int:q_index>/', views.submit_answer, name='submit_answer'),
    path('try_again/<int:session_id>/<int:q_index>/', views.try_again, name='try_again'),
    path('bookmark/<int:session_id>/<int:q_index>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('feedback/<int:session_id>/<int:q_index>/', views.answer_feedback, name='answer_feedback'),
    path('section_summary/<int:session_id>/', views.section_summary, name='section_summary'),
    path('result/<int:session_id>/', views.interview_report, name='interview_report'),
    path('report/<int:session_id>/', views.interview_report, name='interview_report_compat'),
    path('revision/<int:session_id>/', views.start_revision, name='start_revision'),
    path('history/', views.interview_history, name='interview_history'),

    # Group Discussion (GD) Practice Module
    path('gd/', views.gd_home, name='gd_home'),
    path('gd/generate/', views.gd_generate_new, name='gd_generate_new'),
    path('gd/<int:topic_id>/', views.gd_detail, name='gd_detail'),
    path('gd/<int:topic_id>/submit/', views.gd_submit, name='gd_submit'),
    path('gd/result/<int:session_id>/', views.gd_result, name='gd_result'),

    # REST API Endpoints
    path('api/interview/setup', api_views.api_interview_setup),
    path('api/interview/history', api_views.api_interview_history),
    path('api/interview/start', api_views.api_interview_start),
    path('api/interview/reply', api_views.api_interview_reply),
    path('api/interview/end', api_views.api_interview_end),
]
