"""Unit tests for relative_strength functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_trader.server import mcp


@pytest.fixture
def mock_context():
    """Create a mock context."""
    ctx = Mock()
    ctx.log = Mock()
    ctx.report_progress = Mock()
    return ctx


@pytest.mark.asyncio
async def test_relative_strength(mock_context):
    """Test the relative_strength tool with NVDA and SPY."""
    with patch("mcp_trader.server.rs_analysis") as mock_rs:
        mock_rs.calculate_rs = AsyncMock(return_value={
            "RS_21d": 85,
            "RS_63d": 78,
            "RS_126d": 92,
            "RS_252d": 88,
            "Return_21d": 8.5,
            "Benchmark_21d": 2.1,
            "Excess_21d": 6.4,
            "Return_63d": 15.2,
            "Benchmark_63d": 5.8,
            "Excess_63d": 9.4,
            "Return_126d": 32.5,
            "Benchmark_126d": 12.1,
            "Excess_126d": 20.4,
            "Return_252d": 65.8,
            "Benchmark_252d": 22.3,
            "Excess_252d": 43.5,
        })
        
        tools = await mcp.get_tools()
        result = await tools["relative_strength"].fn(
            mock_context, "NVDA", "SPY"
        )
        
        assert "Relative Strength Analysis for NVDA vs SPY" in result
        assert "21d Relative Strength: 85" in result
        assert "(Strong Outperformance)" in result
        assert "NVDA +8.50%" in result
        assert "SPY +2.10%" in result
        assert "= +6.40%" in result