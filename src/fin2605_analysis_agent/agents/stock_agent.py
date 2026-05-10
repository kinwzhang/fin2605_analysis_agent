"""Stock analysis agent with tool binding and skill orchestration."""
import os
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from fin2605_analysis_agent.tools.web_search import search_stock_news, get_market_sentiment
from fin2605_analysis_agent.tools.database import query_market_data, query_technical_indicators
from fin2605_analysis_agent.skills.news_research import create_news_research_skill
from fin2605_analysis_agent.skills.market_data import create_market_data_skill
from fin2605_analysis_agent.skills.stock_report import create_stock_report_skill


def create_stock_analysis_agent():
    """Create a stock analysis agent with tools and skills.

    This demonstrates:
    - Tool binding: Direct LLM access to tools
    - Skill creation: Composable workflow units
    - Skill linking: Skills that call other skills

    Returns:
        Configured agent with tools and skills
    """
    # Get API key from environment
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        raise ValueError("MINIMAX_API_KEY not set in environment")

    # Initialize LLM with MiniMax OpenAI-compatible endpoint
    llm = ChatOpenAI(
        model="MiniMax-M2.7",
        api_key=api_key,
        base_url="https://api.minimax.chat/v1",
    )

    # Bind tools directly to LLM (tool binding pattern)
    tools = [search_stock_news, get_market_sentiment, query_market_data, query_technical_indicators]

    # Create skills (composable workflow units)
    news_skill = create_news_research_skill(llm)
    market_skill = create_market_data_skill(llm)
    report_skill = create_stock_report_skill(news_skill, market_skill, llm)

    # Create ReAct agent with tool binding
    agent = create_react_agent(llm, tools)

    return {
        "agent": agent,
        "llm": llm,
        "tools": tools,
        "skills": {
            "news": news_skill,
            "market": market_skill,
            "report": report_skill,
        },
    }


def run_stock_analysis(agent_config: dict, symbol: str, mode: Literal["agent", "skill", "report"] = "report"):
    """Run stock analysis in different modes.

    Args:
        agent_config: Configuration from create_stock_analysis_agent
        symbol: Stock ticker symbol
        mode: "agent" - uses ReAct agent with tool calling
              "skill" - uses individual skill
              "report" - uses full report skill chain

    Returns:
        Analysis result
    """
    if mode == "agent":
        # Agent mode: LLM decides which tools to call
        agent = agent_config["agent"]
        messages = [
            SystemMessage(content=f"""You are a stock analysis expert. Analyze {symbol} by:
1. First search for news and sentiment using the web search tools
2. Then query market data and technical indicators from the database
3. Provide a comprehensive analysis"""),
            HumanMessage(content=f"Analyze stock {symbol}"),
        ]
        result = agent.invoke({"messages": messages})
        return result["messages"][-1].content

    elif mode == "skill":
        # Skill mode: Direct skill invocation
        news_skill = agent_config["skills"]["news"]
        return news_skill.research(symbol)

    else:  # mode == "report"
        # Report mode: Full workflow with linked skills
        report_skill = agent_config["skills"]["report"]
        return report_skill.generate_report(symbol)


if __name__ == "__main__":
    config = create_stock_analysis_agent()

    print("=== Agent Mode (LLM decides tool usage) ===")
    print(run_stock_analysis(config, "AAPL", mode="agent"))

    print("\n=== Skill Mode (Direct skill call) ===")
    print(run_stock_analysis(config, "AAPL", mode="skill"))

    print("\n=== Report Mode (Full skill chain) ===")
    print(run_stock_analysis(config, "AAPL", mode="report"))