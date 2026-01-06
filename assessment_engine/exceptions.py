from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized error responses.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "message": get_error_message(exc),
            "errors": (
                response.data
                if isinstance(response.data, dict)
                else {"detail": response.data}
            ),
        }
        response.data = error_data

    return response


def get_error_message(exc):
    """
    Extract a user-friendly error message from the exception.
    """
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, dict):
            # Return first error message if dict
            return next(iter(exc.detail.values()))[0] if exc.detail else str(exc)
        elif isinstance(exc.detail, list):
            # Return first error if list
            return exc.detail[0] if exc.detail else str(exc)
        return str(exc.detail)
    return str(exc)
