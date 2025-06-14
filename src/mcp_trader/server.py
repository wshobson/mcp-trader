#!/usr/bin/env python3
"""
MCP Trader Server - Technical analysis and trading tools for stocks and crypto.

This server uses FastMCP for a modern, decorator-based implementation with
context-aware features like logging, progress reporting, and caching.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from fastmcp import Context, FastMCP

# Import configuration
from .config import config

# Import our modules
from .data import MarketData
from .indicators import (
    PatternRecognition,
    RelativeStrength,
    RiskAnalysis,
    TechnicalAnalysis,
    VolumeProfile,
)

load_dotenv()

# Configure logging - simple INFO level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(config.server_name)

# Initialize service instances
market_data = MarketData()
tech_analysis = TechnicalAnalysis()
rs_analysis = RelativeStrength()
volume_analysis = VolumeProfile()
pattern_recognition = PatternRecognition()
risk_analysis = RiskAnalysis()


# Context-aware helper functions
def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


async def log_request_start(ctx: Context, tool_name: str, params: dict[str, Any]) -> str:
    """Log the start of a request with context."""
    request_id = generate_request_id()
    ctx.log(f"[{request_id}] Starting {tool_name} with params: {params}")
    return request_id


async def log_request_end(
    ctx: Context, request_id: str, tool_name: str, success: bool, message: str = ""
):
    """Log the end of a request with context."""
    status = "SUCCESS" if success else "FAILED"
    ctx.log(f"[{request_id}] {tool_name} {status}{f': {message}' if message else ''}")


async def handle_error(ctx: Context, request_id: str, tool_name: str, error: Exception) -> str:
    """Handle and log errors with context."""
    error_msg = f"Error in {tool_name}: {str(error)}"
    ctx.log(f"[{request_id}] ERROR: {error_msg}", level="error")

    # Log additional error details for debugging
    if hasattr(error, "__traceback__"):
        import traceback

        tb_lines = traceback.format_tb(error.__traceback__)
        ctx.log(f"[{request_id}] Traceback: {''.join(tb_lines)}", level="debug")

    return error_msg


# Tools Implementation
@mcp.tool()
async def analyze_crypto(
    ctx: Context,
    symbol: str,
    provider: str | None = None,
    lookback_days: int = 365,
    quote_currency: str = "usd",
) -> str:
    """
    Analyze a crypto asset's technical setup (supports Tiingo and Binance).

    Args:
        symbol: Crypto symbol (e.g., BTC, ETH, BTCUSDT for Binance)
        provider: Data provider - 'tiingo' or 'binance' (default: from config)
        lookback_days: Number of days to look back (default: 365)
        quote_currency: Quote currency (default: usd for Tiingo, USDT for Binance)
    """
    # Use Tiingo as default if not specified
    if provider is None:
        provider = "tiingo"

    request_id = await log_request_start(
        ctx,
        "analyze_crypto",
        {
            "symbol": symbol,
            "provider": provider,
            "lookback_days": lookback_days,
            "quote_currency": quote_currency,
        },
    )

    try:
        # Report progress - fetching data
        ctx.report_progress(0.2, f"Fetching {symbol} data from {provider}...")
        ctx.log(f"[{request_id}] Fetching historical data for {symbol}")

        # Fetch crypto data
        df = await market_data.get_crypto_historical_data(
            symbol=symbol,
            lookback_days=lookback_days,
            provider=provider,
            quote_currency=quote_currency,
        )

        ctx.log(f"[{request_id}] Retrieved {len(df)} data points")

        # Report progress - adding indicators
        ctx.report_progress(0.5, "Calculating technical indicators...")
        ctx.log(f"[{request_id}] Adding technical indicators")

        # Add indicators
        df = tech_analysis.add_core_indicators(df)

        # Report progress - analyzing trends
        ctx.report_progress(0.8, "Analyzing trend status...")
        ctx.log(f"[{request_id}] Checking trend status")

        # Get trend status
        trend = tech_analysis.check_trend_status(df)

        # Report completion
        ctx.report_progress(1.0, "Analysis complete!")

        analysis = f"""
Technical Analysis for {symbol} ({provider.title()}):

Trend Analysis:
- Above 20 SMA: {"✅" if trend["above_20sma"] else "❌"}
- Above 50 SMA: {"✅" if trend["above_50sma"] else "❌"}
- Above 200 SMA: {"✅" if trend["above_200sma"] else "❌"}
- 20/50 SMA Bullish Cross: {"✅" if trend["20_50_bullish"] else "❌"}
- 50/200 SMA Bullish Cross: {"✅" if trend["50_200_bullish"] else "❌"}

Momentum:
- RSI (14): {trend["rsi"]:.2f}
- MACD Bullish: {"✅" if trend["macd_bullish"] else "❌"}

