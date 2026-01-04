from django.contrib import admin

from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model."""

    list_display = ["code", "title", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["code", "title", "description"]
    ordering = ["code"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("code", "title", "description")}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
