import logging

import httpx

from src.config import get_api_key, get_provider_config
from src.llm_client import LLMClient, SpeakerAnalysis, UtteranceRef
from src.providers.base import (
    SYSTEM_PROMPT,
    OpenAICompatibleClient,
    _build_prompt,
    _parse_response,
)

logger = logging.getLogger(__name__)


class MiniMaxClient(LLMClient):
    """MiniMax client using OpenAI-compatible endpoint."""

    def __init__(self, model: str | None = None) -> None:
        config = get_provider_config("minimax")
        self._inner = OpenAICompatibleClient(
            base_url=config.get("openai_base_url", config["base_url"]),
            api_key=get_api_key("minimax"),
            model=model or config["default_model"],
        )

    @property
    def client(self):
        return self._inner.client

    @property
    def model(self) -> str:
        return self._inner.model

    def analyze_speaker(
        self,
        focus_speaker_id: str,
        full_transcript: list[UtteranceRef],
        previous_profile: dict | None = None,
    ) -> SpeakerAnalysis:
        return self._inner.analyze_speaker(focus_speaker_id, full_transcript, previous_profile)


class MiniMaxAnthropicClient(LLMClient):
    """MiniMax client using Anthropic-style endpoint. Kept for future use."""

    def __init__(self) -> None:
        config = get_provider_config("minimax")
        self.api_key = get_api_key("minimax")
        self.base_url = config["base_url"]
        self.chat_endpoint = config.get("chat_endpoint", "/text/chatcompletion_v2")
        self.model = config["default_model"]

    def analyze_speaker(
        self,
        focus_speaker_id: str,
        full_transcript: list[UtteranceRef],
        previous_profile: dict | None = None,
    ) -> SpeakerAnalysis:
        prompt = _build_prompt(focus_speaker_id, full_transcript, previous_profile)

        url = f"{self.base_url}{self.chat_endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "reply_constraints": {"reply_format": "json"},
        }

        resp = httpx.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        content = self._extract_reply(data)
        return _parse_response(content, full_transcript)

    def _extract_reply(self, data: dict) -> str:
        if "reply" in data:
            return data["reply"]
        if "choices" in data and data["choices"]:
            msg = data["choices"][0].get("message", {})
            return msg.get("content", "{}")
        return "{}"
