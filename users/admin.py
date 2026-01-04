from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    """

    # Fields to display in the user list
    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "created_at",
    ]

    # Fields to filter by in the sidebar
    list_filter = ["role", "is_active", "is_staff", "created_at"]

    # Fields to search (email is primary now)
    search_fields = ["email", "first_name", "last_name"]

    # Default ordering
    ordering = ["-created_at"]

    # Read-only fields
    readonly_fields = ["created_at", "updated_at", "last_login", "date_joined"]

    # Fieldsets for the detail/edit page
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "username")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )

    # Fieldsets for adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "username",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
