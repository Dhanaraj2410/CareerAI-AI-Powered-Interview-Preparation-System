from django.urls import path
from . import views, api_views

urlpatterns = [
    # Aptitude Tests
    path('', views.aptitude_home, name='aptitude_home'),
    path('test/<str:difficulty>/', views.aptitude_test, name='aptitude_test'),
    path('submit/', views.aptitude_submit, name='aptitude_submit'),
    path('result/<int:result_id>/', views.aptitude_result, name='aptitude_result'),
    path('retry/<int:result_id>/', views.aptitude_retry_wrong, name='aptitude_retry_wrong'),

    # Coding Practice Challenges (Python, SQL, DSA)
    path('coding/', views.coding_home, name='coding_home'),
    path('coding/history/', views.coding_history, name='coding_history'),
    path('coding/<slug:slug>/', views.coding_detail, name='coding_detail'),
    path('coding/<slug:slug>/submit/', views.coding_submit, name='coding_submit'),

    # REST API endpoints for React Frontend
    path('api/aptitude/submit', api_views.api_submit_aptitude),
    path('api/aptitude/<str:difficulty>', api_views.api_get_questions),
]
