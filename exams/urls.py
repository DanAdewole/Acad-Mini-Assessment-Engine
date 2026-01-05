from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExamViewSet, QuestionViewSet

app_name = "exams"

router = DefaultRouter()
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"questions", QuestionViewSet, basename="question")

urlpatterns = [
    path("", include(router.urls)),
]
