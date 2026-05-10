import logging

import httpx

from src.config import get_api_key, get_provider_config
from src.llm_client import LLMClient, SpeakerAnalysis, UtteranceRef
from src.providers.base import OpenAICompatibleClient

logger = logging.getLogger(__name__)


class AliyunClient(LLMClient):
    def __init__(self, model: str | None = None) -> None:
        config = get_provider_config("aliyun")
        self.api_key = get_api_key("aliyun")
        self._inner = OpenAICompatibleClient(
            base_url=config["chat_base_url"],
            api_key=self.api_key,
            model=model or config["default_model"],
        )
        self.embedding_base_url = config.get("embedding_base_url", "")
        self.embedding_endpoint = config.get("embedding_endpoint", "/text-embedding")

    def analyze_speaker(
        self,
        focus_speaker_id: str,
        full_transcript: list[UtteranceRef],
        previous_profile: dict | None = None,
    ) -> SpeakerAnalysis:
        return self._inner.analyze_speaker(focus_speaker_id, full_transcript, previous_profile)

    @property
    def client(self):
        return self._inner.client

    @property
    def model(self) -> str:
        return self._inner.model

    def embed(self, texts: list[str], model: str = "text-embedding-v2") -> list[list[float]]:
        url = f"{self.embedding_base_url}{self.embedding_endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "input": {"texts": texts},
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["output"]["embeddings"]]
