# MCP Trader Server

A Model Context Protocol (MCP) server for stock traders.

## Features

### Tools

The server provides one tool (more to come):

- **analyze-stock**: Performs technical analysis on a given stock symbol
  - Required argument: `symbol` (string, e.g. "NVDA")
  - Returns comprehensive technical analysis including:
    - Moving average trends (20, 50, 200 SMA)
    - Momentum indicators (RSI, MACD)
    - Volatility metrics (ATR, ADRP)
    - Volume analysis

## Setup

### Prerequisites

- Python 3.13+
- [Tiingo API Key](https://api.tiingo.com/)

### Environment Variables

Create a `.env` file:

```bash
TIINGO_API_KEY=your_api_key_here
```

### Installation

```bash
uv sync
uv venv --python 3.11
source .venv/bin/activate # On Windows: .venv\Scripts\activate
```

## Configuration

### Claude Desktop App

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Development Configuration:

```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/wshobson/workspace/modelcontextprotocol/mcp-trader",
        "run",
        "mcp-trader"
      ]
      "env": {
        "TIINGO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Development

### Build and Run

```bash
uv build
uv run mcp-trader
```

### Debugging

Use the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-trader run mcp-trader
```

## Example Usage

In Claude Desktop:

```
Analyze the technical setup for NVDA
```

The server will return a technical analysis summary including trend status, momentum indicators, and key metrics.

## Dependencies

See pyproject.toml for full dependency list:

```
- aiohttp >=3.11.11
- mcp >=1.2.0
- pandas >=2.2.3
- pandas-ta >=0.3.14b0
- python-dotenv >=1.0.1
```
