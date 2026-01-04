from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Password must be at least 8 characters long",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirm your password",
    )
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "role",
            "token",
        ]
        extra_kwargs = {
            "role": {"default": "student"},
        }

    @extend_schema_field(serializers.CharField)
    def get_token(self, obj):
        """Get or create auth token for the user."""
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return attrs

    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value.lower()

    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop("password_confirm")

        # Create user using custom manager (handles password hashing)
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read-only, for returning user info).
    """

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="User's password",
    )
    token = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(UserSerializer)
    def get_user(self, obj):
        """Get user data."""
        user = obj.get("user")
        return UserSerializer(user).data if user else None

    def validate(self, attrs):
        """Authenticate user with email and password."""
        email = attrs.get("email", "").lower()
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        # Get user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled. Please contact support."
            )

        # Get or create token
        token, created = Token.objects.get_or_create(user=user)

        attrs["user"] = user
        attrs["token"] = token.key

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """

    old_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Validate passwords."""
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match"}
            )
        return attrs

    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
