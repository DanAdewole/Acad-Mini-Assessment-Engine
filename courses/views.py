from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from assessment_engine.base_views import BaseModelViewSet
from assessment_engine.permissions import IsAdmin, IsInstructorOrAdmin

from .models import Course
from .serializers import CourseListSerializer, CourseSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all courses",
        description="Retrieve a list of all courses. Students see only active courses.",
        tags=["Courses"],
    ),
    retrieve=extend_schema(
        summary="Get course details",
        description="Retrieve detailed information about a specific course.",
        tags=["Courses"],
    ),
    create=extend_schema(
        summary="Create a new course",
        description="Create a new course. Requires admin or instructor permissions.",
        tags=["Courses"],
        examples=[
            OpenApiExample(
                "Create Course Example",
                value={
                    "code": "CS101",
                    "title": "Introduction to Computer Science",
                    "description": "Learn the fundamentals of computer science",
                    "is_active": True,
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Update a course",
        description="Update an existing course. Requires admin or instructor permissions.",
        tags=["Courses"],
    ),
    partial_update=extend_schema(
        summary="Partially update a course",
        description="Partially update an existing course. Requires admin or instructor permissions.",
        tags=["Courses"],
    ),
    destroy=extend_schema(
        summary="Delete a course",
        description="Delete a course. Requires admin permissions.",
        tags=["Courses"],
    ),
)
class CourseViewSet(BaseModelViewSet):
    """
    ViewSet for managing courses.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active", "code"]
    search_fields = ["code", "title", "description"]
    ordering_fields = ["title", "code", "created_at"]
    ordering = ["title"]

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def get_queryset(self):
        """
        Filter courses based on user role.
        """
        queryset = Course.objects.all()

        # Add optimizations
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        # Additional prefetch for retrieve action
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("exams")

        # Filter for students - only show active courses
        if self.request.user.is_student:
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Get active courses",
        description="Retrieve only active courses.",
        tags=["Courses"],
    )
    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active courses."""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data, message="Active courses retrieved successfully"
        )

    @extend_schema(
        summary="Get course statistics",
        description="Get statistics for a specific course (exam count, etc.).",
        tags=["Courses"],
    )
    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get course statistics."""
        course = self.get_object()

        stats = {
            "course_id": course.id,
            "course_code": course.code,
            "course_title": course.title,
            "total_exams": course.exams.count(),
            "published_exams": course.exams.filter(is_published=True).count(),
            "active_exams": course.exams.filter(
                is_published=True,
                start_time__lte=request.user.date_joined,
                end_time__gte=request.user.date_joined,
            ).count(),
        }

        return self.success_response(
            data=stats, message="Course statistics retrieved successfully"
        )
