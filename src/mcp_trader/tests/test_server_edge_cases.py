"""Tests for edge cases and error paths in server.py."""

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


class TestRelativeStrengthEdgeCases:
    """Test edge cases for relative strength tool."""

    @pytest.mark.asyncio
    async def test_relative_strength_underperformance(self, mock_context):
        """Test relative strength with underperformance scores."""
        with patch("mcp_trader.server.rs_analysis") as mock_rs:
            # Test all underperformance categories
            mock_rs.calculate_rs = AsyncMock(return_value={
                "RS_21d": 10,    # Strong underperformance
                "RS_63d": 25,    # Moderate underperformance
                "RS_126d": 40,   # Slight underperformance
                "RS_252d": 50,   # Slight outperformance
                "Return_21d": -15.5,
                "Benchmark_21d": 2.0,
                "Excess_21d": -17.5,
            })
            
            tools = await mcp.get_tools()
            result = await tools["relative_strength"].fn(
                mock_context, "AAPL", "SPY"
            )
            
            assert "(Strong Underperformance) ⚠️⚠️⚠️" in result
            assert "(Moderate Underperformance) ⚠️⚠️" in result
            assert "(Slight Underperformance) ⚠️" in result
            assert "(Slight Outperformance) ⭐" in result

    @pytest.mark.asyncio
    async def test_relative_strength_missing_performance_data(self, mock_context):
        """Test when performance detail data is missing."""
        with patch("mcp_trader.server.rs_analysis") as mock_rs:
            # Only RS scores, no return data
            mock_rs.calculate_rs = AsyncMock(return_value={
                "RS_21d": 75,
                "RS_63d": 82,
                # Missing Return/Benchmark/Excess data
            })
            
            tools = await mcp.get_tools()
            result = await tools["relative_strength"].fn(
                mock_context, "TSLA", "SPY"
            )
            
            assert "21d Relative Strength: 75" in result
            assert "Performance Details:" in result
            # Should not show return details if data is missing


class TestVolumeProfileEdgeCases:
    """Test edge cases for volume profile tool."""

    @pytest.mark.asyncio
    async def test_volume_profile_error(self, mock_context):
        """Test volume profile error handling."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(
                side_effect=Exception("Data unavailable")
            )
            
            tools = await mcp.get_tools()
            result = await tools["volume_profile"].fn(
                mock_context, "INVALID", 30
            )
            
            assert "Error analyzing volume profile" in result
            assert "Data unavailable" in result


class TestPositionSizeEdgeCases:
    """Test edge cases for position size tool."""

    @pytest.mark.asyncio
    async def test_position_size_error(self, mock_context):
        """Test position size error handling."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            tools = await mcp.get_tools()
            result = await tools["position_size"].fn(
                mock_context, "AAPL", 145.0, 500.0, 50000.0, 0
            )
            
            assert "Error calculating position size" in result
            assert "API Error" in result


class TestSuggestStopsEdgeCases:
    """Test edge cases for suggest stops tool."""

    @pytest.mark.asyncio
    async def test_suggest_stops_with_sma_levels(self, mock_context, mock_df):
        """Test stop suggestions with all SMA levels present."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(return_value=mock_df)
            
            with patch("mcp_trader.server.tech_analysis") as mock_tech:
                mock_tech.add_core_indicators.return_value = mock_df
                
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
                        "sma_200": 140.00,
                        "recent_swing": 143.00,
                    }
                    
                    tools = await mcp.get_tools()
                    result = await tools["suggest_stops"].fn(
                        mock_context, "AAPL"
                    )
                    
                    assert "20-day SMA: $148.00" in result
                    assert "50-day SMA: $145.00" in result
                    assert "200-day SMA: $140.00" in result
                    assert "Recent Swing Low: $143.00" in result

    @pytest.mark.asyncio
    async def test_suggest_stops_error(self, mock_context):
        """Test suggest stops error handling."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(
                side_effect=Exception("Connection error")
            )
            
            tools = await mcp.get_tools()
            result = await tools["suggest_stops"].fn(
                mock_context, "AAPL"
            )
            
            assert "Error suggesting stops" in result
            assert "Connection error" in result


class TestDetectPatternsEdgeCases:
    """Test edge cases for detect patterns tool."""

    @pytest.mark.asyncio
    async def test_detect_patterns_error(self, mock_context):
        """Test pattern detection error handling."""
        with patch("mcp_trader.server.market_data") as mock_market_data:
            mock_market_data.get_historical_data = AsyncMock(
                side_effect=Exception("Invalid symbol")
            )
            
            tools = await mcp.get_tools()
            result = await tools["detect_patterns"].fn(
                mock_context, "INVALID"
            )
            
            assert "Error detecting patterns" in result
            assert "Invalid symbol" in result


class TestHTTPTestServer:
    """Test the HTTP test server functionality."""

    @pytest.mark.asyncio
    async def test_run_http_test_server(self):
        """Test that HTTP test server can be created."""
        from mcp_trader.server import run_http_test_server
        
        # Just verify the function exists and is callable
        assert callable(run_http_test_server)


class TestMainFunction:
    """Test the main entry point."""

    def test_main_stdio(self):
        """Test main function with stdio transport."""
        with patch("mcp_trader.server.mcp.run") as mock_run:
            from mcp_trader.server import main
            
            main()
            
            mock_run.assert_called_once()


@pytest.fixture
def mock_df():
    """Create a mock DataFrame for testing."""
    dates = pd.date_range(start="2024-01-01", periods=60, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(140, 160, 60),
        "high": np.random.uniform(145, 165, 60),
        "low": np.random.uniform(135, 155, 60),
        "close": np.random.uniform(140, 160, 60),
        "volume": np.random.uniform(1000000, 5000000, 60),
    })