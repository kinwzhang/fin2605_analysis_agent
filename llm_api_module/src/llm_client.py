from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class UtteranceRef:
    transcript_id: str
    utterance_id: int
    anonymized_speaker_id: str
    content: str


@dataclass
class SpeakerAnalysis:
    communication_style: str
    behavioral_traits: str
    preferences: str
    interaction_strategy: str
    references: dict[str, list[UtteranceRef]] = field(default_factory=dict)


class LLMClient(ABC):
    @abstractmethod
    def analyze_speaker(
        self,
        focus_speaker_id: str,
        full_transcript: list[UtteranceRef],
        previous_profile: dict | None = None,
    ) -> SpeakerAnalysis: ...
