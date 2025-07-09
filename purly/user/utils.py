def get_ip_address(request):
    remote_addr = request.META.get("REMOTE_ADDR")

    return remote_addr if remote_addr else None


def get_user_agent(request):
    http_user_agent = request.META.get("HTTP_USER_AGENT")

    return http_user_agent if http_user_agent else None
