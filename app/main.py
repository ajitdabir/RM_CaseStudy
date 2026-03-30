from __future__ import annotations

import copy
import json
import math
import os
import re
from collections import Counter
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from google import genai
except Exception:
    genai = None


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "Demo")
APP_NAME = os.getenv("APP_TITLE", "RM Case Study")
APP_SUBTITLE = "RM Capability Engine"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        color: #1F2937;
    }

    .stApp {
        background: #FBFBFC;
    }

    .block-container {
        max-width: 1420px;
        padding-top: 1.1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #1F2937;
        letter-spacing: -0.03em;
    }

    div[data-testid="stSidebar"] {
        min-width: 320px;
        max-width: 350px;
        background: #F4F6F8;
    }

    .brand-title {
        color: #F58024;
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1.04;
        margin-bottom: 0.10rem;
        white-space: normal;
        word-break: break-word;
    }

    .brand-subtitle {
        color: #1F2937;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.25;
        white-space: normal;
        word-break: break-word;
        margin-bottom: 0.8rem;
    }

    .hero {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFFFFF 80%);
        border: 1px solid #FDE7D3;
        border-radius: 18px;
        padding: 20px 22px 16px 22px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 22px rgba(0,0,0,0.03);
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1F2937;
        line-height: 1.08;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        color: #6B7280;
        font-size: 1rem;
        line-height: 1.45;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    .soft-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .small-muted {
        font-size: 0.85rem;
        color: #6B7280;
    }

    .hint-box {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        color: #9A3412;
        border-radius: 12px;
        padding: 12px 14px;
        margin-top: 10px;
        line-height: 1.45;
    }

    .xp-shell {
        width: 100%;
        background: #E5E7EB;
        border-radius: 999px;
        height: 12px;
        overflow: hidden;
    }

    .xp-fill {
        height: 12px;
        background: #F58024;
        border-radius: 999px;
    }

    .badge {
        display: inline-block;
        background: #1F2937;
        color: #FFFFFF;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.80rem;
        font-weight: 700;
    }

    .metric-label {
        color: #6B7280;
        font-size: 0.86rem;
        margin-bottom: 2px;
    }

    .metric-value {
        color: #1F2937;
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1;
    }

    .score-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 88px;
    }

    .stButton > button {
        background: #F58024;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.62rem 1rem;
    }

    .stButton > button:hover {
        background: #D96D1C;
        color: white;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        overflow: hidden;
        background: #FFFFFF;
    }

    .feedback-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 14px 16px;
        line-height: 1.55;
    }

    .ok-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #ECFDF3;
        color: #067647;
        font-weight: 700;
        font-size: 0.80rem;
    }

    .warn-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #FFF6ED;
        color: #C2410C;
        font-weight: 700;
        font-size: 0.80rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

PERSONAS = {
    "20s - 30s (Wealth Accumulators)": [
        "1. Tech Startup Founder (Post-Seed Round, high risk tolerance, illiquid wealth)",
        "2. DINK Couple (Aggressive savers, ESG focused)",
        "3. Medical Resident (High future earning potential, currently high debt)",
        "4. Freelance Consultant (Irregular cash flow, needs liquidity)",
        "5. Inheritance Recipient (Overwhelmed, low financial literacy)",
    ],
    "40s - 50s (Consolidators & Peak Earners)": [
        "6. C-Suite Executive (High concentration of company stock, time-poor)",
        "7. Business Owner (Preparing for exit / sale in 5 years)",
        "8. Sandwich Generation Parent (Funding college and elder care)",
        "9. Divorced Professional (Rebuilding solo wealth, cashflow constraints)",
        "10. Tech VP with RSU Windfall (Needs diversification strategy)",
    ],
    "60+ (Retirement & Legacy Planning)": [
        "11. Fresh Retiree (Transitioning from accumulation to drawdown)",
        "12. High-Net-Worth Widow (Delegator, relies on RM confidence)",
        "13. Business Seller (Large cash pile, inflation anxiety)",
        "14. Extreme Risk-Averse Pensioner (Terrified of capital loss, income focused)",
        "15. Legacy Planner (Estate efficiency and gifting strategy)",
    ],
}

