from django.db import models
from django.core.validators import MinValueValidator

from courses.models import Course


class Exam(models.Model):
    """
    Assessment instance within a course.

    Attributes:
        course (Course): The course this exam belongs to
        title (str): Exam title
        description (str): Detailed exam description
        duration_minutes (int): Time limit in minutes
        metadata (dict): Additional flexible data stored as JSON
        start_time (datetime): When the exam opens
        end_time (datetime): When the exam closes
        is_published (bool): Whether the exam is visible to students
        created_at (datetime): When the exam was created
        updated_at (datetime): When the exam was last updated
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="exams",
        help_text="The course this exam belongs to",
    )
    title = models.CharField(max_length=200, help_text="Exam title")
    description = models.TextField(blank=True, help_text="Detailed exam description")
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Time limit in minutes",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional flexible data (e.g., instructions, settings)",
    )
    start_time = models.DateTimeField(help_text="When the exam opens for submissions")
    end_time = models.DateTimeField(help_text="When the exam closes")
    is_published = models.BooleanField(
        default=False,
        help_text="Whether the exam is visible to students",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the exam was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the exam was last updated"
    )

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["start_time"]),
            models.Index(fields=["end_time"]),
            models.Index(fields=["course", "is_published"]),
        ]
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        """String representation of the exam."""
        return f"{self.course.code} - {self.title}"

    @property
    def is_active(self):
        """Check if exam is currently accepting submissions."""
        from django.utils import timezone

        now = timezone.now()
        return self.is_published and self.start_time <= now <= self.end_time

    @property
    def total_points(self):
        """Calculate total points available in this exam."""
        return self.questions.aggregate(total=models.Sum("points"))["total"] or 0


class Question(models.Model):
    """
    Individual question within an exam.

    Attributes:
        exam (Exam): The exam this question belongs to
        question_type (str): Type of question (multiple_choice, short_answer, essay)
        question_text (str): The question content
        expected_answer (dict): Expected answer stored as JSON
        options (dict): Answer options for multiple choice (stored as JSON)
        points (int): Points awarded for correct answer
        order (int): Display order within the exam
        created_at (datetime): When the question was created
        updated_at (datetime): When the question was last updated
    """

    class QuestionType(models.TextChoices):
        """Available question types."""

        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        SHORT_ANSWER = "short_answer", "Short Answer"
        ESSAY = "essay", "Essay"
        TRUE_FALSE = "true_false", "True/False"

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="The exam this question belongs to",
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        help_text="Type of question",
    )
    question_text = models.TextField(help_text="The question content")
    expected_answer = models.JSONField(
        help_text="Expected answer (format varies by question type)"
    )
    options = models.JSONField(
        default=dict,
        blank=True,
        help_text="Answer options for multiple choice questions",
    )
    points = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Points awarded for correct answer",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within the exam",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the question was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the question was last updated"
    )

    class Meta:
        ordering = ["exam", "order"]
        indexes = [
            models.Index(fields=["exam"]),
            models.Index(fields=["exam", "order"]),
        ]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        """String representation of the question."""
        return f"{self.exam.title} - Q{self.order}"
