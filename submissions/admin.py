from django.contrib import admin

from .models import Answer, Submission


class AnswerInline(admin.TabularInline):
    """Inline admin for answers within a submission."""

    model = Answer
    extra = 0
    fields = ["question", "answer_text", "score", "max_score"]
    readonly_fields = ["question"]
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model."""

    list_display = [
        "user",
        "exam",
        "status",
        "total_score",
        "max_score",
        "submitted_at",
        "graded_at",
    ]
    list_filter = ["status", "exam__course", "submitted_at", "graded_at"]
    search_fields = ["user__email", "exam__title"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "submitted_at"]
    inlines = [AnswerInline]

    fieldsets = (
        (None, {"fields": ("user", "exam")}),
        ("Status", {"fields": ("status", "submitted_at", "graded_at")}),
        ("Scoring", {"fields": ("total_score", "max_score")}),
        ("Additional Data", {"fields": ("metadata",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin interface for Answer model."""

    list_display = [
        "submission",
        "question",
        "score",
        "max_score",
        "created_at",
    ]
    list_filter = ["question__question_type", "submission__exam"]
    search_fields = [
        "submission__user__email",
        "question__question_text",
        "answer_text",
    ]
    ordering = ["submission", "question__order"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("submission", "question")}),
        ("Answer", {"fields": ("answer_text", "answer_data")}),
        ("Grading", {"fields": ("score", "max_score", "grading_feedback")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
