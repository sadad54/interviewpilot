import json 
from groq import Groq

FOLLOWUP_MODEL = "llama-3.3-70b-versatile"

FOLLOWUP_SYSTEM_PROMPT = """You are an experienced technical interviewer conducting a live interview.
Given the original question and the candidate's answer, decide whether a follow-up question is warranted.


Ask a follow-up when the answer:
- Is vague or surface-level and could reveal more depth if probed
- Mentions a technique/tool by name without explaining it
- Makes a claim that should be justified

Do NOT ask a follow-up when the answer is already thorough and well-justified. 

Return ONLY this JSON, no other text:
{
  "should_follow_up": <true|false>,
  "follow_up_question": "<question text, or empty string if should_follow_up is false>",
  "reasoning": "<one sentence on why you did or didn't probe further>"
}
"""
def generate_followup(client: Groq, question_text: str, answer_text: str)-> dict:
    completion = client.chat.completions.create(
        model=FOLLOWUP_MODEL,
        messages=[
            {"role":"system", "content":FOLLOWUP_SYSTEM_PROMPT},
            {"role":"user", "content":f"original question: {question_text}\n\Candidate's answer:{answer_text}"},
        ],
        temperature=0.4,
        response_format={"type":"json_object"},
    )
    content = completion.choices[0].message.content
    if content is None:
        raise ValueError("No completion content returned")
    return json.loads(content)