from rest_framework import status
from rest_framework.response import Response


class StandardResponse:
    """
    Standardized API response format.

    All API responses follow this structure for consistency:
    {
        "success": true/false,
        "message": "Description",
        "data": {...},
        "errors": {...}
    }
    """

    @staticmethod
    def success(
        data=None, message="Success", status_code=status.HTTP_200_OK, extra_fields=None
    ):
        """
        Return a successful response.
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data,
        }

        if extra_fields:
            response_data.update(extra_fields)

        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        errors=None,
        message="An error occurred",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        """
        Return an error response.
        """
        response_data = {
            "success": False,
            "message": message,
            "errors": errors,
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def created(data=None, message="Resource created successfully"):
        """
        Return a creation success response.
        """
        return StandardResponse.success(
            data=data, message=message, status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def no_content(message="Operation successful"):
        """
        Return a no content response.
        """
        return StandardResponse.success(
            message=message, status_code=status.HTTP_204_NO_CONTENT
        )

    @staticmethod
    def unauthorized(message="Authentication required"):
        """
        Return an unauthorized response.
        """
        return StandardResponse.error(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(message="Permission denied"):
        """
        Return a forbidden response.
        """
        return StandardResponse.error(
            message=message, status_code=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def not_found(message="Resource not found"):
        """
        Return a not found response.
        """
        return StandardResponse.error(
            message=message, status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def validation_error(errors, message="Validation failed"):
        """
        Return a validation error response.
        """
        return StandardResponse.error(
            errors=errors, message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


def paginated_response(
    queryset, serializer_class, request, message="Data retrieved successfully"
):
    """
    Create a paginated response with standard format.
    """
    from rest_framework.pagination import PageNumberPagination

    paginator = PageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(
        paginated_queryset, many=True, context={"request": request}
    )

    return Response(
        {
            "success": True,
            "message": message,
            "data": {
                "results": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
        },
        status=status.HTTP_200_OK,
    )
