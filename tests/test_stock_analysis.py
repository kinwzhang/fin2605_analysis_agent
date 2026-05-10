"""Tests for stock analysis components."""
import pytest
from unittest.mock import MagicMock

from fin2605_analysis_agent.tools.web_search import search_stock_news, get_market_sentiment
from fin2605_analysis_agent.tools.database import query_market_data, query_technical_indicators
from fin2605_analysis_agent.skills.news_research import create_news_research_skill
from fin2605_analysis_agent.skills.market_data import create_market_data_skill


class TestTools:
    """Test individual tools."""

    def test_search_stock_news_aapl(self):
        result = search_stock_news.invoke("AAPL")
        assert "Apple" in result
        assert "positive" in result

    def test_search_stock_news_unknown(self):
        result = search_stock_news.invoke("UNKNOWN")
        assert "No recent news" in result

    def test_get_market_sentiment(self):
        result = get_market_sentiment.invoke("AAPL")
        assert "Sentiment" in result
        assert "Bullish" in result

    def test_query_market_data(self):
        result = query_market_data.invoke({"symbol": "AAPL", "start_date": "2024-01-01", "end_date": "2024-12-31"})
        assert "AAPL" in result
        assert "Market Data" in result

    def test_query_technical_indicators(self):
        result = query_technical_indicators.invoke("AAPL")
        assert "RSI" in result
        assert "MACD" in result


class TestSkills:
    """Test skill composition."""

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content="Mock LLM response")
        return llm

    def test_news_research_skill(self, mock_llm):
        skill = create_news_research_skill(mock_llm)
        result = skill.research("AAPL")
        assert "Mock LLM response" in result
        # Verify LLM was called with proper context
        mock_llm.invoke.assert_called_once()

    def test_market_data_skill(self, mock_llm):
        skill = create_market_data_skill(mock_llm)
        result = skill.analyze("AAPL")
        assert "Mock LLM response" in result
        mock_llm.invoke.assert_called_once()

    def test_skill_uses_tools(self, mock_llm):
        skill = create_news_research_skill(mock_llm)
        # Skills should have tools bound to them
        assert len(skill.tools) == 2  # search_stock_news, get_market_sentiment