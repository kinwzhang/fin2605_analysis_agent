# LangChain Agent Setup Guide

## Overview

This project uses LangChain for agent orchestration with three layers: **Tools**, **Skills**, and **Agents**.

## Architecture

```
Agent (orchestration)
  └── Skills (workflow units)
        └── Tools (low-level functions)
```

### Tools (`tools/`)
Low-level `@tool` decorated functions. Each performs a single task:
- `web_search.py`: `search_stock_news`, `get_market_sentiment`
- `database.py`: `query_market_data`, `query_technical_indicators`

### Skills (`skills/`)
Composable workflow units combining tools + LLM. Skills can link to each other:
- `NewsResearchSkill`: Web search tools → LLM news analysis
- `MarketDataSkill`: Database tools → LLM technical analysis
- `StockAnalysisReportSkill`: Links NewsResearch + MarketData → Full report

### Agent (`agents/stock_agent.py`)
Orchestrates tools and skills with three execution modes:
- **agent**: ReAct agent where LLM decides tool usage
- **skill**: Direct skill invocation
- **report**: Full skill chain

## Running the Demo

```bash
# Set API key in .env (already created, replace with real key)
# MINIMAX_API_KEY=your-key

# Install dependencies
pip install -e ".[dev]"

# Run demo
python examples/stock_analysis_demo.py
```

## API Key Configuration

**NEVER commit API keys to git.**

Create `.env` at project root (already set up):
```
MINIMAX_API_KEY=your-minimax-key-here
KIMI_API_KEY=your-kimi-key-here
ALIYUN_API_KEY=your-aliyun-key-here
LLM_PROVIDER=minimax
```

The stock agent uses `MINIMAX_API_KEY` with LangChain's `ChatOpenAI` (OpenAI-compatible endpoint).

## LLM API Module Structure

The `llm_api_module/` provides OpenAI-compatible LLM clients:

```
llm_api_module/
├── src/
│   ├── config.py          # Settings (.env loading), provider config
│   ├── llm_client.py       # Base LLMClient, OpenAICompatibleClient
│   └── providers/
│       ├── base.py         # OpenAICompatibleClient (reusable)
│       ├── minimax.py      # MiniMaxClient
│       ├── kimi.py         # KimiClient
│       └── aliyun.py       # AliyunClient
├── llm_config.yaml        # Provider endpoints, models, api_key placeholders
├── .env.example           # Environment variable template
└── README.md
```

Use `get_llm_client(provider, model)` to get an LLM client instance.