Latest Price: {df["close"].iloc[-1]:.6f}
Average True Range (14): {df["atr"].iloc[-1]:.6f}
Average Daily Range Percentage: {df["adrp"].iloc[-1]:.2f}%
Average Volume (20D): {df["volume"].iloc[-20:].mean():.2f}
"""

        await log_request_end(
            ctx, request_id, "analyze_crypto", True, f"Successfully analyzed {symbol}"
        )

        return analysis

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "analyze_crypto", e)
        return f"Error analyzing {symbol}: {error_msg}"


@mcp.tool()
async def analyze_stock(ctx: Context, symbol: str) -> str:
    """
    Analyze a stock's technical setup.

    Args:
        symbol: Stock symbol (e.g., NVDA)
    """

    request_id = await log_request_start(ctx, "analyze_stock", {"symbol": symbol})

    try:
        # Report progress - fetching data
        ctx.report_progress(0.2, f"Fetching {symbol} stock data...")
        ctx.log(f"[{request_id}] Fetching historical data for {symbol}")

        # Fetch data
        df = await market_data.get_historical_data(symbol)

        ctx.log(f"[{request_id}] Retrieved {len(df)} data points")

        # Report progress - adding indicators
        ctx.report_progress(0.5, "Calculating technical indicators...")
        ctx.log(f"[{request_id}] Adding technical indicators")

        # Add indicators
        df = tech_analysis.add_core_indicators(df)

        # Report progress - analyzing trends
        ctx.report_progress(0.8, "Analyzing trend status...")
        ctx.log(f"[{request_id}] Checking trend status")

        # Get trend status
        trend = tech_analysis.check_trend_status(df)

        # Report completion
        ctx.report_progress(1.0, "Analysis complete!")

        analysis = f"""
Technical Analysis for {symbol}:

Trend Analysis:
- Above 20 SMA: {"✅" if trend["above_20sma"] else "❌"}
- Above 50 SMA: {"✅" if trend["above_50sma"] else "❌"}
- Above 200 SMA: {"✅" if trend["above_200sma"] else "❌"}
- 20/50 SMA Bullish Cross: {"✅" if trend["20_50_bullish"] else "❌"}
- 50/200 SMA Bullish Cross: {"✅" if trend["50_200_bullish"] else "❌"}

Momentum:
- RSI (14): {trend["rsi"]:.2f}
- MACD Bullish: {"✅" if trend["macd_bullish"] else "❌"}

Latest Price: ${df["close"].iloc[-1]:.2f}
Average True Range (14): {df["atr"].iloc[-1]:.2f}
Average Daily Range Percentage: {df["adrp"].iloc[-1]:.2f}%
Average Volume (20D): {int(df["avg_20d_vol"].iloc[-1])}
"""

        await log_request_end(
            ctx, request_id, "analyze_stock", True, f"Successfully analyzed {symbol}"
        )

        return analysis

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "analyze_stock", e)
        return f"Error analyzing {symbol}: {error_msg}"


@mcp.tool()
async def relative_strength(ctx: Context, symbol: str, benchmark: str = "SPY") -> str:
    """
    Calculate a stock's relative strength compared to benchmark.

    Args:
        symbol: Stock symbol to analyze
        benchmark: Benchmark symbol (default: SPY)
    """
    request_id = await log_request_start(
        ctx, "relative_strength", {"symbol": symbol, "benchmark": benchmark}
    )

    try:
        # Report progress
        ctx.report_progress(0.3, f"Calculating relative strength of {symbol} vs {benchmark}...")
        ctx.log(f"[{request_id}] Starting relative strength calculation")
        # Calculate relative strength
        rs_results = await rs_analysis.calculate_rs(market_data, symbol, benchmark)

        ctx.report_progress(0.8, "Formatting results...")
        ctx.log(f"[{request_id}] Calculated RS scores for multiple periods")

        # Format the results
        rs_text = f"""
Relative Strength Analysis for {symbol} vs {benchmark}:

