"""Simplified configuration for MCP Trader."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Simple configuration for MCP Trader."""

    # API Keys
    tiingo_api_key: str | None = None
    binance_api_key: str | None = None
    binance_api_secret: str | None = None

    # Server settings
    server_name: str = "mcp-trader"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            tiingo_api_key=os.getenv("TIINGO_API_KEY"),
            binance_api_key=os.getenv("BINANCE_API_KEY"),
            binance_api_secret=os.getenv("BINANCE_API_SECRET"),
        )


# Global config instance
config = Config.from_env()
