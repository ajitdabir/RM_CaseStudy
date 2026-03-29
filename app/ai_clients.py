from __future__ import annotations

from typing import Literal

from google import genai
from openai import OpenAI

from app.config import AppConfig

Provider = Literal["OpenAI", "Gemini"]


class AIClientError(RuntimeError):
    pass


class AIQuotaError(AIClientError):
    pass


class LLMGateway:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def generate_text(
        self,
        provider: Provider,
        prompt: str,
        require_json: bool = False,
        temperature: float = 0.4,
    ) -> str:
        if require_json:
            prompt = (
                f"{prompt}\n\n"
                "Return strictly valid JSON only. "
                "Do not include markdown fences or explanations."
            )

        if provider == "OpenAI":
            return self._openai_text(prompt=prompt, temperature=temperature)

        if provider == "Gemini":
            return self._gemini_text(prompt=prompt)

        raise AIClientError(f"Unsupported provider: {provider}")

    def _openai_text(self, prompt: str, temperature: float) -> str:
        if not self.config.openai_api_key:
            raise AIClientError("OPENAI_API_KEY is missing.")

        try:
            client = OpenAI(api_key=self.config.openai_api_key)
            response = client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:
            raise AIClientError(f"OpenAI request failed: {exc}") from exc

    def _gemini_text(self, prompt: str) -> str:
        if not self.config.gemini_api_key:
            raise AIClientError("GEMINI_API_KEY is missing.")

        try:
            client = genai.Client(api_key=self.config.gemini_api_key)
            response = client.models.generate_content(
                model=self.config.gemini_model,
                contents=prompt,
            )

            text = getattr(response, "text", None)
            if text:
                return text

            candidates = getattr(response, "candidates", None)
            if candidates:
                try:
                    parts = candidates[0].content.parts
                    return "".join(getattr(p, "text", "") for p in parts)
                except Exception:
                    pass

            return ""
        except Exception as exc:
            msg = str(exc)
            upper_msg = msg.upper()

            if "429" in upper_msg or "RESOURCE_EXHAUSTED" in upper_msg or "QUOTA" in upper_msg:
                raise AIQuotaError(
                    "Gemini quota exhausted. Switch provider to OpenAI or use a Gemini key with available quota."
                ) from exc

            raise AIClientError(f"Gemini request failed: {exc}") from exc