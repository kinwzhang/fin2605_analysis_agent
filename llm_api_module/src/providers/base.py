import json
import logging

from openai import OpenAI

from src.llm_client import LLMClient, SpeakerAnalysis, UtteranceRef

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a behavioral analyst specializing in communication patterns. "
    "Analyze the target speaker objectively using the full conversational "
    "context. Always cite specific utterance IDs as evidence. "
    "Respond only with valid JSON."
)


def _build_prompt(
    focus_speaker_id: str,
    full_transcript: list[UtteranceRef],
    previous_profile: dict | None = None,
) -> str:
    transcript_lines = [
        f"[ID:{u.transcript_id}:{u.utterance_id}] {u.anonymized_speaker_id}: {u.content}"
        for u in full_transcript
    ]
    transcript_text = "\n".join(transcript_lines)

    prompt = (
        f"You are analyzing a conversation transcript to profile the speaker "
        f"identified as {focus_speaker_id}.\n\n"
        f"The transcript includes multiple speakers. Focus your analysis on "
        f"{focus_speaker_id}, but use the full context to understand:\n"
        f"- How {focus_speaker_id} responds to questions or topics raised by others\n"
        f"- How {focus_speaker_id} asks questions and what they probe into\n"
        f"- How {focus_speaker_id} reacts to answers, disagreements, or suggestions\n"
        f"- Patterns in {focus_speaker_id}'s decision-making and communication\n\n"
        f"Transcript:\n{transcript_text}\n\n"
    )

    if previous_profile:
        prev_summary = (
            f"Previous profile summary (use as context but refine based on new transcript):\n"
            f"- Communication Style: {previous_profile.get('communication_style', 'N/A')}\n"
            f"- Behavioral Traits: {previous_profile.get('behavioral_traits', 'N/A')}\n"
            f"- Preferences: {previous_profile.get('preferences', 'N/A')}\n"
            f"- Interaction Strategy: {previous_profile.get('interaction_strategy', 'N/A')}\n\n"
        )
        prompt += prev_summary

    prompt += (
        f"Respond in JSON format with these fields:\n"
        f"- communication_style: describe how {focus_speaker_id} communicates\n"
        f"- behavioral_traits: key behavioral traits observed in {focus_speaker_id}\n"
        f"- preferences: communication and decision preferences of {focus_speaker_id}\n"
        f"- interaction_strategy: practical advice on working with {focus_speaker_id}\n"
        f"- references: for each field above, array of objects with "
        f'"utterance_id" (integer) and "reason" (string).\n\n'
        f"Example:\n"
        f'{{"communication_style": "...", "behavioral_traits": "...", '
        f'"preferences": "...", "interaction_strategy": "...", '
        f'"references": {{"communication_style": [{{"utterance_id": 1, "reason": "..."}}, ...], '
        f'"behavioral_traits": [...], "preferences": [...], "interaction_strategy": [...]}}}}'
    )
    return prompt


def _resolve_uid(raw_uid: object) -> tuple[str, int] | None:
    if isinstance(raw_uid, (list, tuple)) and len(raw_uid) == 2:
        try:
            return (str(raw_uid[0]), int(raw_uid[1]))
        except (ValueError, TypeError):
            pass
    if isinstance(raw_uid, int):
        return ("", raw_uid)
    if isinstance(raw_uid, str):
        if ":" in raw_uid:
            parts = raw_uid.rsplit(":", 1)
            if len(parts) == 2:
                try:
                    return (parts[0], int(parts[1]))
                except ValueError:
                    pass
        try:
            return ("", int(raw_uid))
        except ValueError:
            pass
        parts = raw_uid.rsplit("_", 1)
        if len(parts) == 2:
            try:
                return ("", int(parts[1]))
            except ValueError:
                pass
    return None


def _extract_json(content: str) -> str:
    end_tag = "</think>"
    idx = content.find(end_tag)
    if idx != -1:
        after = content[idx + len(end_tag) :]
        start = after.find("{")
        end = after.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = after[start : end + 1]
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

    end = content.rfind("}")
    while end != -1:
        depth = 0
        start = end
        while start >= 0:
            if content[start] == "}":
                depth += 1
            elif content[start] == "{":
                depth -= 1
            if depth == 0:
                candidate = content[start : end + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    break
            start -= 1
        end = content.rfind("}", 0, end)
    return content


def _parse_response(content: str, full_transcript: list[UtteranceRef]) -> SpeakerAnalysis:
    extracted = _extract_json(content)
    data = json.loads(extracted)

    utterance_lookup: dict[tuple[str, int], UtteranceRef] = {
        (u.transcript_id, u.utterance_id): u for u in full_transcript
    }

    references: dict[str, list[UtteranceRef]] = {}
    raw_refs = data.get("references", {})
    fields = [
        "communication_style",
        "behavioral_traits",
        "preferences",
        "interaction_strategy",
    ]
    for field_name in fields:
        refs_for_field: list[UtteranceRef] = []
        for ref in raw_refs.get(field_name, []):
            key = _resolve_uid(ref.get("utterance_id"))
            if key is not None and key in utterance_lookup:
                refs_for_field.append(utterance_lookup[key])
        references[field_name] = refs_for_field

    return SpeakerAnalysis(
        communication_style=data.get("communication_style", ""),
        behavioral_traits=data.get("behavioral_traits", ""),
        preferences=data.get("preferences", ""),
        interaction_strategy=data.get("interaction_strategy", ""),
        references=references,
    )


class OpenAICompatibleClient(LLMClient):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def analyze_speaker(
        self,
        focus_speaker_id: str,
        full_transcript: list[UtteranceRef],
        previous_profile: dict | None = None,
    ) -> SpeakerAnalysis:
        prompt = _build_prompt(focus_speaker_id, full_transcript, previous_profile)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        return _parse_response(content, full_transcript)
