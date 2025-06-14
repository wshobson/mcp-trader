"""Smoke tests for basic functionality."""

import pytest

from mcp_trader import __version__, server
from mcp_trader.config import Config, config
from mcp_trader.data import MarketData
from mcp_trader.indicators import TechnicalAnalysis
from mcp_trader.models import CandleData, MarketDataResponse


def test_imports():
    """Test that all main modules can be imported."""
    assert server is not None
    assert MarketData is not None
    assert TechnicalAnalysis is not None
    assert Config is not None


def test_config_loads():
    """Test that configuration loads without errors."""
    assert config is not None
    assert isinstance(config, Config)
    assert hasattr(config, "tiingo_api_key")
    assert hasattr(config, "server_name")


def test_server_tools():
    """Test that server has tools defined."""
    from mcp_trader.server import mcp

    # FastMCP provides get_tools() method
    assert hasattr(mcp, "get_tools")
    # Note: get_tools() is async, we'll test it properly in async test


@pytest.mark.asyncio
async def test_basic_tool_structure():
    """Test basic tool structure."""
    from mcp_trader.server import mcp

    # Check that we have expected tools
    tools = await mcp.get_tools()
    tool_names = list(tools.keys())
    expected_tools = [
        "analyze_crypto",
        "analyze_stock",
        "relative_strength",
        "volume_profile",
        "detect_patterns",
        "position_size",
        "suggest_stops",
    ]

    for expected in expected_tools:
        assert expected in tool_names, f"Tool {expected} not found"


class TestPackageStructure:
    """Test the overall package structure."""

    def test_version(self):
        """Test that version is defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_main_entry_point(self):
        """Test that main entry point exists."""
        from mcp_trader.server import main

        assert callable(main)

    def test_model_imports(self):
        """Test that all models can be imported."""
        from mcp_trader.models import (
            AnalyzeCryptoRequest,
            AnalyzeStockRequest,
            CandleData,
            ChartPattern,
            MarketDataResponse,
            PatternDetectionResult,
            PositionSizeRequest,
            PositionSizeResult,
            RelativeStrengthPeriod,
            RelativeStrengthRequest,
            RelativeStrengthResult,
            StopLevelSuggestions,
            StopSuggestionRequest,
            TechnicalAnalysisResult,
            TechnicalIndicators,
            TrendStatus,
            VolumeBin,
            VolumeProfileRequest,
            VolumeProfileResult,
        )

        # Just check that they're all imported successfully
        assert CandleData is not None
        assert MarketDataResponse is not None