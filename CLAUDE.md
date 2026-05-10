# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

- **Python**: 3.14+
- **Package**: fin2605-analysis-agent
- **Type**: Single package project (no workspace/monorepo)

## Python Version Policy

This project targets Python 3.14+. Ensure any code contributions are compatible with this version.

## Package Structure

The package name is `fin2605-analysis-agent`. When adding source code, follow standard Python packaging conventions with `src/` layout or a flat package structure depending on project needs.

## LangChain Architecture

The project uses LangChain for agent orchestration with three layers:

### Tools (`src/fin2605_analysis_agent/tools/`)
Low-level functions decorated with `@tool`. Each tool performs a single task:
- `web_search.py`: `search_stock_news`, `get_market_sentiment`
- `database.py`: `query_market_data`, `query_technical_indicators`

### Skills (`src/fin2605_analysis_agent/skills/`)
Composable workflow units that combine tools + LLM. Skills link to each other:
- `NewsResearchSkill`: Uses web search tools + LLM for news analysis
- `MarketDataSkill`: Uses database tools + LLM for technical analysis
- `StockAnalysisReportSkill`: Links NewsResearchSkill + MarketDataSkill + LLM for full reports

### Agent (`src/fin2605_analysis_agent/agents/stock_agent.py`)
Orchestrates tools and skills. Provides three modes:
- **agent**: ReAct agent where LLM decides tool usage
- **skill**: Direct skill invocation
- **report**: Full skill chain with linked skills

## API Key Configuration

API keys are stored in `.env` (NEVER commit to git). The stock agent uses `MINIMAX_API_KEY` with LangChain's `ChatOpenAI` (OpenAI-compatible endpoint at `https://api.minimax.chat/v1`).

## Dependency Management

Dependencies should be added to `pyproject.toml` under `[project].dependencies`. Avoid adding unnecessary dependencies.

## Working pattern
Keep documentation of new/updated code in `documentations/` folder after each implementation, following the file naming conventions outlined in `documentations/0_documentation_requirements.md`.
