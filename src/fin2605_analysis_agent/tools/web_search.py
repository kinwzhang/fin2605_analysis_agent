"""Web search tool for fetching stock news."""
from langchain_core.tools import tool


@tool
def search_stock_news(symbol: str) -> str:
    """Search for recent news about a stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL)

    Returns:
        Recent news articles and sentiment for the symbol
    """
    # Simulated web search result - replace with actual API call
    news_data = {
        "AAPL": [
            {"headline": "Apple reports record Q2 earnings", "sentiment": "positive"},
            {"headline": "iPhone sales surge in emerging markets", "sentiment": "positive"},
        ],
        "GOOGL": [
            {"headline": "Google Cloud revenue grows 28%", "sentiment": "positive"},
            {"headline": "AI investments impact margins", "sentiment": "neutral"},
        ],
    }
    articles = news_data.get(symbol, [{"headline": f"No recent news for {symbol}", "sentiment": "unknown"}])
    return str(articles)


@tool
def get_market_sentiment(symbol: str) -> str:
    """Analyze market sentiment for a stock from social media and news.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Sentiment analysis summary
    """
    # Simulated sentiment analysis
    return f"Sentiment for {symbol}: Bullish - positive momentum detected"