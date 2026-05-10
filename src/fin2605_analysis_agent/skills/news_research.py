"""Skill: Research stock news and sentiment."""
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool

from fin2605_analysis_agent.tools.web_search import search_stock_news, get_market_sentiment


class NewsResearchSkill:
    """Gathers and analyzes stock-related news and sentiment."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools: list[Tool] = [search_stock_news, get_market_sentiment]

    def research(self, symbol: str) -> str:
        """Research news for a stock symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Consolidated news and sentiment analysis
        """
        # Step 1: Search for news
        news_result = search_stock_news.invoke(symbol)

        # Step 2: Get sentiment
        sentiment_result = get_market_sentiment.invoke(symbol)

        # Step 3: Synthesize with LLM
        messages = [
            SystemMessage(content="You are a financial analyst synthesizing stock research."),
            HumanMessage(content=f"Analyze this stock news and sentiment data:\n\nNews:\n{news_result}\n\nSentiment:\n{sentiment_result}\n\nProvide a concise summary with key insights."),
        ]

        response = self.llm.invoke(messages)
        return response.content


def create_news_research_skill(llm: BaseChatModel) -> NewsResearchSkill:
    """Factory function to create NewsResearchSkill."""
    return NewsResearchSkill(llm)