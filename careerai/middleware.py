"""
CareerAI Custom Middleware
--------------------------
Provides narrowly scoped CORS handling for API endpoints.
"""

from django.conf import settings


def _cors_origin(request):
    origin = request.headers.get('Origin')
    allowed = set(getattr(settings, 'CORS_ALLOWED_ORIGINS', []))
    if origin and origin in allowed:
        return origin
    return None


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = _cors_origin(request)
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            if origin:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, X-Requested-With'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            return response

        response = self.get_response(request)
        if origin:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, X-Requested-With'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response
