class ShowCsrfTokenMiddleware:
    """
    Shows CSRF token to browser when logging in, allowing browser to set
    it locally & view through JS. Not a CSRF risk because if another
    site can make a request to the login endpoint, they already have
    your credentials.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if 'X-Show-CSRFToken' in response.headers:
            response.headers['X-Csrftoken'] = request.META['CSRF_COOKIE']

        return response
