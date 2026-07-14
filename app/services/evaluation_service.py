import json
from groq import Groq
from app.schemas.evaluation import EvaluationResult

EVAL_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT ="""You are a strict, fair technical interview evaluator.
You will be given an interview question and a candidate's answer.
Score the answer using exactly this JSON schema, with no extra before or after:
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

def build_user_prompt(question_text: str, answer_text:str) -> str:
    return f"Question: {question_text}\n\nCandidates's Answer: {answer_text}"

def evaluate_response(client: Groq, question_text:str, answer_text:str)->EvaluationResult:
    completion = client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question_text, answer_text)}
        ],
        temperature=0.2,
        response_format={"type":"json_object"},
    )

    raw_content = completion.choices[0].message.content
    if raw_content is None:
      raise ValueError("Model returned empty content")
    parsed = json.loads(raw_content)
    return EvaluationResult(**parsed)