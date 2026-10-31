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
    return JsonResponse({'status': 'ok', 'service': 'CareerAI'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health-check/', health_check, name='health_check'),
    path('', include('accounts.urls')),
    path('aptitude/', include('aptitude.urls')),
    path('resumes/', include('resumes.urls')),
    path('interview/', include('interview.urls')),
    path('feedback/', include('feedback.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
