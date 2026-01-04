from django.db import models


class Course(models.Model):
    """
    Academic course that contains exams.

    Attributes:
        code (str): Unique course code (e.g., 'CS101')
        title (str): Course title
        description (str): Detailed course description
        is_active (bool): Whether the course is currently active
        created_at (datetime): When the course was created
        updated_at (datetime): When the course was last updated
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique course code (e.g., 'CS101')",
        db_index=True,
    )
    title = models.CharField(max_length=200, help_text="Course title")
    description = models.TextField(blank=True, help_text="Detailed course description")
    is_active = models.BooleanField(
        default=True, help_text="Whether the course is currently active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the course was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the course was last updated"
    )

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        """String representation of the course."""
        return f"{self.code} - {self.title}"

    @property
    def active_exams_count(self):
        """Count of published exams in this course."""
        return self.exams.filter(is_published=True).count()
