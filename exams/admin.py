from django.contrib import admin

from .models import Exam, Question


class QuestionInline(admin.TabularInline):
    """Inline admin for questions within an exam."""

    model = Question
    extra = 1
    fields = ["order", "question_type", "question_text", "points"]
    ordering = ["order"]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin interface for Exam model."""

    list_display = [
        "title",
        "course",
        "duration_minutes",
        "start_time",
        "end_time",
        "is_published",
        "created_at",
    ]
    list_filter = ["is_published", "course", "start_time"]
    search_fields = ["title", "description", "course__code", "course__title"]
    ordering = ["-start_time"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [QuestionInline]

    fieldsets = (
        (None, {"fields": ("course", "title", "description")}),
        (
            "Duration & Schedule",
            {"fields": ("duration_minutes", "start_time", "end_time")},
        ),
        ("Settings", {"fields": ("is_published", "metadata")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""

    list_display = ["exam", "order", "question_type", "points", "created_at"]
    list_filter = ["question_type", "exam__course"]
    search_fields = ["question_text", "exam__title"]
    ordering = ["exam", "order"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("exam", "order")}),
        ("Question Content", {"fields": ("question_type", "question_text")}),
        ("Answer & Grading", {"fields": ("expected_answer", "options", "points")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
