"""
CareerAI URL Configuration
--------------------------
Main URL routing for all application modules.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """
    Unified health-check endpoint:
    - Returns JSON for API clients, curl, and automated monitoring probes.
    - Renders the interactive Gemini Telemetry Dashboard for browser users.
    """
    if 'text/html' in request.headers.get('Accept', '') and request.GET.get('format') != 'json':
        from accounts.views import gemini_health_view
        return gemini_health_view(request)

    from careerai.gemini_service import check_gemini_health
    health = check_gemini_health()
    return JsonResponse({
        'status': 'ok',
        'service': 'CareerAI',
        'gemini': health
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health-check/', health_check, name='health_check'),
    path('gemini-health/', health_check, name='gemini_health'),
    path('', include('accounts.urls')),
    path('aptitude/', include('aptitude.urls')),
    path('resumes/', include('resumes.urls')),
    path('interview/', include('interview.urls')),
    path('feedback/', include('feedback.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
