from django.http import Http404, JsonResponse
from django.template.response import TemplateResponse
from rest_framework import exceptions, status, views


def client_error(exc, context, response):
    if isinstance(exc, exceptions.MethodNotAllowed):
        method = context.get("request").method
        detail = f"This method is not allowed: {method}"
    elif isinstance(exc, exceptions.UnsupportedMediaType):
        media_type = context.get("request").content_type
        detail = f"This is an unsupported media type: {media_type}"
    elif isinstance(exc, exceptions.NotAcceptable):
        detail = "Could not satisfy the request accept header."
    else:
        detail = exc.detail

    response.data = {
        "type": "client_error",
        "request_id": context.get("request").META.get("X_REQUEST_UUID", ""),
        "errors": [{"attr": None, "code": exc.get_codes(), "detail": detail}],
    }

    return response


def validation_error(exc, context, response):  # noqa: C901
    errors = []

    full_details = exc.get_full_details()

    for field, detail in full_details.items():
        if isinstance(detail, list):
            for item in detail:
                if item.get("message") is not None:
                    errors.append(
                        {"attr": field, "code": item.get("code"), "detail": item.get("message")}
                    )
                else:
                    for nested_field, nested_detail in item.items():
                        for nested_item in nested_detail:
                            errors.append(
                                {
                                    "attr": f"{field}.{nested_field}",
                                    "code": nested_item.get("code"),
                                    "detail": nested_item.get("message"),
                                }
                            )
        elif isinstance(detail, dict):
            for nested_detail in detail.values():
                for item in nested_detail:
                    if item.get("message") is not None:
                        errors.append(
                            {
                                "attr": field,
                                "code": item.get("code"),
                                "detail": item.get("message"),
                            }
                        )

    response.data = {
        "request_id": context.get("request").META.get("X_REQUEST_UUID", ""),
        "type": "validation_error",
        "errors": errors,
    }

    return response


def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound(detail=str(exc) or None)

    response = views.exception_handler(exc, context)

    handlers = {
        "ParseError": client_error,
        "AuthenticationFailed": client_error,
        "NotAuthenticated": client_error,
        "PermissionDenied": client_error,
        "NotFound": client_error,
        "MethodNotAllowed": client_error,
        "NotAcceptable": client_error,
        "UnsupportedMediaType": client_error,
        "Throttled": client_error,
        "ValidationError": validation_error,
    }

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    return response


def page_not_found(request, *args, **kwargs):
    data = {"request_id": request.META.get("X_REQUEST_UUID", "")}

    if request.path.startswith("/api/"):
        response = {
            "type": "client_error",
            "request_id": data["request_id"],
            "errors": [
                {
                    "attr": None,
                    "code": "not_found",
                    "detail": "This API endpoint does not exist.",
                }
            ],
        }

        return JsonResponse(response, status=status.HTTP_404_NOT_FOUND)

    return TemplateResponse(request, "404.html", context=data, status=404)


def server_error(request, *args, **kwargs):
    data = {"request_id": request.META.get("X_REQUEST_UUID", "")}

    if request.path.startswith("/api/"):
        response = {
            "type": "server_error",
            "request_id": data["request_id"],
            "errors": [
                {
                    "attr": None,
                    "code": "internal_error",
                    "detail": "An internal server error occurred.",
                }
            ],
        }

        return JsonResponse(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return TemplateResponse(request, "500.html", context=data, status=500)
