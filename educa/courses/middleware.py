class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from courses.models import Module, Content
        Module._request = request
        Content._request = request
        response = self.get_response(request)
        return response