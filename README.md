# MCP Trader Server

[![smithery badge](https://smithery.ai/badge/mcp-trader)](https://smithery.ai/server/mcp-trader)

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

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- [ta-lib](https://ta-lib.org/install/)
- [Tiingo API Key](https://api.tiingo.com/)

### Environment Variables

Create a `.env` file:

```bash
TIINGO_API_KEY=your_api_key_here
```

### Installing via Smithery

To install Trader for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-trader):

```bash
npx -y @smithery/cli install mcp-trader --client claude
```

### Installation

```bash
uv venv --python 3.11
source .venv/bin/activate # On Windows: .venv\Scripts\activate
uv sync
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
        "/absolute/path/to/mcp-trader",
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

![NVDA Technical Analysis](./technical-mcp.png)

## Dependencies

See pyproject.toml for full dependency list:

```
- aiohttp >=3.11.11
- mcp >=1.2.0
- pandas >=2.2.3
- pandas-ta >=0.3.14b0
- python-dotenv >=1.0.1
```

## Further Reading

Learn more about this project through these detailed blog posts:

- [Building a Stock Analysis Server with MCP, Part 1](https://sethhobson.com/2025/01/building-a-stock-analysis-server-with-mcp-part-1/) - Initial setup, architecture, and core technical analysis features
- [Building a Stock Analysis Server with MCP, Part 2](https://sethhobson.com/2025/03/building-a-stock-analysis-server-with-mcp-part-2/) - Relative Strength, Volume, Pattern Recognition, Risk analysis
