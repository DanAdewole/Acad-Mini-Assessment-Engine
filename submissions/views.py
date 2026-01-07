from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from assessment_engine.base_views import BaseModelViewSet
from assessment_engine.permissions import (
    CanSubmitExam,
    IsAdmin,
    IsInstructorOrAdmin,
    IsStudentOwner,
)

from .models import Submission
from .serializers import (
    SubmissionCreateSerializer,
    SubmissionListSerializer,
    SubmissionSerializer,
)
from .utils import get_grading_service


@extend_schema_view(
    list=extend_schema(
        summary="List all submissions",
        description="Retrieve a list of submissions. Students see only their own.",
        tags=["Submissions"],
    ),
    retrieve=extend_schema(
        summary="Get submission details",
        description="Retrieve detailed information about a specific submission including all answers and grading feedback.",
        tags=["Submissions"],
    ),
    create=extend_schema(
        summary="Submit exam answers",
        description="Submit answers for an exam. Automatically grades the submission.",
        tags=["Submissions"],
        examples=[
            OpenApiExample(
                "Submit Exam Example",
                value={
                    "exam_id": 1,
                    "answers": [
                        {
                            "question": 1,
                            "answer_text": "Paris is the capital of France",
                        },
                        {"question": 2, "answer_data": {"selected": "B"}},
                        {"question": 3, "answer_text": "Photosynthesis..."},
                    ],
                    "metadata": {"browser": "Chrome", "ip_address": "192.168.1.1"},
                },
                request_only=True,
            )
        ],
    ),
)
class SubmissionViewSet(BaseModelViewSet):
    """
    ViewSet for managing exam submissions.
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["exam", "status", "user"]
    search_fields = ["user__email", "exam__title"]
    ordering_fields = ["submitted_at", "graded_at", "total_score", "created_at"]
    ordering = ["-submitted_at"]

    # Query optimization
    select_related_fields = ["user", "exam", "exam__course"]
    prefetch_related_fields = ["answers", "answers__question"]

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == "create":
            return SubmissionCreateSerializer
        elif self.action == "list":
            return SubmissionListSerializer
        return SubmissionSerializer

    def get_queryset(self):
        """
        Filter submissions based on user role.
        """
        queryset = super().get_queryset()

        # Students see only their own submissions
        if self.request.user.is_student:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action == "create":
            permission_classes = [IsAuthenticated, CanSubmitExam]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated, IsStudentOwner]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Only admins can update or delete submissions
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a submission and automatically grade it.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()
        submission = result["submission"]

        # Get all answers for grading
        answers = submission.answers.select_related("question").all()

        # Grade the submission using configured grading service
        grading_service = get_grading_service()

        try:
            grading_result = grading_service.grade_submission(submission, answers)

            # Update submission with grading results
            submission.total_score = grading_result["total_score"]
            submission.max_score = grading_result["max_score"]
            submission.status = Submission.Status.GRADED
            submission.graded_at = timezone.now()
            submission.save()

        except Exception as e:
            # If grading fails, mark as submitted but not graded
            submission.status = Submission.Status.SUBMITTED
            submission.save()
            print(f"Grading error: {e}")

        # Return the graded submission
        response_serializer = SubmissionSerializer(submission)
        return self.created_response(
            data=response_serializer.data,
            message="Submission created and graded successfully",
        )

    @extend_schema(
        summary="Get my submissions",
        description="Retrieve all submissions for the authenticated user.",
        tags=["Submissions"],
    )
    @action(detail=False, methods=["get"])
    def my_submissions(self, request):
        """Get submissions for the authenticated user."""
        queryset = (
            self.get_queryset()
            .filter(user=request.user)
            .select_related("exam", "exam__course")
            .prefetch_related("answers")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubmissionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubmissionListSerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data, message="User submissions retrieved successfully"
        )

    @extend_schema(
        summary="Get submissions for an exam",
        description="Retrieve all submissions for a specific exam. Requires instructor/admin permissions.",
        tags=["Submissions"],
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsInstructorOrAdmin],
        url_path="exam/(?P<exam_id>[^/.]+)",
    )
    def by_exam(self, request, exam_id=None):
        """Get all submissions for a specific exam."""
        queryset = (
            self.get_queryset()
            .filter(exam_id=exam_id)
            .select_related("user", "exam")
            .prefetch_related("answers")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubmissionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubmissionListSerializer(queryset, many=True)
        return self.success_response(
            data=serializer.data, message="Exam submissions retrieved successfully"
        )

    @extend_schema(
        summary="Get submission statistics",
        description="Get statistics for a submission (score, percentage, pass/fail).",
        tags=["Submissions"],
    )
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request, pk=None):
        """Get statistics for a submission."""
        submission = self.get_object()

        # Check permission
        if (
            not request.user.is_instructor
            and not request.user.is_admin_user
            and submission.user != request.user
        ):
            return self.error_response(
                message="You do not have permission to view this submission.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        stats = {
            "submission_id": submission.id,
            "exam_title": submission.exam.title,
            "student_email": submission.user.email,
            "total_score": submission.total_score,
            "max_score": submission.max_score,
            "percentage_score": submission.percentage_score,
            "is_passed": submission.is_passed,
            "status": submission.status,
            "submitted_at": submission.submitted_at,
            "graded_at": submission.graded_at,
            "total_questions": submission.answers.count(),
            "correct_answers": (
                submission.answers.filter(
                    score__gte=0.9 * submission.answers.first().max_score
                ).count()
                if submission.answers.exists()
                else 0
            ),
        }

        return self.success_response(
            data=stats, message="Submission statistics retrieved successfully"
        )

    @extend_schema(
        summary="Regrade a submission",
        description="Regrade an existing submission. Requires instructor/admin permissions.",
        tags=["Submissions"],
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsInstructorOrAdmin],
    )
    def regrade(self, request, pk=None):
        """Regrade a submission."""
        submission = self.get_object()

        # Get all answers for grading
        answers = submission.answers.select_related("question").all()

        # Grade the submission using configured grading service
        grading_service = get_grading_service()

        try:
            grading_result = grading_service.grade_submission(submission, answers)

            # Update submission with new grading results
            submission.total_score = grading_result["total_score"]
            submission.max_score = grading_result["max_score"]
            submission.status = Submission.Status.GRADED
            submission.graded_at = timezone.now()
            submission.save()

            serializer = self.get_serializer(submission)
            return self.success_response(
                data=serializer.data, message="Submission regraded successfully"
            )

        except Exception as e:
            return self.error_response(
                message=f"Regrading failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
