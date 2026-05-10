import logging
import re

import httpx
import yaml

from src.config import LLM_CONFIG_PATH
from src.providers.checker import list_models

logger = logging.getLogger(__name__)

MINIMAX_MODELS_URL = "https://platform.minimaxi.com/docs/api-reference/api-overview"

MINIMAX_TEXT_MODELS = [
    "MiniMax-M2.7",
    "MiniMax-M2.7-highspeed",
    "MiniMax-M2.5",
    "MiniMax-M2.5-highspeed",
    "MiniMax-M2.1",
    "MiniMax-M2.1-highspeed",
    "MiniMax-M2",
]


def _load_config() -> dict:
    with open(LLM_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_config(config: dict) -> None:
    with open(LLM_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _sync_provider_models(provider: str) -> list[str]:
    if provider == "minimax":
        return _sync_minimax_models()
    return list_models(provider)


def _sync_minimax_models() -> list[str]:
    try:
        resp = httpx.get(MINIMAX_MODELS_URL, timeout=15)
        resp.raise_for_status()
        text = resp.text

        pattern = r"MiniMax-M[\d][\w.-]*"
        found = sorted(set(re.findall(pattern, text)))

        chat_models = [m for m in found if re.match(r"^MiniMax-M[12](\.\d+)?(-\w+)?$", m)]

        if chat_models:
            logger.info("MiniMax models from web: %s", chat_models)
            return chat_models
    except Exception:
        logger.exception("Failed to scrape MiniMax models page")

    logger.info("Using hardcoded MiniMax models")
    return MINIMAX_TEXT_MODELS


def sync_all_models() -> dict[str, list[str]]:
    config = _load_config()
    providers = config.get("providers", {})
    result: dict[str, list[str]] = {}

    for provider in providers:
        models = _sync_provider_models(provider)
        if models:
            providers[provider]["models"] = models
            result[provider] = models
            logger.info("Synced %d models for %s", len(models), provider)

    _save_config(config)
    return result


def sync_provider(provider: str) -> list[str]:
    config = _load_config()
    providers = config.get("providers", {})

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")

    models = _sync_provider_models(provider)
    if models:
        providers[provider]["models"] = models
        _save_config(config)
        logger.info("Synced %d models for %s", len(models), provider)

    return models
