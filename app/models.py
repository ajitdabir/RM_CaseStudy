from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_HOUSE_VIEW = {
    "Equity": {
        "Large Cap": "Neutral",
        "Mid Cap": "Neutral",
        "Small Cap": "Neutral",
    },
    "Debt": {
        "Accrual": "Neutral",
        "Duration": "Neutral",
        "Credit": "Neutral",
    },
    "Commodities": {
        "Gold": "Neutral",
        "Silver": "Neutral",
    },
}


@dataclass
class EvaluationResult:
    score: int
    house_view_alignment: str
    empathy_score: int
    prudence_score: int
    clarity_score: int
    originality_score: int
    feedback: str
    recommendation_summary: str

    @classmethod
    def fallback(cls, reason: str) -> "EvaluationResult":
        return cls(
            score=0,
            house_view_alignment="Fail",
            empathy_score=0,
            prudence_score=0,
            clarity_score=0,
            originality_score=0,
            feedback=reason,
            recommendation_summary="Evaluation unavailable.",
        )


@dataclass
class AppStateSnapshot:
    xp: int = 0
    level: int = 1
    active_case: str | None = None
    active_persona: str | None = None
    active_engagement: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)