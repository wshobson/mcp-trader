"""Tests for simplified MCP Trader server."""

import json
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from fastmcp import Context

from mcp_trader.server import mcp


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    ctx = Mock(spec=Context)
    ctx.log = Mock()
    ctx.report_progress = Mock()
    return ctx


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(100, 200, 100),
        "high": np.random.uniform(150, 250, 100),
        "low": np.random.uniform(50, 150, 100),
        "close": np.random.uniform(100, 200, 100),
        "volume": np.random.uniform(1000000, 5000000, 100),
        "symbol": ["TEST"] * 100,
    })


class TestAnalyzeCrypto:
    """Test analyze_crypto tool."""

    @pytest.mark.asyncio
    async def test_analyze_crypto_success(self, mock_context, sample_df):
        """Test successful crypto analysis."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_crypto_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.tech_analysis") as mock_tech:
                enhanced_df = sample_df.copy()
                enhanced_df["atr"] = 5.0
                enhanced_df["adrp"] = 2.5

                mock_tech.add_core_indicators.return_value = enhanced_df
                mock_tech.check_trend_status.return_value = {
                    "above_20sma": True,
                    "above_50sma": True,
                    "above_200sma": False,
                    "20_50_bullish": True,
                    "50_200_bullish": False,
                    "rsi": 65.5,
                    "macd_bullish": True,
                }

                # Get the tool and call its function
                tools = await mcp.get_tools()
                result = await tools["analyze_crypto"].fn(
                    mock_context, "BTC", "tiingo", 30, "usd"
                )

                assert "Technical Analysis for BTC" in result
                assert "✅" in result
                assert "❌" in result
                assert "RSI (14): 65.50" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_error(self, mock_context):
        """Test crypto analysis error handling."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_crypto_historical_data = AsyncMock(
                side_effect=Exception("API Error")
            )

            tools = await mcp.get_tools()
            result = await tools["analyze_crypto"].fn(
                mock_context, "BTC"
            )
            assert "Error analyzing BTC" in result


class TestAnalyzeStock:
    """Test analyze_stock tool."""

    @pytest.mark.asyncio
    async def test_analyze_stock_success(self, mock_context, sample_df):
        """Test successful stock analysis."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.tech_analysis") as mock_tech:
                enhanced_df = sample_df.copy()
                enhanced_df["atr"] = 2.5
                enhanced_df["adrp"] = 1.8
                enhanced_df["avg_20d_vol"] = 1000000

                mock_tech.add_core_indicators.return_value = enhanced_df
                mock_tech.check_trend_status.return_value = {
                    "above_20sma": True,
                    "above_50sma": False,
                    "above_200sma": True,
                    "20_50_bullish": False,
                    "50_200_bullish": True,
                    "rsi": 55.2,
                    "macd_bullish": False,
                }

                tools = await mcp.get_tools()
                result = await tools["analyze_stock"].fn(
                    mock_context, "AAPL"
                )

                assert "Technical Analysis for AAPL" in result
                assert "RSI (14): 55.20" in result
                assert "Latest Price: $" in result

    @pytest.mark.asyncio
    async def test_analyze_stock_error(self, mock_context):
        """Test stock analysis error handling."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(
                side_effect=Exception("Market closed")
            )

            tools = await mcp.get_tools()
            result = await tools["analyze_stock"].fn(
                mock_context, "AAPL"
            )
            assert "Error analyzing AAPL" in result


class TestRelativeStrength:
    """Test relative_strength tool."""

    @pytest.mark.asyncio
    async def test_relative_strength_success(self, mock_context):
        """Test successful relative strength calculation."""
        with patch("mcp_trader.server.rs_analysis") as mock_rs:
            mock_rs.calculate_rs = AsyncMock(return_value={
                "RS_21d": 75,
                "RS_63d": 82,
                "RS_126d": 45,
                "RS_252d": 60,
                "Return_21d": 5.5,
                "Benchmark_21d": 2.0,
                "Excess_21d": 3.5,
                "Return_63d": 12.0,
                "Benchmark_63d": 5.0,
                "Excess_63d": 7.0,
            })

            tools = await mcp.get_tools()
            result = await tools["relative_strength"].fn(
                mock_context, "NVDA", "SPY"
            )

            assert "Relative Strength Analysis for NVDA vs SPY" in result
            assert "21d Relative Strength: 75" in result
            assert "(Moderate Outperformance)" in result

    @pytest.mark.asyncio
    async def test_relative_strength_no_data(self, mock_context):
        """Test relative strength with no data."""
        with patch("mcp_trader.server.rs_analysis") as mock_rs:
            mock_rs.calculate_rs = AsyncMock(return_value={})

            tools = await mcp.get_tools()
            result = await tools["relative_strength"].fn(
                mock_context, "AAPL", "SPY"
            )
            assert "Insufficient historical data" in result


