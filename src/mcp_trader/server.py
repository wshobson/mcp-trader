import mcp.types as types
import mcp.server.stdio
import asyncio

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server

# Add our new imports
from .data import MarketData
from .indicators import (
    TechnicalAnalysis,
    RelativeStrength,
    VolumeProfile,
    PatternRecognition,
    RiskAnalysis,
)

# Initialize our service instances
market_data = MarketData()
tech_analysis = TechnicalAnalysis()
rs_analysis = RelativeStrength()
volume_analysis = VolumeProfile()
pattern_recognition = PatternRecognition()
risk_analysis = RiskAnalysis()

# Keep the server initialization
server = Server("mcp-trader")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List our stock analysis tools."""
    return [
        types.Tool(
            name="analyze-stock",
            description="Analyze a stock's technical setup",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., NVDA)",
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="relative-strength",
            description="Calculate a stock's relative strength compared to benchmark",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol to analyze",
                    },
                    "benchmark": {
                        "type": "string",
                        "description": "Benchmark symbol (default: SPY)",
                        "default": "SPY",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="volume-profile",
            description="Analyze volume distribution by price",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol to analyze",
                    },
                    "lookback_days": {
                        "type": "integer",
                        "description": "Number of days to analyze",
                        "default": 60,
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="detect-patterns",
            description="Detect chart patterns in price data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol to analyze",
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="position-size",
            description="Calculate optimal position size based on risk parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "price": {
                        "type": "number",
                        "description": "Entry price (0 for current price)",
                    },
                    "stop_price": {"type": "number", "description": "Stop loss price"},
                    "risk_amount": {
                        "type": "number",
                        "description": "Dollar amount to risk",
                    },
                    "account_size": {
                        "type": "number",
                        "description": "Total account size in dollars",
                    },
                },
                "required": ["symbol", "stop_price", "risk_amount", "account_size"],
            },
        ),
        types.Tool(
            name="suggest-stops",
            description="Suggest stop loss levels based on technical analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol to analyze",
                    }
                },
                "required": ["symbol"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    if not arguments:
        raise ValueError("Missing arguments")

    try:
        # Original analyze-stock tool
        if name == "analyze-stock":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Missing symbol")

            # Fetch data
            df = await market_data.get_historical_data(symbol)

            # Add indicators
            df = tech_analysis.add_core_indicators(df)

            # Get trend status
            trend = tech_analysis.check_trend_status(df)

            analysis = f"""
Technical Analysis for {symbol}:

Trend Analysis:
- Above 20 SMA: {"✅ " if trend["above_20sma"] else "❌ "}
- Above 50 SMA: {"✅ " if trend["above_50sma"] else "❌ "}
- Above 200 SMA: {"✅ " if trend["above_200sma"] else "❌ "}
- 20/50 SMA Bullish Cross: {"✅ " if trend["20_50_bullish"] else "❌ "}
- 50/200 SMA Bullish Cross: {"✅ " if trend["50_200_bullish"] else "❌ "}

Momentum:
- RSI (14): {trend["rsi"]:.2f}
- MACD Bullish: {"✅ " if trend["macd_bullish"] else "❌ "}

Latest Price: ${df["close"].iloc[-1]:.2f}
Average True Range (14): {df["atr"].iloc[-1]:.2f}
Average Daily Range Percentage: {df["adrp"].iloc[-1]:.2f}%
Average Volume (20D): {int(df["avg_20d_vol"].iloc[-1])}
"""

            return [types.TextContent(type="text", text=analysis)]

        # Relative Strength Analysis
        elif name == "relative-strength":
            symbol = arguments.get("symbol")
            benchmark = arguments.get("benchmark", "SPY")

            if not symbol:
                raise ValueError("Missing symbol")

            # Calculate relative strength
            rs_results = await rs_analysis.calculate_rs(market_data, symbol, benchmark)

            # Format the results
            rs_text = f"""
Relative Strength Analysis for {symbol} vs {benchmark}:

