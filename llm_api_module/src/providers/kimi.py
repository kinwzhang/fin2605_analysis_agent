from src.config import get_api_key, get_provider_config
from src.llm_client import LLMClient, SpeakerAnalysis, UtteranceRef
from src.providers.base import OpenAICompatibleClient


class KimiClient(LLMClient):
    def __init__(self, model: str | None = None) -> None:
        config = get_provider_config("kimi")
        self._inner = OpenAICompatibleClient(
            base_url=config["base_url"],
            api_key=get_api_key("kimi"),
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