class TestVolumeProfile:
    """Test volume_profile tool."""

    @pytest.mark.asyncio
    async def test_volume_profile_success(self, mock_context, sample_df):
        """Test successful volume profile analysis."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.volume_analysis") as mock_volume:
                mock_volume.analyze_volume_profile.return_value = {
                    "point_of_control": 150.50,
                    "value_area_low": 140.00,
                    "value_area_high": 160.00,
                    "bins": [
                        {
                            "price_low": 145,
                            "price_high": 150,
                            "volume": 1000000,
                            "volume_percent": 25.0,
                        },
                        {
                            "price_low": 150,
                            "price_high": 155,
                            "volume": 800000,
                            "volume_percent": 20.0,
                        },
                    ],
                }

                tools = await mcp.get_tools()
                result = await tools["volume_profile"].fn(
                    mock_context, "AAPL", 30
                )

                assert "Volume Profile Analysis for AAPL" in result
                assert "Point of Control (POC): $150.5" in result
                assert "Value Area: $140.0 - $160.0" in result


class TestDetectPatterns:
    """Test detect_patterns tool."""

    @pytest.mark.asyncio
    async def test_detect_patterns_found(self, mock_context, sample_df):
        """Test pattern detection with patterns found."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.pattern_recognition") as mock_pattern:
                mock_pattern.detect_patterns.return_value = {
                    "patterns": [
                        {
                            "type": "Double Bottom",
                            "start_date": "2024-01-01",
                            "end_date": "2024-01-15",
                            "price_level": 145.50,
                            "confidence": "High",
                        }
                    ]
                }

                tools = await mcp.get_tools()
                result = await tools["detect_patterns"].fn(
                    mock_context, "AAPL"
                )

                assert "Chart Patterns Detected for AAPL" in result
                assert "Double Bottom" in result
                assert "Confidence: High" in result

    @pytest.mark.asyncio
    async def test_detect_patterns_none_found(self, mock_context, sample_df):
        """Test pattern detection with no patterns found."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.pattern_recognition") as mock_pattern:
                mock_pattern.detect_patterns.return_value = {"patterns": []}

                tools = await mcp.get_tools()
                result = await tools["detect_patterns"].fn(
                    mock_context, "AAPL"
                )
                assert "No significant chart patterns detected" in result


class TestPositionSize:
    """Test position_size tool."""

    @pytest.mark.asyncio
    async def test_position_size_with_price(self, mock_context):
        """Test position sizing with provided price."""
        with patch("mcp_trader.server.risk_analysis") as mock_risk:
            mock_risk.calculate_position_size.return_value = {
                "recommended_shares": 100,
                "position_cost": 15000.00,
                "dollar_risk": 500.00,
                "risk_per_share": 5.00,
                "account_percent_risked": 1.0,
                "r_multiples": {"r1": 155.00, "r2": 160.00, "r3": 165.00},
            }

            tools = await mcp.get_tools()
            result = await tools["position_size"].fn(
                mock_context, "AAPL", 145.0, 500.0, 50000.0, 150.0
            )

            assert "Position Sizing for AAPL at $150.00" in result
            assert "100 shares ($15000.00)" in result
            assert "Risk: $500.00 (1.00% of account)" in result

    @pytest.mark.asyncio
    async def test_position_size_current_price(self, mock_context, sample_df):
        """Test position sizing with current price fetch."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.risk_analysis") as mock_risk:
                mock_risk.calculate_position_size.return_value = {
                    "recommended_shares": 50,
                    "position_cost": 7500.00,
                    "dollar_risk": 250.00,
                    "risk_per_share": 5.00,
                    "account_percent_risked": 0.5,
                    "r_multiples": {"r1": 155.00, "r2": 160.00, "r3": 165.00},
                }

                tools = await mcp.get_tools()
                result = await tools["position_size"].fn(
                    mock_context, "AAPL", 145.0, 250.0, 50000.0, 0
                )

                assert "Position Sizing for AAPL" in result
                assert "50 shares" in result


class TestSuggestStops:
    """Test suggest_stops tool."""

    @pytest.mark.asyncio
    async def test_suggest_stops_success(self, mock_context, sample_df):
        """Test successful stop suggestion."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=sample_df)

            with patch("mcp_trader.server.tech_analysis") as mock_tech:
                mock_tech.add_core_indicators.return_value = sample_df

                with patch("mcp_trader.server.risk_analysis") as mock_risk:
                    mock_risk.suggest_stop_levels.return_value = {
                        "atr_1x": 147.50,
                        "atr_2x": 145.00,
                        "atr_3x": 142.50,
                        "percent_2": 147.00,
                        "percent_5": 142.50,
                        "percent_8": 138.00,
                        "sma_20": 148.00,
                        "sma_50": 145.00,
                        "recent_swing": 143.00,
                    }

                    tools = await mcp.get_tools()
                    result = await tools["suggest_stops"].fn(
                        mock_context, "AAPL"
                    )

                    assert "Suggested Stop Levels for AAPL" in result
                    assert "ATR-Based Stops:" in result
                    assert "Conservative (1x ATR):" in result


class TestSystemStatus:
    """Test system status resource."""

    @pytest.mark.asyncio
    async def test_system_status(self, mock_context):
        """Test system status resource."""
        with patch.dict("os.environ", {"TIINGO_API_KEY": "test-key"}):
            resources = await mcp.get_resources()
            # Resources may have a different structure, let's use the fn directly
            result = await resources["mcp://system/status"].fn(mock_context)

            status = json.loads(result)
            assert status["server"] == "MCP Trader Server"
            assert status["status"] == "operational"
            assert "timestamp" in status
            assert status["environment"]["tiingo_api_key"] == "configured"