"""
        # Check if we have any results
        if not rs_results:
            rs_text += "Insufficient historical data to calculate relative strength metrics."
            return rs_text

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
            stock_return = rs_results.get(f"Return_{period}")
            benchmark_return = rs_results.get(f"Benchmark_{period}")
            excess = rs_results.get(f"Excess_{period}")

            if all(x is not None for x in [stock_return, benchmark_return, excess]):
                rs_text += f"- {period}: {symbol} {stock_return:+.2f}% vs {benchmark} {benchmark_return:+.2f}% = {excess:+.2f}%\n"

        ctx.report_progress(1.0, "Analysis complete!")
        await log_request_end(
            ctx, request_id, "relative_strength", True, f"Calculated RS for {symbol} vs {benchmark}"
        )
        return rs_text

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "relative_strength", e)
        return f"Error calculating relative strength: {error_msg}"


@mcp.tool()
async def volume_profile(ctx: Context, symbol: str, lookback_days: int = 60) -> str:
    """
    Analyze volume distribution by price.

    Args:
        symbol: Stock symbol to analyze
        lookback_days: Number of days to analyze
    """
    request_id = await log_request_start(
        ctx, "volume_profile", {"symbol": symbol, "lookback_days": lookback_days}
    )

    try:
        ctx.report_progress(0.2, f"Fetching {lookback_days} days of data for {symbol}...")
        ctx.log(f"[{request_id}] Fetching historical data")
        # Get historical data
        df = await market_data.get_historical_data(symbol, lookback_days + 10)

        ctx.report_progress(0.6, "Analyzing volume distribution...")
        ctx.log(f"[{request_id}] Analyzing volume profile")

        # Analyze volume profile
        profile = volume_analysis.analyze_volume_profile(df.tail(lookback_days))

        ctx.report_progress(0.9, "Formatting results...")

        # Format the results
        profile_text = f"""
Volume Profile Analysis for {symbol} (last {lookback_days} days):

Point of Control (POC): ${profile["point_of_control"]} (Price level with highest volume)
Value Area: ${profile["value_area_low"]} - ${profile["value_area_high"]} (70% of volume)

