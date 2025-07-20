from django.http import Http404
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotAcceptable,
    NotFound,
    UnsupportedMediaType,
)
from rest_framework.views import exception_handler


def client_error(exc, context, response):
    if isinstance(exc, MethodNotAllowed):
        method = context.get("request").method
        detail = f"Method '{method}' not allowed."
    elif isinstance(exc, UnsupportedMediaType):
        media_type = context.get("request").content_type
        detail = f"Unsupported media type '{media_type}' in request."
    elif isinstance(exc, NotAcceptable):
        detail = "Could not satisfy the request accept header."
    else:
        detail = exc.detail

    response.data = {
        "type": "client_error",
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
                            errors.append(  # noqa: PERF401
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
                        errors.append(  # noqa: PERF401
                            {
                                "attr": field,
                                "code": item.get("code"),
                                "detail": item.get("message"),
                            }
                        )

    response.data = {
        "type": "validation_error",
        "errors": errors,
    }

    return response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    if isinstance(exc, Http404):
        exc = NotFound(detail=str(exc) or None)

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

    response.data = {  # type: ignore
        "type": None,
        "errors": [{"attr": None, "code": None, "detail": exc.detail}],
    }

    return response
