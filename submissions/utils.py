from django.conf import settings

from assessment_engine.grading import (
    AIGradingService,
    GeminiGradingService,
    MockGradingService,
)


def get_grading_service():
    """
    Factory function to get the configured grading service.
    """
    service_type = settings.GRADING_SERVICE.lower()

    if service_type == "mock":
        return MockGradingService()
    elif service_type == "ai":
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "GRADING_SERVICE is set to 'ai' but OPENAI_API_KEY is not configured. "
                "Please set OPENAI_API_KEY in your .env file or switch to 'mock' grading."
            )
        return AIGradingService(
            api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL
        )
    elif service_type == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GRADING_SERVICE is set to 'gemini' but GEMINI_API_KEY is not configured. "
                "Please set GEMINI_API_KEY in your .env file or switch to 'mock' grading."
            )
        return GeminiGradingService(
            api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL
        )
    else:
        raise ValueError(
            f"Invalid GRADING_SERVICE: '{service_type}'. Must be 'mock', 'ai', or 'gemini'."
        )
