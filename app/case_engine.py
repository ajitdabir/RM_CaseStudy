from __future__ import annotations

import json

from app.ai_clients import AIClientError, AIQuotaError, LLMGateway
from app.models import EvaluationResult
from app.utils import safe_json_loads


def build_case_study(
    gateway: LLMGateway,
    provider: str,
    persona: str,
    engagement: str,
    house_view: dict,
) -> str:
    prompt = f"""
You are designing a realistic wealth-management simulation for a Relationship Manager.

Client Persona:
{persona}

Engagement Type:
{engagement}

Firm House View:
{json.dumps(house_view, indent=2)}

Instructions:
- Write exactly 2 concise but rich paragraphs.
- Make it realistic, commercially relevant, and client-specific.
- Include market context, emotional context, liquidity or cashflow constraints, and investment complexity.
- Include at least one tension or trade-off the RM must handle.
- Do not provide the final solution or recommendation.
- Keep the tone premium, professional, and realistic.
"""
    try:
        return gateway.generate_text(provider=provider, prompt=prompt, require_json=False)
    except AIQuotaError as exc:
        return f"QUOTA_ERROR: {exc}"
    except AIClientError as exc:
        return f"ERROR: {exc}"
    except Exception as exc:
        return f"ERROR: {exc}"


def evaluate_response(
    gateway: LLMGateway,
    provider: str,
    case_study: str,
    excel_summary: str,
    rm_answer: str,
    house_view: dict,
    originality_score: int,
) -> EvaluationResult:
    prompt = f"""
You are a Senior Wealth Manager evaluating an RM response.

Case Study:
{case_study}

Client Cashflow / Excel Context:
{excel_summary}

Firm House View:
{json.dumps(house_view, indent=2)}

RM Response:
{rm_answer}

Originality Signal Score:
{originality_score}

Evaluate on:
1. House view alignment
2. Empathy for the client context
3. Prudence / fiduciary discipline
4. Clarity and actionability
5. Overall capability score

Return JSON exactly in this format:
{{
  "score": 82,
  "house_view_alignment": "Pass",
  "empathy_score": 80,
  "prudence_score": 84,
  "clarity_score": 81,
  "feedback": "Detailed evaluator feedback",
  "recommendation_summary": "A short summary of what the RM should improve"
}}
"""
    try:
        raw = gateway.generate_text(provider=provider, prompt=prompt, require_json=True)
        data = safe_json_loads(
            raw,
            fallback={
                "score": 0,
                "house_view_alignment": "Fail",
                "empathy_score": 0,
                "prudence_score": 0,
                "clarity_score": 0,
                "feedback": f"Failed to parse evaluator output. Raw: {raw}",
                "recommendation_summary": "Evaluation could not be completed.",
            },
        )

        return EvaluationResult(
            score=int(data.get("score", 0)),
            house_view_alignment=str(data.get("house_view_alignment", "Fail")),
            empathy_score=int(data.get("empathy_score", 0)),
            prudence_score=int(data.get("prudence_score", 0)),
            clarity_score=int(data.get("clarity_score", 0)),
            originality_score=int(originality_score),
            feedback=str(data.get("feedback", "")),
            recommendation_summary=str(data.get("recommendation_summary", "")),
        )
    except AIQuotaError as exc:
        return EvaluationResult.fallback(str(exc))
    except AIClientError as exc:
        return EvaluationResult.fallback(str(exc))
    except Exception as exc:
        return EvaluationResult.fallback(str(exc))


def calculate_xp(score: int, originality_score: int, alignment: str) -> int:
    xp = int(score * 1.3)

    if alignment.lower() == "pass":
        xp += 20
    else:
        xp -= 15

    if originality_score >= 75:
        xp += 25
    elif originality_score < 50:
        xp -= 10

    return max(0, xp)