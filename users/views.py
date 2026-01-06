from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assessment_engine.responses import StandardResponse

from .serializers import (
    ChangePasswordSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """
    User registration endpoint.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Create a new user account. student account by default.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserRegistrationSerializer,
                description="User registered successfully",
            ),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return StandardResponse.created(
                data=serializer.data, message="User registered successfully"
            )

        return StandardResponse.validation_error(
            errors=serializer.errors, message="Registration failed"
        )


class LoginView(APIView):
    """
    User login endpoint.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login user",
        description="Authenticate user with email and password. Returns authentication token.",
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=UserLoginSerializer, description="Login successful"
            ),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Login user and return token."""
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            return StandardResponse.success(
                data={
                    "token": serializer.validated_data["token"],
                    "user": UserSerializer(serializer.validated_data["user"]).data,
                },
                message="Login successful",
            )

        return StandardResponse.validation_error(
            errors=serializer.errors, message="Login failed"
        )


class LogoutView(APIView):
    """
    User logout endpoint.

    Deletes the user's auth token to log them out.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout user",
        description="Delete user's auth token to log them out.",
        request=None,
        responses={
            200: OpenApiResponse(description="Logout successful"),
            401: OpenApiResponse(description="Not authenticated"),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Logout user by deleting their token."""
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return StandardResponse.success(message="Logout successful")
        except Exception as e:
            return StandardResponse.error(
                message="Logout failed", status_code=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(APIView):
    """
    Get current authenticated user's information.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user",
        description="Get information about the currently authenticated user.",
        responses={
            200: OpenApiResponse(
                response=UserSerializer, description="User data retrieved"
            ),
            401: OpenApiResponse(description="Not authenticated"),
        },
        tags=["Authentication"],
    )
    def get(self, request):
        """Get current user's data."""
        serializer = UserSerializer(request.user)
        return StandardResponse.success(
            data=serializer.data, message="User data retrieved successfully"
        )


class ChangePasswordView(APIView):
    """
    Change user password endpoint.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="Change current user's password.",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Not authenticated"),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Change user's password."""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # Set new password
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Delete old token and create new one
            Token.objects.filter(user=user).delete()
            new_token = Token.objects.create(user=user)

            return StandardResponse.success(
                data={"token": new_token.key},
                message="Password changed successfully. Please use your new token.",
            )

        return StandardResponse.validation_error(
            errors=serializer.errors, message="Password change failed"
        )
