from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from assessment_engine.base_views import BaseModelViewSet
from assessment_engine.permissions import IsAdmin, IsInstructorOrAdmin

from .models import Exam, Question
from .serializers import (
    ExamDetailSerializer,
    ExamListSerializer,
    ExamSerializer,
    QuestionListSerializer,
    QuestionSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all exams",
        description="Retrieve a list of all exams. Students see only published exams.",
        tags=["Exams"],
    ),
    retrieve=extend_schema(
        summary="Get exam details",
        description="Retrieve detailed information about a specific exam including questions.",
        tags=["Exams"],
    ),
    create=extend_schema(
        summary="Create a new exam",
        description="Create a new exam. Requires admin or instructor permissions.",
        tags=["Exams"],
        examples=[
            OpenApiExample(
                "Create Exam Example",
                value={
                    "course": 1,
                    "title": "Midterm Exam",
                    "description": "Covers chapters 1-5",
                    "duration_minutes": 90,
                    "start_time": "2026-01-08T09:00:00Z",
                    "end_time": "2026-01-08T12:00:00Z",
                    "is_published": False,
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Update an exam",
        description="Update an existing exam. Requires admin or instructor permissions.",
        tags=["Exams"],
    ),
    partial_update=extend_schema(
        summary="Partially update an exam",
        description="Partially update an existing exam. Requires admin or instructor permissions.",
        tags=["Exams"],
    ),
    destroy=extend_schema(
        summary="Delete an exam",
        description="Delete an exam. Requires admin permissions.",
        tags=["Exams"],
    ),
)
class ExamViewSet(BaseModelViewSet):
    """
    ViewSet for managing exams.
    """

    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "is_published"]
    search_fields = ["title", "description", "course__title", "course__code"]
    ordering_fields = ["start_time", "end_time", "created_at"]
    ordering = ["-start_time"]

    # Query optimization
    select_related_fields = ["course"]
    prefetch_related_fields = ["questions"]

    def get_serializer_class(self):
        if self.action == "list":
            return ExamListSerializer
        elif self.action == "retrieve":
            if self.request.user.is_student:
                return ExamDetailSerializer
            return ExamSerializer
        return ExamSerializer

    def get_queryset(self):
        """
        Filter exams based on user role.
        """
        queryset = Exam.objects.all()

        # Add optimizations
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        # Filter for students - only show published exams
        if self.request.user.is_student:
            queryset = queryset.filter(is_published=True)

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
        summary="Get active exams",
        description="Retrieve only currently active exams (within start and end time).",
        tags=["Exams"],
    )
    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get currently active exams."""
        now = timezone.now()
        queryset = (
            self.get_queryset()
            .filter(is_published=True, start_time__lte=now, end_time__gte=now)
            .select_related("course")
        )

        serializer = ExamListSerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data, message="Active exams retrieved successfully"
        )

    @extend_schema(
        summary="Get upcoming exams",
        description="Retrieve upcoming exams that haven't started yet.",
        tags=["Exams"],
    )
    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming exams."""
        now = timezone.now()
        queryset = (
            self.get_queryset()
            .filter(is_published=True, start_time__gt=now)
            .select_related("course")
            .order_by("start_time")
        )

        serializer = ExamListSerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data, message="Upcoming exams retrieved successfully"
        )

    @extend_schema(
        summary="Publish an exam",
        description="Publish an exam to make it visible to students. Requires instructor/admin permissions.",
        tags=["Exams"],
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsInstructorOrAdmin],
    )
    def publish(self, request, pk=None):
        """Publish an exam."""
        exam = self.get_object()
        exam.is_published = True
        exam.save()

        serializer = self.get_serializer(exam)
        return self.success_response(
            data=serializer.data, message="Exam published successfully"
        )

    @extend_schema(
        summary="Unpublish an exam",
        description="Unpublish an exam to hide it from students. Requires instructor/admin permissions.",
        tags=["Exams"],
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsInstructorOrAdmin],
    )
    def unpublish(self, request, pk=None):
        """Unpublish an exam."""
        exam = self.get_object()
        exam.is_published = False
        exam.save()

        serializer = self.get_serializer(exam)
        return self.success_response(
            data=serializer.data, message="Exam unpublished successfully"
        )


@extend_schema_view(
    list=extend_schema(
        summary="List all questions",
        description="Retrieve a list of all questions. Filter by exam.",
        tags=["Questions"],
    ),
    retrieve=extend_schema(
        summary="Get question details",
        description="Retrieve detailed information about a specific question.",
        tags=["Questions"],
    ),
    create=extend_schema(
        summary="Create a new question",
        description="Create a new question. Requires admin or instructor permissions.",
        tags=["Questions"],
        examples=[
            OpenApiExample(
                "Create Multiple Choice Question",
                value={
                    "exam": 1,
                    "question_type": "multiple_choice",
                    "question_text": "What is 2+2?",
                    "expected_answer": {"answer": "B"},
                    "options": ["A. 3", "B. 4", "C. 5", "D. 6"],
                    "points": 5,
                    "order": 1,
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Update a question",
        description="Update an existing question. Requires admin or instructor permissions.",
        tags=["Questions"],
    ),
    partial_update=extend_schema(
        summary="Partially update a question",
        description="Partially update an existing question. Requires admin or instructor permissions.",
        tags=["Questions"],
    ),
    destroy=extend_schema(
        summary="Delete a question",
        description="Delete a question. Requires admin permissions.",
        tags=["Questions"],
    ),
)
class QuestionViewSet(BaseModelViewSet):
    """
    ViewSet for managing questions.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    filterset_fields = ["exam", "question_type"]
    search_fields = ["question_text"]
    ordering_fields = ["order", "points", "created_at"]
    ordering = ["order"]

    # Query optimization
    select_related_fields = ["exam", "exam__course"]

    def get_queryset(self):
        """Get queryset with optimizations."""
        queryset = Question.objects.all()

        # Add optimizations
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == "list":
            return QuestionListSerializer
        return QuestionSerializer
