from django.urls import path
from . import views, api_views

urlpatterns = [
    path('generate/', views.generate_feedback_view, name='generate_feedback'),
    path('detail/<int:feedback_id>/', views.view_feedback_view, name='view_feedback'),
    path('history/', views.feedback_history_view, name='feedback_history'),

    # REST API endpoints for React Frontend
    path('api/feedback', api_views.api_feedback_list_or_generate),
    path('api/feedback/generate', api_views.api_feedback_list_or_generate),
    path('api/feedback/<int:pk>', api_views.api_feedback_detail),
]
