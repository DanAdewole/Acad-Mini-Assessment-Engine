from rest_framework import status
from rest_framework.exceptions import APIException
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


class ExamNotAvailableException(APIException):
    """Exception raised when exam is not available for submission."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "This exam is not available for submission at this time."
    default_code = "exam_not_available"


class SubmissionAlreadyExistsException(APIException):
    """Exception raised when user tries to submit exam twice."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "You have already submitted this exam."
    default_code = "submission_exists"


class InvalidAnswerException(APIException):
    """Exception raised when answer format is invalid."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid answer format."
    default_code = "invalid_answer"


class GradingException(APIException):
    """Exception raised when grading fails."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An error occurred during grading."
    default_code = "grading_error"