"""
            # Check if we have any results
            if not rs_results:
                rs_text += "Insufficient historical data to calculate relative strength metrics."
                return [types.TextContent(type="text", text=rs_text)]

            for period, score in rs_results.items():
                if period.startswith("RS_"):
                    days = period.split("_")[1]
                    rs_text += f"- {days} Relative Strength: {score}"

                    # Add classification
                    if score >= 80:
                        rs_text += " (Strong Outperformance) ⭐⭐⭐"
                    elif score >= 65:
                        rs_text += " (Moderate Outperformance) ⭐⭐"
                    elif score >= 50:
                        rs_text += " (Slight Outperformance) ⭐"
                    elif score >= 35:
                        rs_text += " (Slight Underperformance) ⚠️"
                    elif score >= 20:
                        rs_text += " (Moderate Underperformance) ⚠️⚠️"
                    else:
                        rs_text += " (Strong Underperformance) ⚠️⚠️⚠️"

                    rs_text += "\n"

            rs_text += "\nPerformance Details:\n"

            for period in ["21d", "63d", "126d", "252d"]:
                # Check if we have data for this period
                if (
                    f"Return_{period}" not in rs_results
                    or f"Benchmark_{period}" not in rs_results
                    or f"Excess_{period}" not in rs_results
                ):
                    continue

                stock_return = rs_results.get(f"Return_{period}")
                benchmark_return = rs_results.get(f"Benchmark_{period}")
                excess = rs_results.get(f"Excess_{period}")

                if (
                    stock_return is not None
                    and benchmark_return is not None
                    and excess is not None
                ):
                    rs_text += f"- {period}: {symbol} {stock_return:+.2f}% vs {benchmark} {benchmark_return:+.2f}% = {excess:+.2f}%\n"

            # If no performance details were added
            if "\nPerformance Details:\n" == rs_text.split("\n")[-2] + "\n":
                rs_text += "No performance details available due to insufficient historical data.\n"

            return [types.TextContent(type="text", text=rs_text)]

        # Volume Profile Analysis
        elif name == "volume-profile":
            symbol = arguments.get("symbol")
            lookback_days = arguments.get("lookback_days", 60)

            if not symbol:
                raise ValueError("Missing symbol")

            # Get historical data
            df = await market_data.get_historical_data(symbol, lookback_days + 10)

            # Analyze volume profile
            profile = volume_analysis.analyze_volume_profile(df.tail(lookback_days))

            # Format the results
            profile_text = f"""
Volume Profile Analysis for {symbol} (last {lookback_days} days):

Point of Control (POC): ${profile["point_of_control"]} (Price level with highest volume)
Value Area: ${profile["value_area_low"]} - ${profile["value_area_high"]} (70% of volume)

Volume by Price Level (High to Low):
"""

            # Sort bins by volume and format
            sorted_bins = sorted(
                profile["bins"], key=lambda x: x["volume"], reverse=True
            )
            for i, bin_data in enumerate(sorted_bins[:5]):  # Show top 5 volume levels
                profile_text += f"{i + 1}. ${bin_data['price_low']} - ${bin_data['price_high']}: {bin_data['volume_percent']:.1f}% of volume\n"

            return [types.TextContent(type="text", text=profile_text)]

        # Pattern Recognition
        elif name == "detect-patterns":
            symbol = arguments.get("symbol")

            if not symbol:
                raise ValueError("Missing symbol")

            # Get historical data
            df = await market_data.get_historical_data(symbol, lookback_days=90)

            # Detect patterns
            pattern_results = pattern_recognition.detect_patterns(df)

            # Format the results
            if not pattern_results["patterns"]:
                pattern_text = f"No significant chart patterns detected for {symbol} in the recent data."
            else:
                pattern_text = f"Chart Patterns Detected for {symbol}:\n\n"

                for pattern in pattern_results["patterns"]:
                    pattern_text += f"- {pattern['type']}"

                    if "start_date" in pattern and "end_date" in pattern:
                        pattern_text += (
                            f" ({pattern['start_date']} to {pattern['end_date']})"
                        )

                    pattern_text += f": Price level ${pattern['price_level']}"

                    if "confidence" in pattern:
                        pattern_text += f" (Confidence: {pattern['confidence']})"

                    pattern_text += "\n"

                pattern_text += "\nNote: Pattern recognition is not 100% reliable and should be confirmed with other forms of analysis."

            return [types.TextContent(type="text", text=pattern_text)]

        # Position Sizing
        elif name == "position-size":
            symbol = arguments.get("symbol")
            price = arguments.get("price", 0)
            stop_price = arguments.get("stop_price")
            risk_amount = arguments.get("risk_amount")
            account_size = arguments.get("account_size")

            if not all([symbol, stop_price, risk_amount, account_size]):
                raise ValueError("Missing required parameters")

            # If price is 0, get the current price
            if price == 0:
                df = await market_data.get_historical_data(symbol, lookback_days=5)
                price = df["close"].iloc[-1]

            # Calculate position size
            position_results = risk_analysis.calculate_position_size(
                price=price,
                stop_price=stop_price,
                risk_amount=risk_amount,
                account_size=account_size,
            )

            # Format the results
            position_text = f"""
