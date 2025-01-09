# Original imports - keep these
import mcp.types as types
import mcp.server.stdio

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server

# Add our new imports
from .data import MarketData
from .indicators import TechnicalAnalysis

# Replace the notes dictionary with our service instances
market_data = MarketData()
tech_analysis = TechnicalAnalysis()

# Keep the server initialization
server = Server("mcp-trader")

# We can remove the list_resources and read_resource handlers
# since we're not using them yet

# Remove the list_prompts and get_prompt handlers
# We'll focus on tools for now


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List our stock analysis tools."""
    return [
        types.Tool(
            name="analyze-stock",
            description="Analyze a stock's technical setup",
            inputSchema={
                "type": "object",
                "properties": {"symbol": {"type": "string", "description": "Stock symbol (e.g., NVDA)"}},
                "required": ["symbol"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    if name != "analyze-stock":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    symbol = arguments.get("symbol")
    if not symbol:
        raise ValueError("Missing symbol")

    try:
        # Fetch data
        df = await market_data.get_historical_data(symbol)

        # Add indicators
        df = tech_analysis.add_core_indicators(df)

        # Get trend status
        trend = tech_analysis.check_trend_status(df)

        analysis = f"""
Technical Analysis for {symbol}:

Trend Analysis:
- Above 20 SMA: {'✅' if trend['above_20sma'] else '❌'}
- Above 50 SMA: {'✅' if trend['above_50sma'] else '❌'}
- Above 200 SMA: {'✅' if trend['above_200sma'] else '❌'}
- 20/50 SMA Bullish Cross: {'✅' if trend['20_50_bullish'] else '❌'}
- 50/200 SMA Bullish Cross: {'✅' if trend['50_200_bullish'] else '❌'}

Momentum:
- RSI (14): {trend['rsi']:.2f}
- MACD Bullish: {'✅' if trend['macd_bullish'] else '❌'}

Latest Price: ${df['close'].iloc[-1]:.2f}
Average True Range (14): {df['atr'].iloc[-1]:.2f}
Average Daily Range Percentage: {df['adrp'].iloc[-1]:.2f}%
Average Volume (20D): {df['avg_20d_vol'].iloc[-1]}
"""

        return [types.TextContent(type="text", text=analysis)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"\n<observation>\nError: {str(e)}\n</observation>\n")]


# Keep the main function as is
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-trader",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
