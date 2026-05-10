import logging

import httpx

from src.config import get_api_key, get_provider_config

logger = logging.getLogger(__name__)

LIST_MODELS_PATHS: dict[str, str] = {
    "kimi": "/models",
    "aliyun": "https://dashscope.aliyuncs.com/api/v1/deployments/models",
}


def _get_base_url(provider: str) -> str:
    config = get_provider_config(provider)
    return config.get("base_url", config.get("chat_base_url", ""))


def list_models(provider: str) -> list[str]:
    if provider not in LIST_MODELS_PATHS:
        return []

    api_key = get_api_key(provider)
    path = LIST_MODELS_PATHS.get(provider, "/v1/models")
    url = path if path.startswith("http") else f"{_get_base_url(provider)}{path}"

    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        resp = httpx.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict) and "data" in data:
            return [m.get("id", m.get("model", "")) for m in data["data"]]
        if isinstance(data, dict) and "models" in data:
            return [m.get("id", m.get("model", "")) for m in data["models"]]
        if isinstance(data, list):
            return [m.get("id", m.get("model", "")) for m in data]

        logger.warning("Unexpected model list format from %s", provider)
        return []
    except Exception:
        logger.exception("Failed to list models for provider %s", provider)
        return []


def validate_model(provider: str, model: str) -> str:
    available = list_models(provider)

    if not available:
        logger.warning(
            "Could not fetch model list for %s, using configured model: %s",
            provider,
            model,
        )
        return model

    if model in available:
        return model

    config = get_provider_config(provider)
    fallback = config.get("default_model", "")
    logger.warning(
        "Model '%s' not available from %s. Available: %s. Falling back to: %s",
        model,
        provider,
        available[:5],
        fallback,
    )
    return fallback
