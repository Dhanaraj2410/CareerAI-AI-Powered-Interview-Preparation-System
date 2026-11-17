from django.test import RequestFactory, SimpleTestCase, override_settings

from .middleware import CorsMiddleware


class CorsMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(CORS_ALLOWED_ORIGINS=['https://app.example.com'])
    def test_unconfigured_origin_is_not_reflected(self):
        def response(_request):
            from django.http import HttpResponse
            return HttpResponse('ok')

        middleware = CorsMiddleware(response)
        request = self.factory.get('/', HTTP_ORIGIN='https://evil.example.com')
        result = middleware(request)
        self.assertNotIn('Access-Control-Allow-Origin', result)

    @override_settings(CORS_ALLOWED_ORIGINS=['https://app.example.com'])
    def test_configured_origin_is_reflected(self):
        def response(_request):
            from django.http import HttpResponse
            return HttpResponse('ok')

        middleware = CorsMiddleware(response)
        request = self.factory.get('/', HTTP_ORIGIN='https://app.example.com')
        result = middleware(request)
        self.assertEqual(result['Access-Control-Allow-Origin'], 'https://app.example.com')
