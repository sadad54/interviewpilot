import json
import logging
from groq import Groq
from pydantic import ValidationError
from app.schemas.evaluation import EvaluationResult

EVAL_MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 2

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a strict, fair technical interview evaluator.
You will be given an interview question and a candidate's answer.
Score the answer using exactly this JSON schema, with no extra text before or after:

{
  "criteria_scores": {
    "technical_accuracy": <int 0-10>,
    "clarity": <int 0-10>,
    "depth": <int 0-10>
  },
  "overall_score": <float 0-10>,
  "feedback": "<2-3 sentences of specific, actionable feedback>"
}

Rules:
- Be strict. Most answers should not score above 7 unless genuinely strong.
- overall_score should reflect the weighted reality of the three criteria, not just their average.
- feedback must reference something specific the candidate actually said.
- Return ONLY the JSON object. No markdown, no commentary, no code fences.
"""


def build_user_prompt(question_text: str, answer_text: str) -> str:
    return f"Question: {question_text}\n\nCandidate's Answer: {answer_text}"


def build_repair_prompt(bad_output: str, error_detail: str) -> str:
    return f"""Your previous response was invalid.

Your output: {bad_output}

Validation error: {error_detail}

Return ONLY a corrected JSON object matching the required schema exactly. No commentary."""


def evaluate_response(client: Groq, question_text: str, answer_text: str) -> EvaluationResult:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(question_text, answer_text)},
    ]

    last_error = None

    for attempt in range(1, MAX_RETRIES + 2):  # initial attempt + MAX_RETRIES repairs
        completion = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw_content = completion.choices[0].message.content or ""

        try:
            parsed = json.loads(raw_content)
            return EvaluationResult(**parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            logger.warning(f"Evaluation attempt {attempt} failed validation: {e}")

            if attempt <= MAX_RETRIES:
                # Feed the model its own bad output + the specific error, ask it to fix it
                messages.append({"role": "assistant", "content": raw_content})
                messages.append({"role": "user", "content": build_repair_prompt(raw_content, str(e))})

    raise ValueError(f"Evaluation failed after {MAX_RETRIES + 1} attempts. Last error: {last_error}")