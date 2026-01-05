import re
from typing import Any, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .base import GradingService


class MockGradingService(GradingService):
    """
    Mock grading service implementation.

    Grading strategies:
    - Multiple Choice: Exact match
    - True/False: Exact match
    - Short Answer: TF-IDF + Cosine Similarity + Keyword matching
    - Essay: TF-IDF + Cosine Similarity with higher threshold
    """

    def __init__(self):
        """Initialize the grading service."""
        self.tfidf_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            max_features=1000,
            ngram_range=(1, 2),  # Unigrams and bigrams
        )

    def grade_answer(
        self,
        question_type: str,
        student_answer: str,
        expected_answer: Dict[str, Any],
        max_points: int,
        options: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Grade a single answer based on question type.
        """
        if question_type == "multiple_choice":
            return self._grade_multiple_choice(
                student_answer, expected_answer, max_points, options
            )
        elif question_type == "true_false":
            return self._grade_true_false(student_answer, expected_answer, max_points)
        elif question_type == "short_answer":
            return self._grade_short_answer(student_answer, expected_answer, max_points)
        elif question_type == "essay":
            return self._grade_essay(student_answer, expected_answer, max_points)
        else:
            # Unknown question type - return 0
            return {
                "score": 0.0,
                "max_score": float(max_points),
                "feedback": {
                    "message": "Unknown question type",
                    "correctness": 0.0,
                },
                "correctness": 0.0,
            }

    def grade_submission(self, submission, answers) -> Dict[str, Any]:
        """
        Grade an entire submission.
        """
        total_score = 0.0
        max_score = 0.0
        graded_answers = []

        for answer in answers:
            question = answer.question

            # Get student's answer
            student_answer = answer.answer_text or str(
                answer.answer_data.get("selected", "")
            )

            # Grade the answer
            result = self.grade_answer(
                question_type=question.question_type,
                student_answer=student_answer,
                expected_answer=question.expected_answer,
                max_points=question.points,
                options=question.options,
            )

            # Update answer with grading results
            answer.score = result["score"]
            answer.max_score = result["max_score"]
            answer.grading_feedback = result["feedback"]
            answer.save()

            total_score += result["score"]
            max_score += result["max_score"]

            graded_answers.append(
                {
                    "answer_id": answer.id,
                    "question_id": question.id,
                    "score": result["score"],
                    "max_score": result["max_score"],
                    "correctness": result["correctness"],
                }
            )

        return {
            "total_score": total_score,
            "max_score": max_score,
            "graded_answers": graded_answers,
        }

    def _grade_multiple_choice(
        self,
        student_answer: str,
        expected_answer: Dict[str, Any],
        max_points: int,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Grade multiple choice question with exact matching.
        """
        correct_answer = expected_answer.get("answer", "")
        student_choice = student_answer.strip().upper()
        correct_choice = str(correct_answer).strip().upper()

        is_correct = student_choice == correct_choice

        score = float(max_points) if is_correct else 0.0
        correctness = 100.0 if is_correct else 0.0

        return {
            "score": score,
            "max_score": float(max_points),
            "feedback": {
                "message": (
                    "Correct!"
                    if is_correct
                    else f"Incorrect. The correct answer is {correct_choice}."
                ),
                "correctness": correctness,
                "expected": correct_choice,
                "student": student_choice,
            },
            "correctness": correctness,
        }

    def _grade_true_false(
        self, student_answer: str, expected_answer: Dict[str, Any], max_points: int
    ) -> Dict[str, Any]:
        """
        Grade true/false question with exact matching.
        """
        correct_answer = str(expected_answer.get("answer", "")).strip().lower()
        student_choice = student_answer.strip().lower()

        # Normalize variations
        true_values = ["true", "t", "yes", "y", "1"]
        false_values = ["false", "f", "no", "n", "0"]

        # Normalize student answer
        if student_choice in true_values:
            student_normalized = "true"
        elif student_choice in false_values:
            student_normalized = "false"
        else:
            student_normalized = student_choice

        # Normalize expected answer
        if correct_answer in true_values:
            correct_normalized = "true"
        elif correct_answer in false_values:
            correct_normalized = "false"
        else:
            correct_normalized = correct_answer

        is_correct = student_normalized == correct_normalized

        score = float(max_points) if is_correct else 0.0
        correctness = 100.0 if is_correct else 0.0

        return {
            "score": score,
            "max_score": float(max_points),
            "feedback": {
                "message": (
                    "Correct!"
                    if is_correct
                    else f"Incorrect. The correct answer is {correct_normalized.capitalize()}."
                ),
                "correctness": correctness,
                "expected": correct_normalized,
                "student": student_normalized,
            },
            "correctness": correctness,
        }

    def _grade_short_answer(
        self, student_answer: str, expected_answer: Dict[str, Any], max_points: int
    ) -> Dict[str, Any]:
        """
        Grade short answer using TF-IDF + cosine similarity + keyword matching.
        """
        expected_text = expected_answer.get("answer", "")

        # Clean texts
        student_clean = self._clean_text(student_answer)
        expected_clean = self._clean_text(expected_text)

        # Check for empty answers
        if not student_clean:
            return {
                "score": 0.0,
                "max_score": float(max_points),
                "feedback": {
                    "message": "No answer provided",
                    "correctness": 0.0,
                },
                "correctness": 0.0,
            }

        # Calculate TF-IDF similarity
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                [expected_clean, student_clean]
            )
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            # Fallback if TF-IDF fails
            similarity = 0.0

        # Calculate keyword matching score
        keyword_score = self._calculate_keyword_match(expected_clean, student_clean)

        # Combine scores (70% TF-IDF, 30% keywords)
        final_similarity = (similarity * 0.7) + (keyword_score * 0.3)

        # Convert to correctness percentage
        correctness = final_similarity * 100

        # Calculate score
        score = (correctness / 100) * max_points

        return {
            "score": round(score, 2),
            "max_score": float(max_points),
            "feedback": {
                "message": self.get_feedback_message(correctness),
                "correctness": round(correctness, 2),
                "similarity_score": round(similarity * 100, 2),
                "keyword_score": round(keyword_score * 100, 2),
            },
            "correctness": round(correctness, 2),
        }

    def _grade_essay(
        self, student_answer: str, expected_answer: Dict[str, Any], max_points: int
    ) -> Dict[str, Any]:
        """
        Grade essay using TF-IDF + cosine similarity.
        """
        expected_text = expected_answer.get("answer", "")

        # Clean texts
        student_clean = self._clean_text(student_answer)
        expected_clean = self._clean_text(expected_text)

        # Check for empty answers
        if not student_clean:
            return {
                "score": 0.0,
                "max_score": float(max_points),
                "feedback": {
                    "message": "No answer provided",
                    "correctness": 0.0,
                },
                "correctness": 0.0,
            }

        # Calculate TF-IDF similarity
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                [expected_clean, student_clean]
            )
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            similarity = 0.0

        # Calculate keyword matching
        keyword_score = self._calculate_keyword_match(expected_clean, student_clean)

        # For essays, give more weight to TF-IDF (80% TF-IDF, 20% keywords)
        final_similarity = (similarity * 0.8) + (keyword_score * 0.2)

        # Convert to correctness percentage
        correctness = final_similarity * 100

        # Calculate score
        score = (correctness / 100) * max_points

        return {
            "score": round(score, 2),
            "max_score": float(max_points),
            "feedback": {
                "message": self.get_feedback_message(correctness),
                "correctness": round(correctness, 2),
                "similarity_score": round(similarity * 100, 2),
                "keyword_score": round(keyword_score * 100, 2),
                "word_count": len(student_clean.split()),
            },
            "correctness": round(correctness, 2),
        }

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for comparison.
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        # Remove punctuation except periods and commas
        text = re.sub(r"[^\w\s.,]", "", text)

        return text.strip()

    def _calculate_keyword_match(self, expected: str, student: str) -> float:
        """
        Calculate keyword matching score.
        """
        # Extract words (excluding common stop words)
        expected_words = set(expected.split())
        student_words = set(student.split())

        # Remove very short words
        expected_words = {w for w in expected_words if len(w) > 3}
        student_words = {w for w in student_words if len(w) > 3}

        if not expected_words:
            return 0.0

        # Calculate overlap
        matches = expected_words.intersection(student_words)
        score = len(matches) / len(expected_words)

        return min(1.0, score)
