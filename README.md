# fin2605-analysis-agent

An AI-powered stock analysis and prediction system leveraging Large Language Models for financial analysis, valuation, and price prediction.

## Project Goals

- **Stock Analysis**: LLM-based analysis of financial data and market trends
- **Stock Valuation**: Models for determining intrinsic stock value
- **Price Prediction**: AI algorithms for stock price forecasting based on technical indicators
- **Real-time Intelligence**: Web search and scraping for market news and social media sentiment
- **User Interface**: Dashboard for displaying analysis results and predictions

## Key Features

- Data collection and preprocessing tools for financial data
- LLM-based models for stock analysis and valuation
- Real-time market news and sentiment analysis via web search/scraping
- Stock price prediction algorithms using technical indicators
- Interactive UI for results display

## Tech Stack

- **Python**: 3.14+
- **AI/ML**: LLM integration, scikit-learn for technical indicators
- **Data**: pandas, numpy for data processing
- **Web**: HTTP client for market data APIs

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Lint
ruff check .
```

## Project Structure

```
fin2605_analysis_agent/
├── src/
│   └── fin2605_analysis_agent/
│       ├── __init__.py
│       └── (modules)
├── tests/
├── documentations/
├── feature_requirements/
└── pyproject.toml
```