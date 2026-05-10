"""PostgreSQL database tool for market data."""
from langchain_core.tools import tool


@tool
def query_market_data(symbol: str, start_date: str, end_date: str) -> str:
    """Query historical market data from PostgreSQL database.

    Args:
        symbol: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        OHLCV data and technical indicators
    """
    # Simulated database response - replace with actual psycopg2 query
    mock_data = {
        "AAPL": {
            "dates": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "open": [185.50, 186.20, 185.80],
            "high": [187.50, 187.00, 186.50],
            "low": [185.00, 185.50, 185.00],
            "close": [186.80, 185.90, 186.20],
            "volume": [45000000, 42000000, 48000000],
        },
        "GOOGL": {
            "dates": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "open": [140.50, 141.20, 140.80],
            "high": [142.50, 142.00, 141.50],
            "low": [140.00, 140.50, 140.00],
            "close": [141.80, 140.90, 141.20],
            "volume": [25000000, 22000000, 28000000],
        },
    }

    data = mock_data.get(symbol, {})
    if not data:
        return f"No data found for {symbol} in range {start_date} to {end_date}"

    return f"""
{symbol} Market Data ({start_date} to {end_date}):
- Latest Close: ${data['close'][-1]:.2f}
- Latest Volume: {data['volume'][-1]:,}
- Price Change: ${data['close'][-1] - data['close'][0]:.2f} ({((data['close'][-1] - data['close'][0]) / data['close'][0] * 100):.2f}%)
"""


@tool
def query_technical_indicators(symbol: str) -> str:
    """Query technical indicators from PostgreSQL database.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Technical indicators (RSI, MACD, Bollinger Bands, etc.)
    """
    # Simulated technical indicators
    return f"""
{symbol} Technical Indicators:
- RSI(14): 58.5 (Neutral zone)
- MACD: 1.2 (Bullish crossover)
- MA(50): $185.00
- MA(200): $178.50
- Bollinger Upper: $190.00, Lower: $180.00
"""