"""Tests for server startup and logging functionality."""

import os
from unittest.mock import Mock, patch

import pytest

from mcp_trader.server import log_startup, mcp


class TestServerStartup:
    """Test server startup and logging."""

    def test_log_startup_with_api_keys(self):
        """Test startup logging with API keys configured."""
        with patch("mcp_trader.server.logger") as mock_logger:
            with patch("mcp_trader.server.config") as mock_config:
                mock_config.tiingo_api_key = "test-key"
                mock_config.binance_api_key = "binance-key"
                mock_config.server_name = "mcp-trader"
                log_startup()
                
                # Check that appropriate log messages were made
                assert mock_logger.info.call_count >= 4
                log_messages = [call[0][0] for call in mock_logger.info.call_args_list]
                
                # Just check that we got some log messages
                assert len(log_messages) >= 5
                assert "MCP Trader Server starting up..." in log_messages[0]
                assert "MCP Trader Server ready to handle requests!" in log_messages[-1]

    def test_log_startup_without_api_keys(self):
        """Test startup logging without API keys."""
        with patch("mcp_trader.server.logger") as mock_logger:
            with patch("mcp_trader.server.config") as mock_config:
                mock_config.tiingo_api_key = None
                mock_config.binance_api_key = None
                mock_config.server_name = "mcp-trader"
                log_startup()
                
                # Check warning about missing Tiingo key
                assert mock_logger.warning.called
                warning_messages = [call[0][0] for call in mock_logger.warning.call_args_list]
                assert any("No Tiingo API key configured" in msg for msg in warning_messages)

    def test_log_startup_logging_calls(self):
        """Test specific logging calls during startup."""
        with patch("mcp_trader.server.logger") as mock_logger:
            log_startup()
            
            # Verify specific log messages
            info_calls = mock_logger.info.call_args_list
            assert len(info_calls) >= 3
            
            # First call should be startup message
            assert "MCP Trader Server starting up" in info_calls[0][0][0]
            
            # Should log server name
            server_name_logged = any("Server name:" in call[0][0] for call in info_calls)
            assert server_name_logged


class TestSystemStatusResource:
    """Test system status resource functionality."""

    @pytest.mark.asyncio
    async def test_system_status_with_api_keys(self):
        """Test system status when API keys are configured."""
        mock_context = Mock()
        mock_context.log = Mock()
        
        with patch("mcp_trader.server.config") as mock_config:
            mock_config.tiingo_api_key = "test-tiingo-key"
            mock_config.binance_api_key = "test-binance-key"
            resources = await mcp.get_resources()
            result = await resources["mcp://system/status"].fn(mock_context)
            
            import json
            status = json.loads(result)
            
            assert status["server"] == "MCP Trader Server"
            assert status["version"] == "2.0.0"
            assert status["status"] == "operational"
            assert status["environment"]["tiingo_api_key"] == "configured"
            assert status["environment"]["binance_api_key"] == "configured"
            assert status["services"]["market_data"] == "ready"
            assert status["services"]["technical_analysis"] == "ready"

    @pytest.mark.asyncio
    async def test_system_status_without_api_keys(self):
        """Test system status when API keys are not configured."""
        mock_context = Mock()
        mock_context.log = Mock()
        
        with patch("mcp_trader.server.config") as mock_config:
            mock_config.tiingo_api_key = None
            mock_config.binance_api_key = None
            resources = await mcp.get_resources()
            result = await resources["mcp://system/status"].fn(mock_context)
            
            import json
            status = json.loads(result)
            
            assert status["environment"]["tiingo_api_key"] == "not configured"
            assert status["environment"]["binance_api_key"] == "not configured"