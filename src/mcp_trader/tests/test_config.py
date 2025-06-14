"""
Unit tests for simplified configuration management.

Tests environment variable loading and defaults for the server.
"""

import os
from unittest.mock import patch

import pytest

from mcp_trader.config import Config, config


class TestConfig:
    """Test Config functionality."""

    def test_default_config(self):
        """Test default config with no environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            cfg = Config()
            assert cfg.tiingo_api_key is None
            assert cfg.binance_api_key is None
            assert cfg.binance_api_secret is None
            assert cfg.server_name == "mcp-trader"

    def test_config_from_env(self):
        """Test config loading from environment variables."""
        env_vars = {
            "TIINGO_API_KEY": "test-tiingo-key",
            "BINANCE_API_KEY": "test-binance-key",
            "BINANCE_API_SECRET": "test-binance-secret",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            cfg = Config.from_env()
            assert cfg.tiingo_api_key == "test-tiingo-key"
            assert cfg.binance_api_key == "test-binance-key"
            assert cfg.binance_api_secret == "test-binance-secret"
            assert cfg.server_name == "mcp-trader"

    def test_config_initialization(self):
        """Test direct config initialization."""
        cfg = Config(
            tiingo_api_key="my-tiingo-key",
            binance_api_key="my-binance-key",
            binance_api_secret="my-binance-secret",
            server_name="custom-server",
        )

        assert cfg.tiingo_api_key == "my-tiingo-key"
        assert cfg.binance_api_key == "my-binance-key"
        assert cfg.binance_api_secret == "my-binance-secret"
        assert cfg.server_name == "custom-server"


class TestGlobalConfig:
    """Test the global config instance."""

    def test_global_config_exists(self):
        """Test that global config instance exists."""
        assert config is not None
        assert isinstance(config, Config)

    def test_global_config_attributes(self):
        """Test that global config has expected attributes."""
        assert hasattr(config, "tiingo_api_key")
        assert hasattr(config, "binance_api_key")
        assert hasattr(config, "binance_api_secret")
        assert hasattr(config, "server_name")
        assert config.server_name == "mcp-trader"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
