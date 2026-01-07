import json
from typing import Any, Dict

from decouple import config

from .base import GradingService


class GeminiGradingService(GradingService):
    """
    AI-powered grading service using Google's Gemini models.
    """

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini grading service.
        """
        self.api_key = api_key or config("GEMINI_API_KEY", default="")
        self.model = model

        if not self.api_key:
            raise ValueError("Google AI API key is required for Gemini grading.")

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(
                model_name=self.model,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
            )
        except ImportError:
            raise ImportError(
                "google-generativeai package is required for Gemini grading. "
                "Install it with: poetry add google-generativeai"
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
        Grade a single answer using Gemini AI.
        """
        prompt = self._build_grading_prompt(
            question_type, student_answer, expected_answer, max_points, options
        )

        try:
            response = self.client.generate_content(prompt)
            result_text = response.text

            # Extract JSON from response (Gemini sometimes adds markdown)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # Validate and normalize the result
            score = float(result.get("score", 0))
            score = max(0.0, min(float(max_points), score))  # Clamp to valid range

            correctness = self.normalize_score(score, max_points)

            return {
                "score": round(score, 2),
                "max_score": float(max_points),
                "feedback": {
                    "message": result.get("feedback", "No feedback provided"),
                    "correctness": round(correctness, 2),
                    "strengths": result.get("strengths", []),
                    "improvements": result.get("improvements", []),
                    "detailed_analysis": result.get("detailed_analysis", ""),
                },
                "correctness": round(correctness, 2),
            }

        except Exception as e:
            # Fallback error response
            return {
                "score": 0.0,
                "max_score": float(max_points),
                "feedback": {
                    "message": f"Error during Gemini grading: {str(e)}",
                    "correctness": 0.0,
                    "error": str(e),
                },
                "correctness": 0.0,
            }

    def grade_submission(self, submission, answers) -> Dict[str, Any]:
        """
        Grade an entire submission using Gemini AI.
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

    def _build_grading_prompt(
        self,
        question_type: str,
        student_answer: str,
        expected_answer: Dict[str, Any],
        max_points: int,
        options: Dict[str, Any] = None,
    ) -> str:
        """
        Build a detailed grading prompt for Gemini AI.
        """
        expected_text = expected_answer.get("answer", "")

        prompt = f"""You are an expert educational assessment grader. Grade the following student answer fairly and provide constructive feedback.

**Question Type:** {question_type}
**Maximum Points:** {max_points}

**Expected Answer:**
{expected_text}

**Student's Answer:**
{student_answer}
"""

        # Add options for multiple choice questions
        if question_type == "multiple_choice" and options:
            prompt += f"\n**Available Options:**\n{json.dumps(options, indent=2)}\n"

        prompt += """

**Grading Instructions:**
1. Evaluate the accuracy and completeness of the student's answer
2. Award partial credit where appropriate
3. Consider different valid ways of expressing the same concept
4. For multiple choice/true-false, be strict about correctness
5. For essays and short answers, evaluate understanding and completeness

**Return your evaluation as a JSON object with this exact structure (no markdown, just JSON):**
{
    "score": <number between 0 and max_points>,
    "feedback": "<brief overall feedback message>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "improvements": ["<area for improvement 1>", "<area for improvement 2>"],
    "detailed_analysis": "<detailed explanation of the grading decision>"
}

**Important:** 
- Be fair but rigorous in your grading
- Provide constructive, specific feedback
- Award full points only for excellent answers
- Partial credit should reflect the degree of understanding shown
- Return ONLY valid JSON, no additional text or markdown
"""

        return prompt
