"""
AI Service — wraps OpenAI GPT-4o for:
  1. Question generation
  2. Candidate evaluation / scoring
"""
import json
import logging
from typing import List, Optional
from openai import OpenAI
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


# ── Question Generation ───────────────────────────────────────────────────────

QUESTION_GEN_SYSTEM = """You are an expert technical interviewer at a top tech company.
Generate high-quality assessment questions in strict JSON format only.
No markdown, no extra text — pure JSON array."""

QUESTION_GEN_TEMPLATE = """Generate {count} {type} questions for a {role} role.
Skills required: {skills}
Difficulty: {difficulty}

Return a JSON array of objects. Each object must have:
- "type": "{type}"
- "difficulty": "{difficulty}"
- "prompt": <question text>
- "options": <array of 4 strings for MCQ, null for others>
- "correct_answer": <correct option index 0-3 for MCQ, reference solution for coding/sql>
- "test_cases": <array of {{"input": "...", "expected_output": "..."}} for coding, null for MCQ>
- "points": <integer 10-30>

For coding questions, write a clear problem statement with input/output format.
For SQL questions, include the table schema in the prompt.
For MCQ, all 4 options must be plausible."""


def generate_questions(
    role: str,
    skills: List[str],
    difficulty: str,
    question_type: str,
    count: int,
) -> List[dict]:
    """Call GPT-4o to generate questions. Returns list of question dicts."""
    prompt = QUESTION_GEN_TEMPLATE.format(
        count=count,
        type=question_type,
        role=role,
        skills=", ".join(skills),
        difficulty=difficulty,
    )
    try:
        client = _client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": QUESTION_GEN_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)
        # GPT-4o with json_object may wrap in a key
        if isinstance(data, dict):
            for key in ("questions", "items", "data"):
                if key in data:
                    data = data[key]
                    break
            else:
                data = list(data.values())[0] if data else []
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error("Question generation failed: %s", e)
        raise


# ── Candidate Evaluation ─────────────────────────────────────────────────────

EVAL_SYSTEM = """You are a fair, expert technical evaluator.
Evaluate candidate submissions objectively.
Respond ONLY with a JSON object — no markdown, no extra text."""

EVAL_TEMPLATE = """Evaluate the following candidate assessment submission.

Role: {role}
Assessment Type: {types}

CODE SUBMISSIONS:
{code_block}

MCQ ANSWERS:
{mcq_block}

PROCTORING SIGNALS:
{proctor_block}

Provide scores (0–100) and brief insights. Return JSON:
{{
  "technical_score": <0-100 float>,
  "code_quality_score": <0-100 float>,
  "mcq_score": <0-100 float>,
  "behavioral_score": <0-100 float>,
  "composite_score": <0-100 float>,
  "recommendation": "strong_hire" | "hire" | "borderline" | "no_hire",
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "code_feedback": [{{"question": "...", "feedback": "...", "score": 0-100}}],
  "risk_flags": ["..."],
  "summary": "<2-3 sentence professional summary>"
}}"""


def evaluate_candidate(
    role: str,
    types: List[str],
    code_submissions: List[dict],
    mcq_answers: List[dict],
    proctoring_data: Optional[dict] = None,
) -> dict:
    """
    Call GPT-4o to evaluate a candidate's full submission.
    Returns structured evaluation dict.
    """
    code_block = "\n\n".join(
        f"Q: {s.get('prompt', 'N/A')}\nLanguage: {s.get('language')}\n"
        f"Test Cases Passed: {s.get('passed_cases', '?')}/{s.get('total_cases', '?')}\n"
        f"Code:\n```\n{s.get('code', '')[:1500]}\n```"
        for s in code_submissions
    ) or "No code submissions."

    mcq_block = "\n".join(
        f"Q: {m.get('prompt', 'N/A')} | Answered: {m.get('answer_index')} "
        f"| Correct: {m.get('correct_index')} | {'✓' if m.get('is_correct') else '✗'}"
        for m in mcq_answers
    ) or "No MCQ answers."

    proctor_block = json.dumps(proctoring_data or {}, indent=2)

    prompt = EVAL_TEMPLATE.format(
        role=role,
        types=", ".join(types),
        code_block=code_block,
        mcq_block=mcq_block,
        proctor_block=proctor_block,
    )

    try:
        client = _client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": EVAL_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        logger.error("Evaluation failed: %s", e)
        raise


# ── Adaptive Difficulty ───────────────────────────────────────────────────────

def next_question_difficulty(current_score: float) -> str:
    """IRT-inspired adaptive difficulty selection."""
    if current_score >= 0.80:
        return "hard"
    elif current_score >= 0.50:
        return "medium"
    else:
        return "easy"
