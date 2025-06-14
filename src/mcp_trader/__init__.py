"""MCP Trader - Technical analysis tools for stocks and crypto."""

__version__ = "0.3.0"

from . import server


def main():
    """Main entry point for the package."""
    server.main()


# Optionally expose other important items at package level
__all__ = ["__version__", "main", "server"]
