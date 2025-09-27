import uuid


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META["X_REQUEST_ID"] = str(uuid.uuid4())

        return self.get_response(request)
