from src.config import settings
from src.llm_client import LLMClient, SpeakerAnalysis, UtteranceRef
from src.providers.base import OpenAICompatibleClient


class OpenAIClient(LLMClient):
    def __init__(self) -> None:
        self._inner = OpenAICompatibleClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model="gpt-4o-mini",
        )

    def analyze_speaker(
        self,
        focus_speaker_id: str,
        full_transcript: list[UtteranceRef],
        previous_profile: dict | None = None,
    ) -> SpeakerAnalysis:
        return self._inner.analyze_speaker(focus_speaker_id, full_transcript, previous_profile)
