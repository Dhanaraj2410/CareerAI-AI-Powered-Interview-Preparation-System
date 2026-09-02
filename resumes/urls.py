from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.resume_home, name='resume_home'),
    path('builder/', views.resume_builder, name='resume_builder'),
    path('builder/<int:pk>/', views.resume_builder, name='resume_edit'),
    path('preview/<int:pk>/', views.resume_preview, name='resume_preview'),
    path('analyzer/', views.resume_analyzer, name='resume_analyzer'),

    # REST API endpoints for React Frontend
    path('api/resume', api_views.api_resume_list),
    path('api/resume/analyze', api_views.api_resume_analyze),
    path('api/resume/<int:pk>', api_views.api_resume_detail),
    path('api/resume/<int:pk>/duplicate', api_views.api_resume_duplicate),
]
