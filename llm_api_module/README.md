# LLM API Module — Portable Multi-Provider LLM Client

A clean, extractable Python module for interacting with multiple LLM providers
through a unified interface. Originally extracted from the PersonaTrace project.

## Architecture

```
llm_api_module/
├── pyproject.toml              # Dependencies (openai, httpx, pydantic-settings, pyyaml)
├── .env.example                # Template for API keys
├── llm_config.yaml             # Provider definitions (URLs, models, defaults)
└── src/
    ├── __init__.py              # Re-exports: LLMClient, SpeakerAnalysis, UtteranceRef, get_llm_client
    ├── llm_client.py            # Core ABC + dataclasses (the contract)
    ├── config.py                # Settings + YAML config management
    └── providers/
        ├── __init__.py          # Factory: get_llm_client(provider, model)
        ├── base.py              # OpenAICompatibleClient + prompt builder + JSON parser
        ├── kimi.py              # Kimi (Moonshot) provider wrapper
        ├── aliyun.py            # Aliyun (DashScope) provider + embeddings
        ├── minimax.py           # MiniMax (OpenAI + Anthropic-style endpoints)
        ├── openai_legacy.py     # Generic OpenAI-compatible provider
        ├── checker.py           # list_models() / validate_model() for each provider
        └── sync.py              # sync_all_models() — update llm_config.yaml from APIs
```

### Data Flow

```
Your code
  └─ get_llm_client("kimi")
       └─ KimiClient ─┐
                       ├─ OpenAICompatibleClient  ← uses OpenAI SDK
                       │    ├─ _build_prompt()    ← constructs analysis prompt
                       │    ├─ OpenAI(api_key, base_url).chat.completions.create()
                       │    └─ _parse_response()  ← extracts JSON, resolves references
                       │
AliyunClient ──────────┤
  └─ embed() ── httpx  │                          ← direct HTTP for embeddings
                       │
MiniMaxClient ─────────┘
MiniMaxAnthropicClient ── httpx                    ← Anthropic-style HTTP endpoint
OpenAIClient ────────────── OpenAI SDK             ← generic OpenAI-compatible
```

## Supported Providers & Endpoints

| Provider | Base URL | Chat Endpoint | Auth | Notes |
|---|---|---|---|---|
| **Kimi** | `https://api.moonshot.cn/v1` | `/chat/completions` | `Bearer {api_key}` | Full OpenAI-compatible |
| **Aliyun** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `/chat/completions` | `Bearer {api_key}` | Also has `/text-embedding` endpoint |
| **MiniMax** | `https://api.minimax.chat/v1` | `/text/chatcompletion_v2` | `Bearer {api_key}` | Two client variants: OpenAI-compat + Anthropic-style |
| **OpenAI** | configurable via env | `/chat/completions` | `Bearer {api_key}` | Generic, works with any OpenAI-compatible API |

## Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Copy and configure
cp .env.example .env
# Edit .env with your API keys

# 3. Use the client
python -c "
from src import get_llm_client
client = get_llm_client('kimi')
print(f'Using model: {client.model}')
"
```

### Basic Usage

```python
from src import get_llm_client, UtteranceRef
from src.providers.checker import list_models

# List available models
models = list_models("kimi")
print(f"Kimi models: {models}")

# Create a client
client = get_llm_client("kimi", model="kimi-k2.5")

# Build a transcript
transcript = [
    UtteranceRef(
        transcript_id="tr_1",
        utterance_id=1,
        anonymized_speaker_id="sp_001",
        content="I think we should go with option A",
    ),
    UtteranceRef(
        transcript_id="tr_1",
        utterance_id=2,
        anonymized_speaker_id="sp_002",
        content="What about the risks with option A?",
    ),
]

# Analyze a speaker
analysis = client.analyze_speaker(
    focus_speaker_id="sp_001",
    full_transcript=transcript,
)

