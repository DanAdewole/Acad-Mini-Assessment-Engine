from rest_framework import status

from .responses import StandardResponse


class StandardResponseMixin:
    """
    Mixin to use standardized responses in views.

    Provides helper methods for consistent API responses.
    """

    def success_response(
        self, data=None, message="Success", status_code=status.HTTP_200_OK
    ):
        """Return a standardized success response."""
        return StandardResponse.success(
            data=data, message=message, status_code=status_code
        )

    def error_response(
        self,
        errors=None,
        message="An error occurred",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        """Return a standardized error response."""
        return StandardResponse.error(
            errors=errors, message=message, status_code=status_code
        )

    def created_response(self, data=None, message="Resource created successfully"):
        """Return a standardized creation response."""
        return StandardResponse.created(data=data, message=message)


class QueryOptimizationMixin:
    """
    Mixin to optimize database queries.

    Automatically applies select_related and prefetch_related
    based on defined attributes.
    """

    select_related_fields = []  # Override in view
    prefetch_related_fields = []  # Override in view

    def get_queryset(self):
        """Get optimized queryset with related fields."""
        queryset = super().get_queryset()

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset


class UserFilterMixin:
    """
    Mixin to filter queryset by current user.

    Automatically filters queryset to show only the current user's data.
    Useful for submissions, answers, etc.
    """

    user_field = "user"  # Override if using different field name

    def get_queryset(self):
        """Filter queryset by current user."""
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # Admins and instructors can see all
            if self.request.user.role in ["admin", "instructor"]:
                return queryset
            # Students see only their own data
            filter_kwargs = {self.user_field: self.request.user}
            return queryset.filter(**filter_kwargs)
        return queryset.none()


class TimestampMixin:
    """
    Mixin to add timestamp information to serialized data.

    Adds created_at and updated_at to readonly fields.
    """

    def get_serializer_class(self):
        """Get serializer with timestamp fields as readonly."""
        serializer_class = super().get_serializer_class()
        if hasattr(serializer_class, "Meta"):
            if not hasattr(serializer_class.Meta, "read_only_fields"):
                serializer_class.Meta.read_only_fields = []
            serializer_class.Meta.read_only_fields = list(
                serializer_class.Meta.read_only_fields
            ) + ["created_at", "updated_at"]
        return serializer_class
