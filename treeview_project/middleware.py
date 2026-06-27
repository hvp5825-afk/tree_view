from django.utils.cache import add_never_cache_headers


class NoCacheMiddleware:
    """Prevent browser caching for ALL pages.
    Disables back-forward cache (bfcache) to prevent stale CSRF tokens
    and stale session state when using browser back/forward buttons."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        add_never_cache_headers(response)
        response['Vary'] = 'Cookie'
        return response
