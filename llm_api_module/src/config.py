from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "minimax"
    llm_base_url: str = ""
    llm_api_key: str = ""
    kimi_api_key: str = ""
    aliyun_api_key: str = ""
    minimax_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

LLM_CONFIG_PATH = Path(__file__).parent.parent / "llm_config.yaml"


def load_llm_config() -> dict:
    with open(LLM_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_llm_config(config: dict) -> None:
    with open(LLM_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)


def get_provider_config(provider: str | None = None) -> dict:
    config = load_llm_config()
    provider = provider or config.get("active_provider", settings.llm_provider)
    providers = config.get("providers", {})
    if provider not in providers:
        raise ValueError(f"Unknown LLM provider: {provider}. Available: {list(providers.keys())}")
    return providers[provider]


def get_selected_model(provider: str | None = None) -> str | None:
    config = load_llm_config()
    active = config.get("active_provider", settings.llm_provider)
    if provider and provider != active:
        return None
    return config.get("selected_model")


def set_selected_model(provider: str, model: str) -> None:
    config = load_llm_config()
    config["selected_model"] = model
    save_llm_config(config)


def set_active_provider(provider: str) -> None:
    config = load_llm_config()
    config["active_provider"] = provider
    save_llm_config(config)


def set_api_key(provider: str, api_key: str) -> None:
    config = load_llm_config()
    if "providers" not in config:
        config["providers"] = {}
    if provider not in config["providers"]:
        config["providers"][provider] = {}
    config["providers"][provider]["api_key"] = api_key
    save_llm_config(config)


def get_api_key(provider: str) -> str:
    try:
        config = load_llm_config()
        provider_config = config.get("providers", {}).get(provider, {})
        yaml_key = provider_config.get("api_key", "")
        if yaml_key:
            return yaml_key
    except Exception:
        pass

    key_map = {
        "kimi": settings.kimi_api_key,
        "aliyun": settings.aliyun_api_key,
        "minimax": settings.minimax_api_key,
    }
    key = key_map.get(provider, "")
    if not key:
        env_var = f"{provider.upper()}_API_KEY"
        raise ValueError(f"No API key for provider: {provider}. Set {env_var} in .env")
    return key