Position Sizing for {symbol} at ${price:.2f}:

📊 Recommended Position:
- {position_results["recommended_shares"]} shares (${position_results["position_cost"]:.2f})
- Risk: ${position_results["dollar_risk"]:.2f} ({position_results["account_percent_risked"]:.2f}% of account)
- Risk per share: ${position_results["risk_per_share"]:.2f}

🎯 Potential Targets (R-Multiples):
- R1 (1:1): ${position_results["r_multiples"]["r1"]:.2f}
- R2 (2:1): ${position_results["r_multiples"]["r2"]:.2f}
- R3 (3:1): ${position_results["r_multiples"]["r3"]:.2f}

Remember what Ramada said: "Good trades don't just happen, they're the result of careful planning!"
"""

            return [types.TextContent(type="text", text=position_text)]

        # Suggest Stop Levels
        elif name == "suggest-stops":
            symbol = arguments.get("symbol")

            if not symbol:
                raise ValueError("Missing symbol")

            # Get historical data
            df = await market_data.get_historical_data(symbol, lookback_days=60)

            # Add indicators
            df = tech_analysis.add_core_indicators(df)

            # Get stop suggestions
            stops = risk_analysis.suggest_stop_levels(df)

            latest_close = df["close"].iloc[-1]

            # Format the results
            stops_text = f"""
Suggested Stop Levels for {symbol} (Current Price: ${latest_close:.2f}):

ATR-Based Stops:
- Conservative (1x ATR): ${stops["atr_1x"]:.2f} ({((latest_close - stops["atr_1x"]) / latest_close * 100):.2f}% from current price)
- Moderate (2x ATR): ${stops["atr_2x"]:.2f} ({((latest_close - stops["atr_2x"]) / latest_close * 100):.2f}% from current price)
- Aggressive (3x ATR): ${stops["atr_3x"]:.2f} ({((latest_close - stops["atr_3x"]) / latest_close * 100):.2f}% from current price)

Percentage-Based Stops:
- Tight (2%): ${stops["percent_2"]:.2f}
- Medium (5%): ${stops["percent_5"]:.2f}
- Wide (8%): ${stops["percent_8"]:.2f}

Technical Levels:
"""

            if "sma_20" in stops:
                stops_text += f"- 20-day SMA: ${stops['sma_20']:.2f} ({((latest_close - stops['sma_20']) / latest_close * 100):.2f}% from current price)\n"

            if "sma_50" in stops:
                stops_text += f"- 50-day SMA: ${stops['sma_50']:.2f} ({((latest_close - stops['sma_50']) / latest_close * 100):.2f}% from current price)\n"

            if "sma_200" in stops:
                stops_text += f"- 200-day SMA: ${stops['sma_200']:.2f} ({((latest_close - stops['sma_200']) / latest_close * 100):.2f}% from current price)\n"

            if "recent_swing" in stops:
                stops_text += f"- Recent Swing Low: ${stops['recent_swing']:.2f} ({((latest_close - stops['recent_swing']) / latest_close * 100):.2f}% from current price)\n"

            return [types.TextContent(type="text", text=stops_text)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"\n<observation>\nError: {str(e)}\n</observation>\n"
            )
        ]


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


# Add a standalone HTTP server for testing
async def run_http_server():
    """Run a standalone HTTP server for testing purposes."""
    from aiohttp import web

    # Initialize our data and analysis modules
    global \
        market_data, \
        tech_analysis, \
        rs_analysis, \
        pattern_recognition, \
        volume_analysis, \
        risk_analysis
    market_data = MarketData()
    tech_analysis = TechnicalAnalysis()
    rs_analysis = RelativeStrength()
    pattern_recognition = PatternRecognition()
    volume_analysis = VolumeProfile()
    risk_analysis = RiskAnalysis()

    app = web.Application()

    async def list_tools_handler(request):
        tools = await handle_list_tools()
        return web.json_response(tools)

    async def call_tool_handler(request):
        data = await request.json()
        name = data.get("name")
        arguments = data.get("arguments", {})

        result = await handle_call_tool(name, arguments)

        # Convert the result to a JSON-serializable format
        response_data = []
        for item in result:
            if item.type == "text":
                response_data.append({"type": "text", "text": item.text})
            # Add other content types as needed

        return web.json_response(response_data)

    app.router.add_get("/list-tools", list_tools_handler)
    app.router.add_post("/call-tool", call_tool_handler)

    print("Starting HTTP server on http://localhost:8000")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8000)
    await site.start()

    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run as HTTP server
        asyncio.run(run_http_server())
    else:
        # Run as MCP server
        asyncio.run(main())
