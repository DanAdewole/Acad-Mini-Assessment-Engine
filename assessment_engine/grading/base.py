from abc import ABC, abstractmethod
from typing import Dict, Any


class GradingService(ABC):
    """
    Abstract base class for grading services.

    This provides a modular interface that allows different grading
    implementations (mock, AI-based, rules-based, etc.) to be easily
    swapped or extended.
    """

    @abstractmethod
    def grade_answer(
        self,
        question_type: str,
        student_answer: str,
        expected_answer: Dict[str, Any],
        max_points: int,
        options: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Grade a single answer.

        Args:
            question_type: Type of question (multiple_choice, short_answer, essay, true_false)
            student_answer: Student's submitted answer
            expected_answer: Expected/correct answer
            max_points: Maximum points for this question
            options: Additional options (e.g., for multiple choice)

        Returns:
            Dictionary containing:
            - score (float): Points earned
            - max_score (float): Maximum points possible
            - feedback (dict): Grading feedback with details
            - correctness (float): Percentage (0-100)
        """
        pass

    @abstractmethod
    def grade_submission(self, submission, answers) -> Dict[str, Any]:
        """
        Grade an entire submission with multiple answers.

        Args:
            submission: Submission model instance
            answers: List of Answer model instances

        Returns:
            Dictionary containing:
            - total_score (float): Total points earned
            - max_score (float): Total possible points
            - graded_answers (list): List of graded answer details
        """
        pass

    def normalize_score(self, score: float, max_score: float) -> float:
        """
        Normalize score to percentage (0-100).
        """
        if max_score <= 0:
            return 0.0
        return min(100.0, max(0.0, (score / max_score) * 100))

    def get_feedback_message(self, correctness: float) -> str:
        """
        Generate feedback message based on correctness percentage.
        """
        if correctness >= 90:
            return "Excellent! Your answer is highly accurate."
        elif correctness >= 75:
            return "Good work! Your answer is mostly correct."
        elif correctness >= 60:
            return "Fair attempt. Your answer captures some key points."
        elif correctness >= 40:
            return "Needs improvement. Consider reviewing the material."
        else:
            return "Incorrect. Please review the topic and try again."
