from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any

import pandas as pd


def clean_json_string(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        return match.group(0).strip()

    return text


def safe_json_loads(raw_text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    try:
        return json.loads(clean_json_string(raw_text))
    except Exception:
        return fallback


def extract_persona_name(persona_text: str) -> str:
    parts = persona_text.split(". ", 1)
    return parts[1] if len(parts) > 1 else persona_text


def summarize_excel(uploaded_file) -> str:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        lines: list[str] = [f"Workbook sheets: {sheet_names}"]

        for sheet in sheet_names[:3]:
            df = pd.read_excel(xls, sheet_name=sheet)
            lines.append(f"\nSheet: {sheet}")
            lines.append(f"Columns: {list(df.columns)}")
            lines.append(f"Rows: {len(df)}")
            if not df.empty:
                preview = df.head(8).fillna("").to_string(index=False)
                lines.append(f"Preview:\n{preview}")

        return "\n".join(lines)
    except Exception as exc:
        return f"Excel parsing failed: {exc}"


def local_originality_score(text: str) -> tuple[int, str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return 0, "No response submitted."

    words = re.findall(r"\b[\w'-]+\b", cleaned.lower())
    if len(words) < 30:
        return 40, "Short answer. Originality signal is limited due to low text volume."

    word_counts = Counter(words)
    repeated_ratio = sum(c for c in word_counts.values() if c > 2) / max(len(words), 1)

    sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned) if s.strip()]
    sentence_lengths = [len(re.findall(r"\b[\w'-]+\b", s)) for s in sentences if s]
    variance = _variance(sentence_lengths) if len(sentence_lengths) > 1 else 0.0

    generic_phrases = [
        "it is important to note",
        "in conclusion",
        "tailored to your needs",
        "balanced approach",
        "carefully consider",
        "based on your risk profile",
        "diversified portfolio",
    ]
    generic_hits = sum(1 for phrase in generic_phrases if phrase in cleaned.lower())

    score = 78
    score -= int(repeated_ratio * 100)
    score -= min(generic_hits * 7, 21)
    score += min(int(math.sqrt(max(variance, 0))), 12)

    score = max(5, min(95, score))

    if score >= 75:
        reason = "Language pattern looks reasonably natural, with decent variation and low template repetition."
    elif score >= 55:
        reason = "Response appears partly templated but still shows some natural variation."
    else:
        reason = "Response looks highly templated or repetitive, which may reduce originality confidence."

    return score, reason


def _variance(values: list[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)