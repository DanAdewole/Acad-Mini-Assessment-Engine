from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from exams.models import Exam, Question


class Submission(models.Model):
    """
    Student's exam attempt/submission.

    Attributes:
        user (User): The student who submitted
        exam (Exam): The exam being submitted
        submitted_at (datetime): When the submission was completed
        graded_at (datetime): When the submission was graded
        total_score (float): Student's total score
        max_score (float): Maximum possible score
        status (str): Submission status (in_progress, submitted, graded)
        metadata (dict): Additional flexible data stored as JSON
        created_at (datetime): When the submission was started
        updated_at (datetime): When the submission was last updated
    """

    class Status(models.TextChoices):
        """Submission statuses."""

        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        GRADED = "graded", "Graded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="The student who submitted",
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="The exam being submitted",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the submission was completed",
    )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the submission was graded",
    )
    total_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Student's total score",
    )
    max_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Maximum possible score",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        help_text="Current submission status",
        db_index=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional flexible data (e.g., IP address, browser info)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the submission was started"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the submission was last updated"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user", "exam"]),
            models.Index(fields=["exam", "status"]),
            models.Index(fields=["submitted_at"]),
        ]
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"
        # does not allow retake, only one submission per exam per user
        unique_together = [["user", "exam"]]

    def __str__(self):
        """String representation of the submission."""
        return f"{self.user.email} - {self.exam.title}"

    @property
    def percentage_score(self):
        """Calculate percentage score."""
        if self.max_score > 0:
            return (self.total_score / self.max_score) * 100
        return 0.0

    @property
    def is_passed(self, passing_score=60):
        """Check if submission passed (default 60%)."""
        return self.percentage_score >= passing_score


class Answer(models.Model):
    """
    Individual answer within a submission.

    Attributes:
        submission (Submission): The submission this answer belongs to
        question (Question): The question being answered
        answer_text (str): Student's text answer
        answer_data (dict): Structured answer data stored as JSON
        score (float): Points earned for this answer
        max_score (float): Maximum points available
        grading_feedback (dict): Detailed grading feedback stored as JSON
        created_at (datetime): When the answer was created
        updated_at (datetime): When the answer was last updated
    """

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="answers",
        help_text="The submission this answer belongs to",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        help_text="The question being answered",
    )

    answer_text = models.TextField(
        blank=True,
        help_text="Student's text answer",
    )
    answer_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured answer data (e.g., selected option, multiple values)",
    )
    score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Points earned for this answer",
    )
    max_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Maximum points available",
    )
    grading_feedback = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed grading feedback (e.g., correctness, suggestions)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the answer was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the answer was last updated"
    )

    class Meta:
        ordering = ["submission", "question__order"]
        indexes = [
            models.Index(fields=["submission"]),
            models.Index(fields=["question"]),
            models.Index(fields=["submission", "question"]),
        ]
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        # one answer per question per submission
        unique_together = [["submission", "question"]]

    def __str__(self):
        """String representation of the answer."""
        return f"{self.submission.user.email} - Q{self.question.order}"

    @property
    def percentage_score(self):
        """Calculate percentage score for this answer."""
        if self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0.0
