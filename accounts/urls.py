from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.change_password_view, name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # AI Learning Assistant / Chatbot
    path('assistant/', views.assistant_view, name='ai_assistant'),
    path('assistant/send/', views.api_assistant_send, name='api_assistant_send'),
    path('assistant/clear/', views.api_assistant_clear, name='api_assistant_clear'),

    # Job Recommendations & Roadmaps
    path('recommendations/', views.job_recommendations_view, name='job_recommendations'),

    # Admin / System Gemini API Health Check
    path('gemini-diagnostics/', views.gemini_health_view, name='gemini_health_diagnostics'),

    # REST API endpoints for React Frontend
    path('api/auth/login', api_views.api_login),
    path('api/auth/register/send-otp', api_views.api_send_register_otp),
    path('api/auth/register', api_views.api_register),
    path('api/auth/forgot-password/send-otp', api_views.api_send_forgot_otp),
    path('api/auth/forgot-password/reset', api_views.api_reset_password),
    path('api/auth/logout', api_views.api_logout),
]