ENGAGEMENT_TYPES = [
    "Deploying Fresh Money",
    "Portfolio Review",
    "Client Query / Panic",
    "Complete Fresh Allocation",
]


def init_state() -> None:
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "level" not in st.session_state:
        st.session_state.level = 1
    if "history" not in st.session_state:
        st.session_state.history = []
    if "active_case" not in st.session_state:
        st.session_state.active_case = None
    if "active_persona" not in st.session_state:
        st.session_state.active_persona = None
    if "active_engagement" not in st.session_state:
        st.session_state.active_engagement = None
    if "case_error" not in st.session_state:
        st.session_state.case_error = None
    if "house_view" not in st.session_state:
        st.session_state.house_view = copy.deepcopy(DEFAULT_HOUSE_VIEW)


def extract_persona_name(persona_text: str) -> str:
    parts = persona_text.split(". ", 1)
    return parts[1] if len(parts) > 1 else persona_text


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text.lower())


def sentence_split(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def word_count(text: str) -> int:
    return len(tokenize_words(text))


def unique_word_ratio(text: str) -> float:
    words = tokenize_words(text)
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def repeated_line_ratio(text: str) -> float:
    lines = [ln.strip().lower() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    return 1 - (len(set(lines)) / len(lines))


def has_gibberish_pattern(text: str) -> bool:
    stripped = text.strip().lower()
    if not stripped:
        return True

    bad_patterns = [
        r"(.)\1{6,}",
        r"[bcdfghjklmnpqrstvwxyz]{7,}",
        r"(asdf|qwer|zxcv){2,}",
    ]
    for pattern in bad_patterns:
        if re.search(pattern, stripped):
            return True

    words = tokenize_words(stripped)
    if not words:
        return True

    short_noise = sum(1 for w in words if len(w) <= 2)
    if len(words) >= 12 and short_noise / len(words) > 0.55:
        return True

    return False


def low_effort_response_reason(text: str) -> str | None:
    wc = word_count(text)
    if wc < 20:
        return "Response is too short to evaluate meaningfully."
    if has_gibberish_pattern(text):
        return "Response appears nonsensical or placeholder-like."
    if unique_word_ratio(text) < 0.32 and wc > 30:
        return "Response is overly repetitive."
    if repeated_line_ratio(text) > 0.34:
        return "Response repeats the same lines too much."
    return None


def summarize_excel(uploaded_file) -> str:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        lines = [f"Workbook sheets: {sheet_names}"]

        for sheet in sheet_names[:3]:
            df = pd.read_excel(xls, sheet_name=sheet)
            lines.append(f"\nSheet: {sheet}")
            lines.append(f"Columns: {list(df.columns)}")
            lines.append(f"Rows: {len(df)}")
            if not df.empty:
                lines.append(f"Preview:\n{df.head(6).fillna('').to_string(index=False)}")

        return "\n".join(lines)
    except Exception as exc:
        return f"Excel parsing failed: {exc}"


def local_originality_score(text: str) -> tuple[int, str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return 0, "No response submitted."

    words = tokenize_words(cleaned)
    if len(words) < 30:
        return 42, "Short answer. Originality signal is limited due to low text volume."

    word_counts = Counter(words)
    repeated_ratio = sum(c for c in word_counts.values() if c > 2) / max(len(words), 1)

    sentences = sentence_split(cleaned)
    sentence_lengths = [len(tokenize_words(s)) for s in sentences if s]
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
        reason = "Language variation looks reasonably natural and not overly templated."
    elif score >= 55:
        reason = "Response appears partly templated but still reasonably usable."
    else:
        reason = "Response looks highly repetitive or templated."

    return score, reason


def _variance(values: list[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


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


def count_hits(text: str, phrases: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for phrase in phrases if phrase in lowered)


def detect_structure_score(text: str) -> int:
    lowered = text.lower()
    signals = [
        "first", "second", "third", "next", "therefore",
        "because", "recommend", "plan", "step", "review",
        "monitor", "phased", "stagger", "immediately", "over the next"
    ]
    hits = count_hits(lowered, signals)
    sentences = sentence_split(text)

    score = 45 + min(hits * 6, 30)
    if len(sentences) >= 4:
        score += 8
    if len(sentences) >= 6:
        score += 5

    return max(20, min(95, score))


def detect_empathy_score(text: str) -> int:
    lowered = text.lower()
    signals = [
        "i understand", "your concern", "your goals", "comfort",
        "liquidity", "cash flow", "volatility", "reassure",
        "short term", "long term", "confidence", "given your situation",
        "important to you", "risk tolerance", "needs"
    ]
    hits = count_hits(lowered, signals)

    score = 40 + min(hits * 7, 42)
    if "you" in lowered:
        score += 5
    if "goal" in lowered or "objectives" in lowered:
        score += 5

    return max(20, min(95, score))


def detect_prudence_score(text: str) -> int:
    lowered = text.lower()
    signals = [
        "diversify", "allocation", "rebalance", "stagger", "phased",
        "risk", "suitable", "liquidity buffer", "emergency",
        "avoid concentration", "time horizon", "review", "debt",
        "equity", "gold", "protect", "preserve capital"
    ]
    hits = count_hits(lowered, signals)

    score = 42 + min(hits * 6, 42)
    if "all in" in lowered:
        score -= 12
    if "guaranteed return" in lowered:
        score -= 15
    if "100%" in lowered and "equity" in lowered:
        score -= 10

    return max(15, min(95, score))


def detect_personalization_score(text: str, persona: str, engagement: str) -> int:
    lowered = text.lower()
    persona_lower = extract_persona_name(persona).lower()
    engagement_lower = engagement.lower()

    persona_tokens = [w for w in tokenize_words(persona_lower) if len(w) > 4]
    persona_hits = sum(1 for token in persona_tokens[:5] if token in lowered)

    engagement_hits = 1 if any(token in lowered for token in tokenize_words(engagement_lower)) else 0

    client_context_terms = [
        "liquidity", "cash flow", "concentration", "volatility",
        "income", "retirement", "legacy", "risk tolerance", "tax"
    ]
    context_hits = count_hits(lowered, client_context_terms)

    score = 38 + min(persona_hits * 10, 20) + min(engagement_hits * 8, 8) + min(context_hits * 4, 20)
    return max(20, min(95, score))


def evaluate_house_view_alignment(answer: str, house_view: dict) -> tuple[str, int, list[str], list[str]]:
    text = answer.lower()
    positives: list[str] = []
    negatives: list[str] = []

    def check_asset(asset_label: str, stance: str, positive_terms: list[str], caution_terms: list[str]) -> int:
        mentioned = asset_label in text
        score_delta = 0
        if not mentioned:
            return 0

        pos_hit = any(term in text for term in positive_terms)
        caution_hit = any(term in text for term in caution_terms)

        if stance == "bullish":
            if pos_hit:
                positives.append(f"Supports {asset_label} in line with bullish house view.")
                score_delta += 10
            elif caution_hit:
                negatives.append(f"Sounds cautious on {asset_label} despite bullish house view.")
                score_delta -= 10

        elif stance == "bearish":
            if caution_hit:
                positives.append(f"Shows caution on {asset_label} in line with bearish house view.")
                score_delta += 10
            elif pos_hit:
                negatives.append(f"Pushes {asset_label} despite bearish house view.")
                score_delta -= 10

        else:
            if pos_hit and caution_hit:
                positives.append(f"Balanced treatment of {asset_label} matches neutral house view.")
                score_delta += 8
            elif pos_hit or caution_hit:
                positives.append(f"Mentions {asset_label} without extreme positioning.")
                score_delta += 3

        return score_delta

    positive_terms = ["increase", "overweight", "allocate", "add", "exposure", "favour", "prefer", "tilt"]
    caution_terms = ["avoid", "limit", "reduce", "underweight", "be cautious", "hold back", "stagger", "moderate"]

    score = 55
    score += check_asset("large cap", house_view["Equity"]["Large Cap"].lower(), positive_terms, caution_terms)
    score += check_asset("mid cap", house_view["Equity"]["Mid Cap"].lower(), positive_terms, caution_terms)
    score += check_asset("small cap", house_view["Equity"]["Small Cap"].lower(), positive_terms, caution_terms)
    score += check_asset("accrual", house_view["Debt"]["Accrual"].lower(), positive_terms, caution_terms)
    score += check_asset("duration", house_view["Debt"]["Duration"].lower(), positive_terms, caution_terms)
    score += check_asset("credit", house_view["Debt"]["Credit"].lower(), positive_terms, caution_terms)
    score += check_asset("gold", house_view["Commodities"]["Gold"].lower(), positive_terms, caution_terms)
    score += check_asset("silver", house_view["Commodities"]["Silver"].lower(), positive_terms, caution_terms)

    score = max(10, min(95, score))
    alignment = "Pass" if score >= 55 and len(negatives) <= 2 else "Fail"
    return alignment, score, positives, negatives


def friendly_provider_error(provider: str, exc: Exception) -> str:
    msg = str(exc)
    upper = msg.upper()

    if provider == "OpenAI":
        if "401" in upper or "INCORRECT API KEY" in upper or "INVALID_API_KEY" in upper:
            return "OpenAI API key is invalid. Update OPENAI_API_KEY in your .env file."
        if "429" in upper or "RATE LIMIT" in upper or "QUOTA" in upper:
            return "OpenAI quota or rate limit reached. Try again later or use Demo mode."
        return f"OpenAI request failed: {msg}"

    if provider == "Gemini":
        if "429" in upper or "RESOURCE_EXHAUSTED" in upper or "QUOTA" in upper:
            return "Gemini quota exhausted. Use OpenAI or Demo mode."
        if "401" in upper or "403" in upper or "API KEY" in upper:
            return "Gemini API key is invalid or not authorized. Update GEMINI_API_KEY in your .env file."
        return f"Gemini request failed: {msg}"

    return msg


def generate_text(provider: str, prompt: str, require_json: bool = False) -> str:
    if provider == "Demo":
        raise RuntimeError("Demo mode uses local generators only.")

    if require_json:
        prompt = (
            f"{prompt}\n\n"
            "Return strictly valid JSON only. "
            "Do not include markdown fences or explanations."
        )

    if provider == "OpenAI":
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        if not OPENAI_API_KEY:
            raise RuntimeError("Missing OPENAI_API_KEY.")

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content or ""

    if provider == "Gemini":
        if genai is None:
            raise RuntimeError("google-genai package is not installed.")
        if not GEMINI_API_KEY:
            raise RuntimeError("Missing GEMINI_API_KEY.")

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return getattr(response, "text", "") or ""

    raise RuntimeError(f"Unsupported provider: {provider}")


def demo_case_study(persona: str, engagement: str, house_view: dict) -> str:
    persona_name = extract_persona_name(persona)
    return f"""
{persona_name} has approached Alpha Lens for a {engagement.lower()} discussion in an environment where market sentiment is mixed and portfolio positioning matters. The current firm stance is {house_view['Equity']['Large Cap'].lower()} on large caps, {house_view['Equity']['Mid Cap'].lower()} on mid caps, and {house_view['Equity']['Small Cap'].lower()} on small caps, while the debt view is {house_view['Debt']['Accrual'].lower()} on accrual, {house_view['Debt']['Duration'].lower()} on duration, and {house_view['Debt']['Credit'].lower()} on credit. The client is financially capable but emotionally conflicted, balancing return expectations with liquidity needs, concentration concerns, and sensitivity to volatility.

During the conversation, the client wants clarity and reassurance quickly, but the situation requires judgment. There is a visible trade-off between growth, capital protection, and liquidity planning. The RM must respond with empathy, align to house view, explain the rationale behind portfolio positioning, and suggest practical next steps without sounding generic or product-pushy.
""".strip()


def demo_evaluation(
    rm_answer: str,
    house_view: dict,
    persona: str,
    engagement: str,
) -> dict[str, Any]:
    text = rm_answer.strip()

    low_effort_reason = low_effort_response_reason(text)
    originality_score, originality_reason = local_originality_score(text)

    if low_effort_reason:
        return {
            "score": 18,
            "house_view_alignment": "Fail",
            "empathy_score": 20,
            "prudence_score": 20,
            "clarity_score": 20,
            "originality_score": max(10, originality_score),
            "feedback": (
                f"The response is too weak to be treated as a valid RM recommendation. "
                f"{low_effort_reason} A credible RM answer should acknowledge the client context, "
                f"show suitability thinking, and provide clear next steps."
            ),
            "recommendation_summary": (
                "Write a fuller recommendation with empathy, allocation logic, risk control, "
                "and specific action steps."
            ),
            "strengths": [],
            "improvements": [
                "Expand the answer meaningfully.",
                "Address the client’s goals and concerns.",
                "Give a practical, phased recommendation.",
                "Reference the firm house view explicitly.",
            ],
        }

    empathy_score = detect_empathy_score(text)
    prudence_score = detect_prudence_score(text)
    clarity_score = detect_structure_score(text)
    personalization_score = detect_personalization_score(text, persona, engagement)

    house_alignment, house_score, house_strengths, house_issues = evaluate_house_view_alignment(text, house_view)

    generic_phrases = [
        "please invest according to your risk profile",
        "a diversified portfolio is important",
        "you should invest carefully",
        "we can create a balanced portfolio",
        "it is important to stay invested",
    ]
    generic_hits = count_hits(text, generic_phrases)

    if generic_hits >= 2:
        clarity_score -= 8
        personalization_score -= 10

    if word_count(text) < 45:
        clarity_score -= 8
        prudence_score -= 6

    if word_count(text) > 90:
        clarity_score += 3

    empathy_score = max(20, min(95, empathy_score))
    prudence_score = max(20, min(95, prudence_score))
    clarity_score = max(20, min(95, clarity_score))
    personalization_score = max(20, min(95, personalization_score))

    overall_score = round(
        (0.24 * empathy_score)
        + (0.27 * prudence_score)
        + (0.20 * clarity_score)
        + (0.15 * personalization_score)
        + (0.14 * house_score)
    )

    strengths: list[str] = []
    improvements: list[str] = []

    if empathy_score >= 75:
        strengths.append("Shows empathy and acknowledges the client’s emotional and practical concerns.")
    else:
        improvements.append("Acknowledge the client’s concerns, goals, or liquidity needs more explicitly.")

    if prudence_score >= 75:
        strengths.append("Demonstrates suitability, diversification, and risk-awareness.")
    else:
        improvements.append("Strengthen suitability language with diversification, risk control, and phased deployment.")

    if clarity_score >= 75:
        strengths.append("Recommendation is reasonably structured and actionable.")
    else:
        improvements.append("Use a clearer structure such as current situation, recommendation, and next steps.")

    if personalization_score >= 70:
        strengths.append("Advice is reasonably tailored to the selected persona and engagement context.")
    else:
        improvements.append("Tailor the answer more directly to the chosen client persona and engagement type.")

    if house_alignment == "Pass":
        strengths.extend(house_strengths[:2] if house_strengths else ["Directionally aligned with current house view."])
    else:
        improvements.extend(house_issues[:2] if house_issues else ["Make the recommendation more explicitly aligned to house view."])

    if originality_score < 50:
        improvements.append("Reduce generic template language and make the response more natural and specific.")

    if not strengths:
        strengths.append("The response attempts to engage with the client situation.")
    if not improvements:
        improvements.append("Add more precision to the implementation plan and review checkpoints.")

    feedback = (
        f"Persona reviewed: {extract_persona_name(persona)} | Engagement: {engagement}. "
        f"This response was scored across empathy, prudence, clarity, personalization, originality, and house-view alignment. "
        f"Strengths: {' '.join(strengths)} "
        f"Areas to improve: {' '.join(improvements)} "
        f"Originality note: {originality_reason}"
    )

    recommendation_summary = (
        "Lead with the client concern, tie the advice to suitability and house view, "
        "and end with a phased action plan plus a review schedule."
    )

    return {
        "score": int(max(5, min(95, overall_score))),
        "house_view_alignment": house_alignment,
        "empathy_score": int(empathy_score),
        "prudence_score": int(prudence_score),
        "clarity_score": int(clarity_score),
        "originality_score": int(originality_score),
        "feedback": feedback,
        "recommendation_summary": recommendation_summary,
        "strengths": strengths,
        "improvements": improvements,
    }


def build_case_study(provider: str, persona: str, engagement: str, house_view: dict) -> tuple[str | None, str | None]:
    if provider == "Demo":
        return demo_case_study(persona, engagement, house_view), None

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
        return generate_text(provider, prompt, require_json=False), None
    except Exception as exc:
        return None, friendly_provider_error(provider, exc)


def evaluate_response(
    provider: str,
    case_study: str,
    excel_summary: str,
    rm_answer: str,
    house_view: dict,
    persona: str,
    engagement: str,
) -> dict[str, Any]:
    if provider == "Demo":
        return demo_evaluation(rm_answer, house_view, persona, engagement)

    originality_score, _ = local_originality_score(rm_answer)

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
        raw = generate_text(provider, prompt, require_json=True)
        return safe_json_loads(
            raw,
            {
                "score": 0,
                "house_view_alignment": "Fail",
                "empathy_score": 0,
                "prudence_score": 0,
                "clarity_score": 0,
                "feedback": f"Could not parse evaluation response. Raw output: {raw}",
                "recommendation_summary": "Evaluation unavailable.",
            },
        )
    except Exception as exc:
        return {
            "score": 0,
            "house_view_alignment": "Fail",
            "empathy_score": 0,
            "prudence_score": 0,
            "clarity_score": 0,
            "feedback": friendly_provider_error(provider, exc),
            "recommendation_summary": "Evaluation unavailable.",
        }


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


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("<div class='brand-title'>scripbox</div>", unsafe_allow_html=True)
        st.markdown("<div class='brand-subtitle'>RM Case Study · RM Capability Engine</div>", unsafe_allow_html=True)
        st.markdown("---")

        options = ["Demo", "OpenAI", "Gemini"]
        default_index = options.index(DEFAULT_PROVIDER) if DEFAULT_PROVIDER in options else 0

        st.markdown("### ⚙️ Engine Settings")
        provider = st.radio("Select AI Provider", options, index=default_index)

        st.markdown(
            """
            <div class="hint-box">
            <b>Best experience:</b> use <b>Demo</b> to validate the full learning flow.<br>
            Then switch to <b>OpenAI</b> or <b>Gemini</b> once the API key and quota are ready.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(f"### 🏅 Level {st.session_state.level} RM")
        st.write(f"Total XP: {st.session_state.xp}")

        progress = (st.session_state.xp % 500) / 500
        st.markdown(
            f"""
            <div class="xp-shell">
                <div class="xp-fill" style="width:{progress * 100:.0f}%"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='small-muted'>500 XP per level</div>", unsafe_allow_html=True)

        if st.session_state.level >= 3:
            st.markdown("<div class='badge'>Trusted Advisor</div>", unsafe_allow_html=True)

    return provider


def render_app_header() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{APP_NAME}</div>
            <div class="hero-subtitle">
                {APP_SUBTITLE} — practice realistic RM conversations, align to house view,
                and improve recommendation quality through structured evaluation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_house_view() -> None:
    st.subheader("Firm Strategy & House View")
    st.caption("Set the investment stance that recommendations should follow.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Equity")
        for item in ["Large Cap", "Mid Cap", "Small Cap"]:
            current = st.session_state.house_view["Equity"][item]
            st.session_state.house_view["Equity"][item] = st.selectbox(
                item,
                ["Bullish", "Neutral", "Bearish"],
                index=["Bullish", "Neutral", "Bearish"].index(current),
                key=f"equity_{item}",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 🏛️ Debt")
        for item in ["Accrual", "Duration", "Credit"]:
            current = st.session_state.house_view["Debt"][item]
            st.session_state.house_view["Debt"][item] = st.selectbox(
                item,
                ["Bullish", "Neutral", "Bearish"],
                index=["Bullish", "Neutral", "Bearish"].index(current),
                key=f"debt_{item}",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 🪙 Commodities")
        for item in ["Gold", "Silver"]:
            current = st.session_state.house_view["Commodities"][item]
            st.session_state.house_view["Commodities"][item] = st.selectbox(
                item,
                ["Bullish", "Neutral", "Bearish"],
                index=["Bullish", "Neutral", "Bearish"].index(current),
                key=f"commodity_{item}",
            )
        st.markdown("</div>", unsafe_allow_html=True)


def render_simulation(provider: str) -> None:
    st.subheader("Client Simulation")
    st.caption("Design a case, respond like an RM, and review structured feedback.")

    with st.expander("📝 1. Design the Scenario", expanded=True):
        col1, col2, col3 = st.columns([1.0, 1.8, 1.2])

        with col1:
            age_group = st.selectbox("Client Age Profile", list(PERSONAS.keys()))

        with col2:
            persona = st.selectbox("Specific Persona", PERSONAS[age_group])

        with col3:
            engagement = st.selectbox("Engagement Type", ENGAGEMENT_TYPES)

        if st.button("Generate Case Study"):
            with st.spinner(f"Generating case study with {provider}..."):
                case_text, error_text = build_case_study(
                    provider=provider,
                    persona=persona,
                    engagement=engagement,
                    house_view=st.session_state.house_view,
                )
                st.session_state.active_case = case_text
                st.session_state.active_persona = persona
                st.session_state.active_engagement = engagement
                st.session_state.case_error = error_text

    if st.session_state.case_error:
        st.error(st.session_state.case_error)
        return

    if st.session_state.active_case:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("### 💼 Active Case Study")
        st.write(st.session_state.active_case)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 2. Submit RM Advice")
        st.caption("Be empathetic, suitable, clear, and aligned to the current house view.")

        uploaded_file = st.file_uploader(
            "Optional: Upload client cashflow workbook (.xlsx)",
            type=["xlsx"],
        )

        excel_summary = "No Excel workbook provided."
        if uploaded_file is not None:
            excel_summary = summarize_excel(uploaded_file)
            if excel_summary.startswith("Excel parsing failed:"):
                st.error(excel_summary)
            else:
                try:
                    uploaded_file.seek(0)
                    xls = pd.ExcelFile(uploaded_file)
                    preview_df = pd.read_excel(xls, sheet_name=xls.sheet_names[0]).head(8)
                    st.dataframe(preview_df, use_container_width=True)
                except Exception:
                    pass

        rm_answer = st.text_area(
            "Your RM response",
            height=260,
            placeholder=(
                "Write as if you are speaking to the client.\n\n"
                "Suggested structure:\n"
                "1. Acknowledge the client concern or goal\n"
                "2. Give your recommendation aligned to house view\n"
                "3. Explain why\n"
                "4. Suggest next steps / phased action plan"
            ),
        )

        wc = word_count(rm_answer)
        st.caption(f"Word count: {wc} | Better evaluation usually starts at 50+ words.")

        if st.button("Submit to Senior RM Review"):
            if not rm_answer.strip():
                st.warning("Please enter your RM response first.")
                return

            low_effort_reason = low_effort_response_reason(rm_answer)
            if low_effort_reason and word_count(rm_answer) < 20:
                st.warning(
                    "This response is too weak to evaluate as an RM recommendation. "
                    "Please provide a fuller answer with empathy, suitability, and next steps."
                )
                return

            originality_score, originality_reason = local_originality_score(rm_answer)

            with st.spinner("Reviewing response..."):
                evaluation = evaluate_response(
                    provider=provider,
                    case_study=st.session_state.active_case,
                    excel_summary=excel_summary,
                    rm_answer=rm_answer,
                    house_view=st.session_state.house_view,
                    persona=st.session_state.active_persona or "",
                    engagement=st.session_state.active_engagement or "",
                )

            score = int(evaluation.get("score", 0))
            alignment = str(evaluation.get("house_view_alignment", "Fail"))
            empathy = int(evaluation.get("empathy_score", 0))
            prudence = int(evaluation.get("prudence_score", 0))
            clarity = int(evaluation.get("clarity_score", 0))

            xp_gained = calculate_xp(score, originality_score, alignment)

            st.session_state.xp += xp_gained
            st.session_state.level = (st.session_state.xp // 500) + 1

            st.session_state.history.append(
                {
                    "Persona": extract_persona_name(st.session_state.active_persona or ""),
                    "Engagement": st.session_state.active_engagement or "",
                    "Provider": provider,
                    "Score": score,
                    "Alignment": alignment,
                    "Originality": originality_score,
                    "XP Gained": xp_gained,
                }
            )

            st.markdown("---")
            st.markdown("### Senior RM Feedback")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown("<div class='score-card'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>Capability Score</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>{score}/100</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown("<div class='score-card'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>House View</div>", unsafe_allow_html=True)
                pill = "ok-pill" if alignment.lower() == "pass" else "warn-pill"
                st.markdown(f"<span class='{pill}'>{alignment}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with c3:
                st.markdown("<div class='score-card'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>Originality</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>{originality_score}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with c4:
                st.markdown("<div class='score-card'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>XP Earned</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>+{xp_gained}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            d1, d2, d3 = st.columns(3)
            d1.metric("Empathy", empathy)
            d2.metric("Prudence", prudence)
            d3.metric("Clarity", clarity)

            strengths = evaluation.get("strengths", [])
            improvements = evaluation.get("improvements", [])

            left, right = st.columns(2)
            with left:
                st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
                st.markdown("#### What worked")
                for item in strengths:
                    st.write(f"• {item}")
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
                st.markdown("#### What to improve")
                for item in improvements:
                    st.write(f"• {item}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='feedback-box'>", unsafe_allow_html=True)
            st.markdown("#### Detailed Feedback")
            st.write(str(evaluation.get("feedback", "No feedback available.")))
            st.markdown("</div>", unsafe_allow_html=True)

            st.caption(f"Originality note: {originality_reason}")
            st.caption(f"Improvement summary: {evaluation.get('recommendation_summary', 'N/A')}")


def render_analytics() -> None:
    st.subheader("Performance Analytics")
    st.caption("Track learning progress, quality, and consistency over time.")

    if not st.session_state.history:
        st.info("Complete at least one simulation to unlock analytics.")
        return

    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Average Score", round(df["Score"].mean(), 1))
    c2.metric("Average Originality", round(df["Originality"].mean(), 1))
    c3.metric(
        "Pass Rate",
        f"{round((df['Alignment'].str.lower().eq('pass').mean()) * 100, 1)}%",
    )

    st.bar_chart(df[["Persona", "Score"]].copy().set_index("Persona"))
    st.bar_chart(df[["Persona", "XP Gained"]].copy().set_index("Persona"))


def main() -> None:
    init_state()
    provider = render_sidebar()

    render_app_header()

    tab1, tab2, tab3 = st.tabs(["House View", "Simulation", "Analytics"])

    with tab1:
        render_house_view()

    with tab2:
        render_simulation(provider)

    with tab3:
        render_analytics()


if __name__ == "__main__":
    main()
