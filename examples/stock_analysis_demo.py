"""Example demonstrating agent, skill, and tool interactions.

This script shows how:
1. Tools are bound to an LLM for tool-calling
2. Skills compose multiple tools into workflow units
3. Skills can link to other skills (StockAnalysisReportSkill uses NewsResearchSkill + MarketDataSkill)
"""
from fin2605_analysis_agent.agents.stock_agent import create_stock_analysis_agent, run_stock_analysis


def main():
    # Create agent - reads MINIMAX_API_KEY from environment
    try:
        config = create_stock_analysis_agent()
    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure MINIMAX_API_KEY is set in .env")
        return

    print("=" * 60)
    print("STOCK ANALYSIS AGENT DEMONSTRATION")
    print("=" * 60)

    symbol = "AAPL"

    print("\n--- Tool Binding ---")
    print("Tools bound to LLM:", [t.name for t in config["tools"]])

    print("\n--- Skill Composition ---")
    print("Skills available:")
    for name, skill in config["skills"].items():
        tool_names = [t.name for t in skill.tools]
        print(f"  {name}: uses tools {tool_names}")

    print("\n--- Skill Linking ---")
    print("StockAnalysisReportSkill links NewsResearchSkill + MarketDataSkill")

    print("\n" + "=" * 60)
    print("RUNNING ANALYSIS")
    print("=" * 60)

    # Mode 1: Agent - LLM decides which tools to use
    print("\n[Mode: Agent (ReAct with tool calling)]")
    print("-" * 40)
    result = run_stock_analysis(config, symbol, mode="agent")
    print(result)

    # Mode 2: Skill - Direct skill usage
    print("\n[Mode: Skill (Direct skill call)]")
    print("-" * 40)
    result = run_stock_analysis(config, symbol, mode="skill")
    print(result)

    # Mode 3: Report - Linked skills
    print("\n[Mode: Report (Skill chain)]")
    print("-" * 40)
    result = run_stock_analysis(config, symbol, mode="report")
    print(result)


if __name__ == "__main__":
    main()