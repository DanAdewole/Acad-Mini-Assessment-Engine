from rest_framework import serializers

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model.
    Includes computed field for active exams count.
    """

    active_exams_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "title",
            "description",
            "is_active",
            "active_exams_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "active_exams_count", "created_at", "updated_at"]

    def validate_code(self, value):
        """Validate course code is uppercase and alphanumeric."""
        if not value.replace("-", "").replace("_", "").isalnum():
            raise serializers.ValidationError(
                "Course code must be alphanumeric (hyphens and underscores allowed)"
            )
        return value.upper()


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing courses.
    Excludes description for better performance.
    """

    active_exams_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "code", "title", "is_active", "active_exams_count"]
        read_only_fields = fields
