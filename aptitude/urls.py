from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.aptitude_home, name='aptitude_home'),
    path('test/<str:difficulty>/', views.aptitude_test, name='aptitude_test'),
    path('submit/', views.aptitude_submit, name='aptitude_submit'),
    path('result/<int:result_id>/', views.aptitude_result, name='aptitude_result'),
    path('retry/<int:result_id>/', views.aptitude_retry_wrong, name='aptitude_retry_wrong'),

    # REST API endpoints for React Frontend
    path('api/aptitude/submit', api_views.api_submit_aptitude),
    path('api/aptitude/<str:difficulty>', api_views.api_get_questions),
]
