from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners to edit their objects.

    Read permissions are allowed to any request.
    Write permissions are only allowed to the owner.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access object."""
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners to access their objects.

    Both read and write permissions require ownership.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user is the owner."""
        return obj.user == request.user


class IsStudent(permissions.BasePermission):
    """Permission to only allow students."""

    def has_permission(self, request, view):
        """Check if user is a student."""
        return request.user.is_authenticated and request.user.role == "student"


class IsInstructor(permissions.BasePermission):
    """Permission to only allow instructors."""

    def has_permission(self, request, view):
        """Check if user is an instructor."""
        return request.user.is_authenticated and request.user.role == "instructor"


class IsAdmin(permissions.BasePermission):
    """Permission to only allow admins."""

    def has_permission(self, request, view):
        """Check if user is an admin."""
        return request.user.is_authenticated and request.user.role == "admin"


class IsInstructorOrAdmin(permissions.BasePermission):
    """Permission to only allow instructors or admins."""

    def has_permission(self, request, view):
        """Check if user is an instructor or admin."""
        return request.user.is_authenticated and request.user.role in [
            "instructor",
            "admin",
        ]


class IsStudentOwner(permissions.BasePermission):
    """
    Permission to allow students to access their own submissions.
    Instructors and admins can access all submissions.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user can access the submission.
        """
        # Instructors and admins can access any submission
        if request.user.role in ["instructor", "admin"]:
            return True

        # Students can only access their own submissions
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "submission"):
            return obj.submission.user == request.user
        return False


class CanSubmitExam(permissions.BasePermission):
    """
    Permission to check if user can submit an exam.
    """

    message = "You cannot submit this exam at this time."

    def has_permission(self, request, view):
        """Check if user can submit exams."""
        return request.user.is_authenticated and request.user.role == "student"

    def has_object_permission(self, request, view, obj):
        """Check if user can submit this specific exam."""
        from django.utils import timezone

        exam = obj if hasattr(obj, "title") else obj.exam

        if not exam.is_published:
            self.message = "This exam is not published yet."
            return False

        now = timezone.now()
        if now < exam.start_time:
            self.message = "This exam hasn't started yet."
            return False
        if now > exam.end_time:
            self.message = "This exam has ended."
            return False

        from submissions.models import Submission

        existing_submission = Submission.objects.filter(
            user=request.user, exam=exam
        ).exists()

        if existing_submission:
            self.message = "You have already submitted this exam."
            return False

        return True


class ReadOnly(permissions.BasePermission):
    """
    Permission to only allow read-only access.

    Useful for published exams and questions that students can view
    but not modify.
    """

    def has_permission(self, request, view):
        """Only allow safe methods."""
        return request.method in permissions.SAFE_METHODS
