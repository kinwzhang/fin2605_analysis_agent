"""Skill: Generate comprehensive stock analysis report."""
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from fin2605_analysis_agent.skills.news_research import NewsResearchSkill
from fin2605_analysis_agent.skills.market_data import MarketDataSkill


class StockAnalysisReportSkill:
    """Combines news research and market data into a comprehensive report."""

    def __init__(self, news_skill: NewsResearchSkill, market_skill: MarketDataSkill, llm: BaseChatModel):
        self.news_skill = news_skill
        self.market_skill = market_skill
        self.llm = llm

    def generate_report(self, symbol: str, start_date: str = "2024-01-01", end_date: str = "2024-12-31") -> str:
        """Generate comprehensive stock analysis report.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date for market data
            end_date: End date for market data

        Returns:
            Comprehensive analysis report
        """
        # Step 1: Gather news and sentiment
        news_analysis = self.news_skill.research(symbol)

        # Step 2: Analyze market data
        market_analysis = self.market_skill.analyze(symbol, start_date, end_date)

        # Step 3: Generate final report
        messages = [
            SystemMessage(content="You are a senior financial analyst creating comprehensive stock reports."),
            HumanMessage(content=f"""
Create a comprehensive stock analysis report for {symbol} combining:

NEWS RESEARCH:
{news_analysis}

MARKET DATA ANALYSIS:
{market_analysis}

Provide a complete report with:
1. Executive Summary
2. Fundamental Analysis
3. Technical Analysis
4. Sentiment Analysis
5. Investment Recommendation
"""),
        ]

        response = self.llm.invoke(messages)
        return response.content


def create_stock_report_skill(
    news_skill: NewsResearchSkill,
    market_skill: MarketDataSkill,
    llm: BaseChatModel
) -> StockAnalysisReportSkill:
    """Factory function to create StockAnalysisReportSkill."""
    return StockAnalysisReportSkill(news_skill, market_skill, llm)