from django.utils import timezone
from rest_framework import serializers

from exams.models import Exam, Question
from exams.serializers import ExamListSerializer, QuestionSerializer
from users.serializers import UserSerializer

from .models import Answer, Submission


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for Answer model.
    """

    question_details = QuestionSerializer(source="question", read_only=True)
    percentage_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "submission",
            "question",
            "question_details",
            "answer_text",
            "answer_data",
            "score",
            "max_score",
            "percentage_score",
            "grading_feedback",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "score",
            "max_score",
            "percentage_score",
            "grading_feedback",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """Validate answer data."""
        question = attrs.get("question")
        answer_text = attrs.get("answer_text", "")
        answer_data = attrs.get("answer_data", {})

        # Ensure at least one answer field is provided
        if not answer_text and not answer_data:
            raise serializers.ValidationError(
                "Either answer_text or answer_data must be provided"
            )

        # Validate answer_data structure for multiple choice
        if question and question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
            if not isinstance(answer_data, dict) or "selected" not in answer_data:
                raise serializers.ValidationError(
                    {
                        "answer_data": "Multiple choice answers must have 'selected' field"
                    }
                )

        return attrs


class AnswerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating answers.
    """

    class Meta:
        model = Answer
        fields = [
            "question",
            "answer_text",
            "answer_data",
        ]

    def validate(self, attrs):
        """Validate answer data."""
        question = attrs.get("question")
        answer_text = attrs.get("answer_text", "")
        answer_data = attrs.get("answer_data", {})

        # Ensure at least one answer field is provided
        if not answer_text and not answer_data:
            raise serializers.ValidationError(
                "Either answer_text or answer_data must be provided"
            )

        return attrs


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission model with nested answers.
    """

    user_details = UserSerializer(source="user", read_only=True)
    exam_details = ExamListSerializer(source="exam", read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    percentage_score = serializers.FloatField(read_only=True)
    is_passed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "user",
            "user_details",
            "exam",
            "exam_details",
            "submitted_at",
            "graded_at",
            "total_score",
            "max_score",
            "percentage_score",
            "status",
            "is_passed",
            "metadata",
            "answers",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "submitted_at",
            "graded_at",
            "total_score",
            "max_score",
            "percentage_score",
            "is_passed",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_is_passed(self, obj):
        """Check if submission passed."""
        return obj.is_passed

    def validate_exam(self, value):
        """
        Validate exam is available for submission.
        """
        exam = value
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        # Check if exam is published
        if not exam.is_published:
            raise serializers.ValidationError("This exam is not published yet")

        # Check time window
        now = timezone.now()
        if now < exam.start_time:
            raise serializers.ValidationError(
                f"This exam hasn't started yet. It starts at {exam.start_time}"
            )
        if now > exam.end_time:
            raise serializers.ValidationError(
                f"This exam has ended. It ended at {exam.end_time}"
            )

        # Check for duplicate submission (only for creation)
        if self.instance is None:
            existing = Submission.objects.filter(user=request.user, exam=exam).exists()
            if existing:
                raise serializers.ValidationError(
                    "You have already submitted this exam"
                )

        return value


class SubmissionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating submissions with answers.
    """

    exam_id = serializers.IntegerField(write_only=True)
    answers = AnswerCreateSerializer(many=True, write_only=True)
    submission = SubmissionSerializer(read_only=True)

    def validate_exam_id(self, value):
        """Validate exam exists and is available."""
        try:
            exam = Exam.objects.get(id=value)
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Exam not found")

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        # Check if exam is published
        if not exam.is_published:
            raise serializers.ValidationError("This exam is not published yet")

        # Check time window
        now = timezone.now()
        if now < exam.start_time:
            raise serializers.ValidationError("This exam hasn't started yet")
        if now > exam.end_time:
            raise serializers.ValidationError("This exam has ended")

        # Check for duplicate submission
        existing = Submission.objects.filter(user=request.user, exam=exam).exists()
        if existing:
            raise serializers.ValidationError("You have already submitted this exam")

        return value

    def validate_answers(self, value):
        """Validate answers list is not empty."""
        if not value:
            raise serializers.ValidationError("At least one answer is required")
        return value

    def validate(self, attrs):
        """
        Validate submission completeness.
        """
        exam_id = attrs.get("exam_id")
        answers = attrs.get("answers", [])

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise serializers.ValidationError({"exam_id": "Exam not found"})

        # Get all questions for this exam
        exam_questions = set(exam.questions.values_list("id", flat=True))
        answered_questions = set(
            answer["question"].id for answer in answers if "question" in answer
        )

        # Check if all questions are answered
        missing_questions = exam_questions - answered_questions
        if missing_questions:
            raise serializers.ValidationError(
                {
                    "answers": f"Missing answers for {len(missing_questions)} question(s). All questions must be answered."
                }
            )

        # Check for duplicate answers
        if len(answered_questions) != len(answers):
            raise serializers.ValidationError(
                {"answers": "Duplicate answers detected for some questions"}
            )

        return attrs

    def create(self, validated_data):
        """
        Create submission with answers.
        """
        raise NotImplementedError(
            "Use SubmissionViewSet.create() to handle submission creation"
        )


class SubmissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing submissions.
    """

    user_details = UserSerializer(source="user", read_only=True)
    exam_details = ExamListSerializer(source="exam", read_only=True)
    percentage_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "user_details",
            "exam_details",
            "submitted_at",
            "graded_at",
            "total_score",
            "max_score",
            "percentage_score",
            "status",
        ]
        read_only_fields = fields
