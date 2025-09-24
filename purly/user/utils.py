def get_ip_address(request):
    return request.META.get("REMOTE_ADDR", None)


def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")
