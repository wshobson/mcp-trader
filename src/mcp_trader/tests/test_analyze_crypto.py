"""Unit tests for analyze_crypto functionality."""

from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from mcp_trader.server import mcp


@pytest.fixture
def mock_context():
    """Create a mock context."""
    ctx = Mock()
    ctx.log = Mock()
    ctx.report_progress = Mock()
    return ctx


@pytest.fixture
def sample_crypto_df():
    """Create sample crypto data."""
    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(40000, 50000, 30),
        "high": np.random.uniform(45000, 55000, 30),
        "low": np.random.uniform(35000, 45000, 30),
        "close": np.random.uniform(40000, 50000, 30),
        "volume": np.random.uniform(1000000, 5000000, 30),
    })


@pytest.mark.asyncio
async def test_analyze_crypto_tiingo(mock_context, sample_crypto_df):
    """Test analyze_crypto with Tiingo provider."""
    with patch("mcp_trader.server.market_data") as mock_market_data:
        mock_market_data.get_crypto_historical_data = AsyncMock(return_value=sample_crypto_df)
        
        with patch("mcp_trader.server.tech_analysis") as mock_tech:
            enhanced_df = sample_crypto_df.copy()
            enhanced_df["atr"] = 1500.0
            enhanced_df["adrp"] = 3.2
            
            mock_tech.add_core_indicators.return_value = enhanced_df
            mock_tech.check_trend_status.return_value = {
                "above_20sma": True,
                "above_50sma": True,
                "above_200sma": False,
                "20_50_bullish": True,
                "50_200_bullish": False,
                "rsi": 58.5,
                "macd_bullish": True,
            }
            
            tools = await mcp.get_tools()
            result = await tools["analyze_crypto"].fn(
                mock_context, "BTC", "tiingo", 30, "usd"
            )
            
            assert "Technical Analysis for BTC (Tiingo)" in result
            assert "RSI (14): 58.50" in result
            assert "✅" in result  # Some positive indicators
            assert "❌" in result  # Some negative indicators


@pytest.mark.asyncio
async def test_analyze_crypto_binance(mock_context, sample_crypto_df):
    """Test analyze_crypto with Binance provider."""
    with patch("mcp_trader.server.market_data") as mock_market_data:
        mock_market_data.get_crypto_historical_data = AsyncMock(return_value=sample_crypto_df)
        
        with patch("mcp_trader.server.tech_analysis") as mock_tech:
            enhanced_df = sample_crypto_df.copy()
            enhanced_df["atr"] = 1200.0
            enhanced_df["adrp"] = 2.8
            
            mock_tech.add_core_indicators.return_value = enhanced_df
            mock_tech.check_trend_status.return_value = {
                "above_20sma": False,
                "above_50sma": False,
                "above_200sma": True,
                "20_50_bullish": False,
                "50_200_bullish": True,
                "rsi": 42.3,
                "macd_bullish": False,
            }
            
            tools = await mcp.get_tools()
            result = await tools["analyze_crypto"].fn(
                mock_context, "BTCUSDT", "binance", 30
            )
            
            assert "Technical Analysis for BTCUSDT (Binance)" in result
            assert "RSI (14): 42.30" in result