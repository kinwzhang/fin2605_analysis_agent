from src.config import settings
from src.llm_client import LLMClient
from src.providers.aliyun import AliyunClient
from src.providers.kimi import KimiClient
from src.providers.minimax import MiniMaxClient

_CLIENTS: dict[str, type[LLMClient]] = {
    "kimi": KimiClient,
    "aliyun": AliyunClient,
    "minimax": MiniMaxClient,
}


def get_llm_client(provider: str | None = None, model: str | None = None) -> LLMClient:
    from src.config import get_provider_config, get_selected_model, load_llm_config

    config = load_llm_config()
    provider = provider or config.get("active_provider", settings.llm_provider)

    if model is None:
        model = get_selected_model(provider)

    if provider == "openai":
        from src.providers.openai_legacy import OpenAIClient

        return OpenAIClient()

    client_cls = _CLIENTS.get(provider)
    if not client_cls:
        raise ValueError(f"Unknown LLM provider: {provider}. Available: {list(_CLIENTS.keys())}")
    return client_cls(model=model)