print(f"Communication style: {analysis.communication_style}")
print(f"Behavioral traits: {analysis.behavioral_traits}")
```

### Using with the OpenAI SDK Directly

Each provider client exposes the underlying `client` property for direct OpenAI SDK
access when you need it:

```python
client = get_llm_client("minimax")
response = client.client.chat.completions.create(
    model=client.model,
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Ali Cloud Embeddings

```python
client = get_llm_client("aliyun")
embeddings = client.embed(
    texts=["Hello world", "Another text"],
    model="text-embedding-v2",
)
```

## Configuration

### 1. Environment variables (`.env`)

```ini
LLM_PROVIDER=minimax           # Default provider name
MINIMAX_API_KEY=mk-xxxx        # Provider API key
KIMI_API_KEY=sk-xxxx
ALIYUN_API_KEY=sk-xxxx
```

### 2. YAML config (`llm_config.yaml`)

Defines per-provider settings: base URLs, available models, default model, and
optional API key (takes precedence over `.env`). Keys are looked up in this order:

1. `llm_config.yaml` → `providers.<name>.api_key`
2. `.env` environment variable → `<NAME>_API_KEY`

### Runtime switching

```python
# Switch provider at runtime
client = get_llm_client("aliyun", model="qwen-max")
```

## How to Reuse in Other Projects

### Option A: Copy the module (recommended)

```bash
cp -r llm_api_module /path/to/your/project/
```

Add these dependencies to your `pyproject.toml`:

```toml
dependencies = [
    "openai>=1.12.0",
    "httpx>=0.27.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0.0",
]
```

### Option B: Install as a sub-package

```bash
pip install -e ./llm_api_module
```

Then in your code:

```python
from llm_api_module import get_llm_client
```

### Customizing the Prompt

To change the analysis prompt for your domain:

1. Edit `SYSTEM_PROMPT` in `src/providers/base.py`
2. Edit `_build_prompt()` in the same file — this builds the user message

The prompt is designed for behavioral analysis but can be adapted to any
domain (e.g., code review, sentiment analysis, question answering).

### Using Just the OpenAI-Compatible Client

If you only need one provider, you can bypass the factory entirely:

```python
from src.providers.base import OpenAICompatibleClient

client = OpenAICompatibleClient(
    base_url="https://api.moonshot.cn/v1",
    api_key="sk-...",
    model="moonshot-v1-8k",
)
```

### Adding a New Provider

1. Create `src/providers/new_provider.py`
2. Implement `LLMClient` (wrap `OpenAICompatibleClient` or use raw `httpx`)
3. Add to `_CLIENTS` dict in `src/providers/__init__.py`
4. Add provider config to `llm_config.yaml`

Example:

```python
# src/providers/new_provider.py
from src.config import get_api_key, get_provider_config
from src.llm_client import LLMClient, SpeakerAnalysis, UtteranceRef
from src.providers.base import OpenAICompatibleClient


class NewProviderClient(LLMClient):
    def __init__(self, model: str | None = None) -> None:
        config = get_provider_config("new_provider")
        self._inner = OpenAICompatibleClient(
            base_url=config["base_url"],
            api_key=get_api_key("new_provider"),
            model=model or config["default_model"],
        )

    def analyze_speaker(self, focus_speaker_id, full_transcript, previous_profile=None):
        return self._inner.analyze_speaker(
            focus_speaker_id, full_transcript, previous_profile
        )
```

## File Reference

| File | Responsibility | Extractable |
|---|---|---|
| `src/llm_client.py` | **ABC + dataclasses** — the interface contract. Zero dependencies beyond stdlib. | Fully portable |
| `src/config.py` | **Settings + YAML I/O** — env-driven config with `pydantic-settings`. | Fully portable |
| `src/providers/base.py` | **Core implementation** — `OpenAICompatibleClient`, prompt builder, JSON parser, UID resolver. | Fully portable |
| `src/providers/kimi.py` | **Kimi wrapper** — thin delegation to `OpenAICompatibleClient`. | Fully portable |
| `src/providers/aliyun.py` | **Aliyun wrapper** + embedding support via raw `httpx`. | Fully portable |
| `src/providers/minimax.py` | **MiniMax** — OpenAI-compat + Anthropic-style endpoint. | Fully portable |
| `src/providers/openai_legacy.py` | **Generic OpenAI** — uses env vars for base URL. | Fully portable |
| `src/providers/checker.py` | **Model availability** — `list_models()` / `validate_model()` via HTTP GET. | Fully portable |
| `src/providers/sync.py` | **Model sync** — fetches models from APIs, updates `llm_config.yaml`. | Fully portable |
| `llm_config.yaml` | **Provider registry** — URLs, models, defaults. | Edit to add/remove providers |
| `.env.example` | **Template** — shows required env vars. | Edit to match your needs |
