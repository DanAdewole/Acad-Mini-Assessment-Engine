from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubmissionViewSet

app_name = "submissions"

router = DefaultRouter()
router.register(r"", SubmissionViewSet, basename="submission")

urlpatterns = [
    path("", include(router.urls)),
]
