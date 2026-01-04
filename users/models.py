from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        # Validate superuser flags
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for students and instructors.

    Meta:
        ordering: Orders users by date created (newest first)
        indexes: Optimizes queries by role and email
    """

    class RoleChoices(models.TextChoices):
        """Available user roles in the system."""

        STUDENT = "student", "Student"
        INSTRUCTOR = "instructor", "Instructor"
        ADMIN = "admin", "Admin"

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text="Optional username",
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.STUDENT,
        help_text="User role in the system",
        db_index=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when user was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when user was last updated"
    )
    # Make email required and unique
    email = models.EmailField(
        unique=True,
        help_text="User's email address (must be unique)",
    )

    # Custom manager
    objects = UserManager()

    # Authentication settings
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """String representation of the user."""
        return f"{self.email} ({self.get_role_display()})"

    def get_full_name(self):
        """
        Return the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == self.RoleChoices.STUDENT

    @property
    def is_instructor(self):
        """Check if user is an instructor."""
        return self.role == self.RoleChoices.INSTRUCTOR

    @property
    def is_admin_user(self):
        """Check if user is an admin."""
        return self.role == self.RoleChoices.ADMIN