Volume by Price Level (High to Low):
"""

        # Sort bins by volume and format
        sorted_bins = sorted(profile["bins"], key=lambda x: x["volume"], reverse=True)
        for i, bin_data in enumerate(sorted_bins[:5]):  # Show top 5 volume levels
            profile_text += f"{i + 1}. ${bin_data['price_low']} - ${bin_data['price_high']}: {bin_data['volume_percent']:.1f}% of volume\n"

        ctx.report_progress(1.0, "Analysis complete!")
        await log_request_end(
            ctx, request_id, "volume_profile", True, f"Analyzed volume profile for {symbol}"
        )
        return profile_text

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "volume_profile", e)
        return f"Error analyzing volume profile: {error_msg}"


@mcp.tool()
async def detect_patterns(ctx: Context, symbol: str) -> str:
    """
    Detect chart patterns in price data.

    Args:
        symbol: Stock symbol to analyze
    """

    request_id = await log_request_start(ctx, "detect_patterns", {"symbol": symbol})

    try:
        ctx.report_progress(0.2, "Fetching data for pattern detection...")
        ctx.log(f"[{request_id}] Fetching 90 days of historical data")
        # Get historical data
        df = await market_data.get_historical_data(symbol, lookback_days=90)

        ctx.report_progress(0.6, "Scanning for chart patterns...")
        ctx.log(f"[{request_id}] Running pattern detection algorithms")

        # Detect patterns
        pattern_results = pattern_recognition.detect_patterns(df)

        ctx.report_progress(0.9, "Formatting pattern results...")

        # Format the results
        if not pattern_results["patterns"]:
            pattern_text = (
                f"No significant chart patterns detected for {symbol} in the recent data."
            )
        else:
            pattern_text = f"Chart Patterns Detected for {symbol}:\n\n"

            for pattern in pattern_results["patterns"]:
                pattern_text += f"- {pattern['type']}"

                if "start_date" in pattern and "end_date" in pattern:
                    pattern_text += f" ({pattern['start_date']} to {pattern['end_date']})"

                pattern_text += f": Price level ${pattern['price_level']}"

                if "confidence" in pattern:
                    pattern_text += f" (Confidence: {pattern['confidence']})"

                pattern_text += "\n"

            pattern_text += "\nNote: Pattern recognition is not 100% reliable and should be confirmed with other forms of analysis."

        ctx.report_progress(1.0, "Pattern detection complete!")
        patterns_found = len(pattern_results.get("patterns", []))
        await log_request_end(
            ctx,
            request_id,
            "detect_patterns",
            True,
            f"Found {patterns_found} patterns for {symbol}",
        )
        return pattern_text

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "detect_patterns", e)
        return f"Error detecting patterns: {error_msg}"


@mcp.tool()
async def position_size(
    ctx: Context,
    symbol: str,
    stop_price: float,
    risk_amount: float,
    account_size: float,
    price: float = 0,
) -> str:
    """
    Calculate optimal position size based on risk parameters.

    Args:
        symbol: Stock symbol
        stop_price: Stop loss price
        risk_amount: Dollar amount to risk
        account_size: Total account size in dollars
        price: Entry price (0 for current price)
    """

    request_id = await log_request_start(
        ctx,
        "position_size",
        {
            "symbol": symbol,
            "stop_price": stop_price,
            "risk_amount": risk_amount,
            "account_size": account_size,
            "price": price,
        },
    )

    try:
        # If price is 0, get the current price
        if price == 0:
            ctx.report_progress(0.2, "Fetching current price...")
            ctx.log(f"[{request_id}] Fetching current price for {symbol}")
            df = await market_data.get_historical_data(symbol, lookback_days=5)
            price = df["close"].iloc[-1]
            ctx.log(f"[{request_id}] Current price: ${price:.2f}")

        ctx.report_progress(0.6, "Calculating position size...")

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
        ctx.report_progress(1.0, "Position sizing complete!")
        await log_request_end(
            ctx,
            request_id,
            "position_size",
            True,
            f"Calculated position size: {position_results['recommended_shares']} shares",
        )
        return position_text

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "position_size", e)
        return f"Error calculating position size: {error_msg}"


@mcp.tool()
async def suggest_stops(ctx: Context, symbol: str) -> str:
    """
    Suggest stop loss levels based on technical analysis.

    Args:
        symbol: Stock symbol to analyze
    """

    request_id = await log_request_start(ctx, "suggest_stops", {"symbol": symbol})

    try:
        ctx.report_progress(0.2, "Fetching data for stop analysis...")
        ctx.log(f"[{request_id}] Fetching 60 days of historical data")
        # Get historical data
        df = await market_data.get_historical_data(symbol, lookback_days=60)

        ctx.report_progress(0.4, "Calculating technical indicators...")
        ctx.log(f"[{request_id}] Adding technical indicators")

        # Add indicators
        df = tech_analysis.add_core_indicators(df)

        ctx.report_progress(0.7, "Analyzing stop levels...")
        ctx.log(f"[{request_id}] Calculating suggested stop levels")

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

        ctx.report_progress(1.0, "Stop analysis complete!")
        await log_request_end(
            ctx,
            request_id,
            "suggest_stops",
            True,
            f"Suggested stop levels for {symbol} at ${latest_close:.2f}",
        )
        return stops_text

    except Exception as e:
        error_msg = await handle_error(ctx, request_id, "suggest_stops", e)
        return f"Error suggesting stops: {error_msg}"


# Startup logging
def log_startup():
    """Log startup information."""
    logger.info("MCP Trader Server starting up...")
    logger.info(f"Server name: {config.server_name}")
    logger.info("Transport: stdio")
    logger.info("All features enabled: crypto, patterns, risk_tools")

    # Check for API keys
    if config.tiingo_api_key:
        logger.info("Tiingo API key configured")
    else:
        logger.warning("No Tiingo API key configured")

    if config.binance_api_key:
        logger.info("Binance API credentials configured")

    logger.info("MCP Trader Server ready to handle requests!")


# Add system status resource
@mcp.resource("mcp://system/status")
async def get_system_status(ctx: Context) -> str:
    """Get current system status and statistics."""
    ctx.log("Generating system status report", level="debug")

    status = {
        "server": "MCP Trader Server",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "tiingo_api_key": "configured" if config.tiingo_api_key else "not configured",
            "binance_api_key": "configured" if config.binance_api_key else "not configured",
        },
        "services": {
            "market_data": "ready",
            "technical_analysis": "ready",
            "relative_strength": "ready",
            "volume_profile": "ready",
            "pattern_recognition": "ready",
            "risk_analysis": "ready",
        },
    }

    return json.dumps(status, indent=2)


# Main function
def main():
    """Main entry point for the MCP server."""
    log_startup()
    mcp.run()


# HTTP server mode (for testing and alternative deployment)
async def run_http_test_server():
    """Run a standalone HTTP server for testing purposes."""
    from aiohttp import web

    app = web.Application()

    async def list_tools_handler(_):
        tools = []
        for name, tool in mcp._tools.items():
            tools.append(
                {
                    "name": name,
                    "description": tool.__doc__ or "",
                    "inputSchema": {"type": "object", "properties": {}},
                }
            )
        return web.json_response(tools)

    async def call_tool_handler(req):
        data = await req.json()
        name = data.get("name")
        arguments = data.get("arguments", {})

        # Call FastMCP tool
        tool_func = mcp._tools.get(name)
        if not tool_func:
            return web.json_response({"error": f"Unknown tool: {name}"}, status=404)

        # Create a mock context
        class MockContext:
            def log(self, msg, level="info"):
                logger.log(getattr(logging, level.upper()), msg)

            def report_progress(self, progress, message=""):
                logger.info(f"Progress: {progress * 100:.0f}% - {message}")

        ctx = MockContext()

        try:
            result = await tool_func(ctx, **arguments)
            return web.json_response({"type": "text", "text": result})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    app.router.add_get("/list-tools", list_tools_handler)
    app.router.add_post("/call-tool", call_tool_handler)

    logger.info("Starting HTTP test server on http://localhost:8000")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8000)
    await site.start()

    # Keep the server running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run as HTTP test server
        asyncio.run(run_http_test_server())
    else:
        # Run as MCP server
        main()
