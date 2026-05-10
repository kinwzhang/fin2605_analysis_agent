"""Skill: Analyze market data and technical indicators."""
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool

from fin2605_analysis_agent.tools.database import query_market_data, query_technical_indicators


class MarketDataSkill:
    """Analyzes market data and technical indicators."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools: list[Tool] = [query_market_data, query_technical_indicators]

    def analyze(self, symbol: str, start_date: str = "2024-01-01", end_date: str = "2024-12-31") -> str:
        """Analyze market data for a stock symbol.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            Technical analysis with trading signals
        """
        # Step 1: Get market data
        market_data = query_market_data.invoke({"symbol": symbol, "start_date": start_date, "end_date": end_date})

        # Step 2: Get technical indicators
        indicators = query_technical_indicators.invoke(symbol)

        # Step 3: LLM analysis
        messages = [
            SystemMessage(content="You are a technical analysis expert. Analyze market data and provide trading insights."),
            HumanMessage(content=f"Market Data:\n{market_data}\n\nTechnical Indicators:\n{indicators}\n\nProvide buy/sell/hold recommendation with technical justification."),
        ]

        response = self.llm.invoke(messages)
        return response.content


def create_market_data_skill(llm: BaseChatModel) -> MarketDataSkill:
    """Factory function to create MarketDataSkill."""
    return MarketDataSkill(llm)