from rest_framework import status, viewsets

from .mixins import (
    QueryOptimizationMixin,
    StandardResponseMixin,
    UserFilterMixin,
)


class BaseModelViewSet(
    StandardResponseMixin,
    QueryOptimizationMixin,
    UserFilterMixin,
    viewsets.ModelViewSet,
):
    """
    Base ViewSet with all common functionality.
    """

    auto_wrap_responses = True

    def list(self, request, *args, **kwargs):
        """List all objects with standardized response."""
        if not self.auto_wrap_responses:
            return super().list(request, *args, **kwargs)

        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)

                return self.success_response(
                    data=paginated_response.data.get("results", paginated_response.data),
                    message="Data retrieved successfully" if paginated_response.data.get("results") else "List empty",
                    extra_fields={k: v for k, v in paginated_response.data.items() if k != "results"}
                )

            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Data retrieved successfully" if serializer.data else "List empty",
            )
        except Exception as e:
            return self.error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        """Create object with standardized response."""
        if not self.auto_wrap_responses:
            return super().create(request, *args, **kwargs)

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return self.created_response(
                data=serializer.data, message="Resource created successfully"
            )
        except Exception as e:
            return self.error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single object with standardized response."""
        if not self.auto_wrap_responses:
            return super().retrieve(request, *args, **kwargs)

        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data, message="Data retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=str(e), status_code=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        """Update object with standardized response."""
        if not self.auto_wrap_responses:
            return super().update(request, *args, **kwargs)

        try:
            partial = kwargs.pop("partial", True)  # Default to PATCH behavior
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return self.success_response(
                data=serializer.data, message="Resource updated successfully"
            )
        except Exception as e:
            return self.error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        """Partial update (PATCH) with standardized response."""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete object with standardized response."""
        if not self.auto_wrap_responses:
            return super().destroy(request, *args, **kwargs)

        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return self.success_response(
                data=None, message="Resource deleted successfully"
            )
        except Exception as e:
            error_msg = str(e)

            # Handle protected foreign key errors
            if "protected" in error_msg.lower():
                error_msg = "This record cannot be deleted because it is referenced by other records"

            return self.error_response(
                message=error_msg, status_code=status.HTTP_400_BAD_REQUEST
            )


class ReadOnlyBaseViewSet(
    StandardResponseMixin, QueryOptimizationMixin, viewsets.ReadOnlyModelViewSet
):
    """
    Base ViewSet for read-only endpoints.
    """

    auto_wrap_responses = True

    def list(self, request, *args, **kwargs):
        """List all objects."""
        if not self.auto_wrap_responses:
            return super().list(request, *args, **kwargs)

        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data, message="Data retrieved successfully"
            )
        except Exception as e:
            return self.error_response(message=str(e))

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single object."""
        if not self.auto_wrap_responses:
            return super().retrieve(request, *args, **kwargs)

        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data, message="Data retrieved successfully"
            )
        except Exception as e:
            return self.error_response(
                message=str(e), status_code=status.HTTP_404_NOT_FOUND
            )
