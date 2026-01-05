from django.utils import timezone
from rest_framework import serializers

from courses.serializers import CourseListSerializer

from .models import Exam, Question


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.
    """

    class Meta:
        model = Question
        fields = [
            "id",
            "exam",
            "question_type",
            "question_text",
            "expected_answer",
            "options",
            "points",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_points(self, value):
        """Validate points are positive."""
        if value <= 0:
            raise serializers.ValidationError("Points must be greater than 0")
        return value

    def validate(self, attrs):
        """Validate question based on type."""
        question_type = attrs.get("question_type")
        expected_answer = attrs.get("expected_answer")
        options = attrs.get("options", {})

        # Multiple choice must have options
        if question_type == Question.QuestionType.MULTIPLE_CHOICE:
            if not options or not isinstance(options, dict):
                raise serializers.ValidationError(
                    {"options": "Multiple choice questions must have options"}
                )
            if "choices" not in options:
                raise serializers.ValidationError(
                    {"options": "Options must contain 'choices' list"}
                )

        # True/False validation
        if question_type == Question.QuestionType.TRUE_FALSE:
            if not isinstance(expected_answer, dict) or "answer" not in expected_answer:
                raise serializers.ValidationError(
                    {"expected_answer": "True/False questions must have 'answer' in expected_answer"}
                )

        return attrs


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing questions without expected answers.
    """

    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "question_text",
            "options",
            "points",
            "order",
        ]
        read_only_fields = fields


class ExamSerializer(serializers.ModelSerializer):
    """
    Serializer for Exam model with nested questions.
    """

    course_details = CourseListSerializer(source="course", read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    questions_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "course_details",
            "title",
            "description",
            "duration_minutes",
            "metadata",
            "start_time",
            "end_time",
            "is_published",
            "is_active",
            "total_points",
            "questions_count",
            "questions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "total_points",
            "questions_count",
            "created_at",
            "updated_at",
        ]

    def get_questions_count(self, obj):
        """Get count of questions in this exam."""
        return obj.questions.count()

    def validate_duration_minutes(self, value):
        """Validate exam duration is reasonable."""
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        if value > 600:  # 10 hours max
            raise serializers.ValidationError(
                "Duration cannot exceed 600 minutes (10 hours)"
            )
        return value

    def validate(self, attrs):
        """
        Validate exam times.
        """
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        if start_time and end_time:
            # Validate start < end
            if start_time >= end_time:
                raise serializers.ValidationError(
                    {"end_time": "End time must be after start time"}
                )

            # Validate time window is reasonable (at least duration + buffer)
            duration_minutes = attrs.get("duration_minutes", 60)
            time_diff = (end_time - start_time).total_seconds() / 60

            if time_diff < duration_minutes:
                raise serializers.ValidationError(
                    {
                        "end_time": f"Time window ({time_diff:.0f} min) must be at least as long as exam duration ({duration_minutes} min)"
                    }
                )

            # Warn if start time is in the past (for creation)
            if self.instance is None and start_time < timezone.now():
                raise serializers.ValidationError(
                    {"start_time": "Start time cannot be in the past"}
                )

        return attrs


class ExamListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing exams.
    """

    course_details = CourseListSerializer(source="course", read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    questions_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "course_details",
            "title",
            "duration_minutes",
            "start_time",
            "end_time",
            "is_published",
            "is_active",
            "total_points",
            "questions_count",
        ]
        read_only_fields = fields

    def get_questions_count(self, obj):
        """Get count of questions."""
        return obj.questions.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    """
    Detailed exam serializer for students taking exams.
    Shows questions without expected answers.
    """

    course_details = CourseListSerializer(source="course", read_only=True)
    questions = QuestionListSerializer(many=True, read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "course_details",
            "title",
            "description",
            "duration_minutes",
            "start_time",
            "end_time",
            "is_active",
            "total_points",
            "questions",
        ]
        read_only_fields = fields
