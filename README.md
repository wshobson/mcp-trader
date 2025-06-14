# MCP Trader Server

[![smithery badge](https://smithery.ai/badge/mcp-trader)](https://smithery.ai/server/mcp-trader)

A simplified Model Context Protocol (MCP) server for stock and cryptocurrency analysis. This version is optimized for learning with minimal configuration and clear code structure.

## Features

### Technical Analysis Tools

The server provides the following tools for market analysis:

- **analyze-stock**: Performs technical analysis on a given stock symbol
  - Required argument: `symbol` (string, e.g. "NVDA")
  - Returns comprehensive technical analysis including:
    - Moving average trends (20, 50, 200 SMA)
    - Momentum indicators (RSI, MACD)
    - Volatility metrics (ATR, ADRP)
    - Volume analysis

- **analyze-crypto**: Performs technical analysis on cryptocurrency assets
  - Required argument: `symbol` (string, e.g. "BTC", "ETH", "BTCUSDT" for Binance)
  - Optional arguments:
    - `provider` (string, default: "tiingo", options: "tiingo", "binance")
    - `lookback_days` (integer, default: 365)
    - `quote_currency` (string, default: "usd" for Tiingo, "USDT" for Binance)
  - Returns comprehensive technical analysis including all stock indicators plus crypto-specific metrics

- **relative-strength**: Calculates a stock's relative strength compared to a benchmark
  - Required argument: `symbol` (string, e.g. "AAPL")
  - Optional argument: `benchmark` (string, default: "SPY")
  - Returns relative strength metrics across multiple timeframes (21, 63, 126, 252 days)

- **volume-profile**: Analyzes volume distribution by price
  - Required argument: `symbol` (string, e.g. "MSFT")
  - Optional argument: `lookback_days` (integer, default: 60)
  - Returns volume profile analysis including Point of Control (POC) and Value Area

- **detect-patterns**: Identifies chart patterns in price data
  - Required argument: `symbol` (string, e.g. "AMZN")
  - Returns detected chart patterns with confidence levels and price targets

- **position-size**: Calculates optimal position size based on risk parameters
  - Required arguments:
    - `symbol` (string, e.g. "TSLA")
    - `stop_price` (number)
    - `risk_amount` (number)
    - `account_size` (number)
  - Optional argument: `price` (number, default: current price)
  - Returns recommended position size and R-multiple profit targets

- **suggest-stops**: Suggests stop loss levels based on technical analysis
  - Required argument: `symbol` (string, e.g. "META")
  - Returns multiple stop loss suggestions based on ATR, percentages, and technical levels

### FastMCP Resources (NEW)

The server now supports FastMCP resources for direct market data access:

#### Stock Resources
- `stock://{symbol}` - Get current stock price and statistics
- `stock://{symbol}/history` - Get historical price data

#### Crypto Resources  
- `crypto://{symbol}` - Get current crypto price (supports Tiingo & Binance)
- `crypto://{symbol}/history` - Get historical crypto data

#### Cache Resources
- `market://cache/clear` - Clear the data cache
- `market://cache/status` - View cache statistics

### Data Sources

- **Stocks**: [Tiingo API](https://api.tiingo.com/) for historical daily OHLCV data
- **Crypto**: 
  - Tiingo API for major pairs (BTC, ETH, etc. paired with USD)
  - Binance API for extended pairs and USDT quotes

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [Tiingo API Key](https://api.tiingo.com/)
- Optional: [ta-lib](https://ta-lib.org/install/) for enhanced performance (see [INSTALL.md](INSTALL.md))

### Environment Variables

Create a `.env` file in your project root:

```bash
# MCP Trader
# Copy this file to .env for API access

# Tiingo API Key (free tier works great)
# Get yours at: https://www.tiingo.com/
TIINGO_API_KEY=your_tiingo_api_key_here

# Optional: For higher rate limits
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
```

### Installation

```bash
# Clone the repository
git clone https://github.com/wshobson/mcp-trader.git
cd mcp-trader

# Create virtual environment and install dependencies
uv venv --python 3.11
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync

# Copy the example environment file
cp .env.example .env
# Edit .env and add your Tiingo API key
```

## Configuration

### Claude Desktop App

The configuration file location varies by platform:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

#### Standard MCP Configuration

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
      ],
      "env": {
        "TIINGO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### FastMCP Configuration (with Resources)

To enable FastMCP resources alongside the standard tools:

```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-trader",
        "run",
        "python",
        "-m",
        "mcp_trader.fastmcp_server"
      ],
      "env": {
        "TIINGO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Running Tests

The project includes a comprehensive test suite with 80% code coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/mcp_trader --cov-report=term-missing

# Run specific test file
pytest src/mcp_trader/tests/test_indicators.py

# Run with verbose output
pytest -v
```

## Running the Server

### Standard Mode

Runs the MCP server with all tools:

```bash
uv run mcp-trader
```

### Development Mode

For development and debugging:

```bash
# Run with Python directly
uv run python -m mcp_trader.server

# Run with MCP Inspector for debugging
npx @modelcontextprotocol/inspector uv --directory . run mcp-trader
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t mcp-trader .

# Run the container
docker run -e TIINGO_API_KEY=your_api_key_here -p 8000:8000 mcp-trader

# Run in HTTP server mode
docker run -e TIINGO_API_KEY=your_api_key_here -p 8000:8000 mcp-trader uv run mcp-trader --http
```

## Example Usage

In Claude Desktop, simply ask:

```
Analyze the technical setup for NVDA
```

The server will return a comprehensive technical analysis including trend status, momentum indicators, and key metrics.

![NVDA Technical Analysis](./technical-mcp.png)

For crypto analysis:

```
Analyze BTC using Binance data
```

## Project Structure

```
mcp-trader/
├── src/mcp_trader/
│   ├── __init__.py       # Package initialization
│   ├── server.py         # Main MCP server (simplified)
│   ├── config.py         # Simple configuration dataclass
│   ├── models.py         # Pydantic models for type safety
│   ├── data.py           # Market data providers
│   ├── indicators.py     # Technical analysis calculations
│   └── tests/            # Comprehensive test suite
├── .env.example          # Example environment configuration
├── pyproject.toml        # Project dependencies
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **"TIINGO_API_KEY not set" error**
   - Copy `.env.example` to `.env`
   - Add your Tiingo API key to the `.env` file

2. **Test failures**
   - Ensure all dependencies are installed: `uv sync`
   - Run tests with verbose output: `pytest -v`

3. **Import errors**
   - Make sure you're in the virtual environment: `source .venv/bin/activate`
   - Reinstall dependencies: `uv sync --force-reinstall`

## Dependencies

Core dependencies:
- aiohttp >=3.11.11
- fastmcp >=0.4.2
- numpy >=1.26.4,<2.0
- pandas >=2.2.3
- pandas-ta >=0.3.14b0
- python-dotenv >=1.0.1
- setuptools >=75.8.0

Optional:
- ta-lib >=0.6.0 (for enhanced performance)

See [pyproject.toml](pyproject.toml) for the complete list.

## Learning Resources

### Understanding the Code

1. **Start with `server.py`**: The main entry point showing how MCP tools are defined
2. **Study `models.py`**: Learn about type-safe request/response handling with Pydantic
3. **Explore `indicators.py`**: See how technical analysis calculations are implemented
4. **Review tests**: The test suite demonstrates proper usage of each component

### Key Concepts

- **MCP Tools**: Functions exposed to AI assistants via the Model Context Protocol
- **Technical Indicators**: Mathematical calculations on price/volume data
- **Type Safety**: Using Pydantic models for validation and documentation
- **Async Programming**: All tools use async/await for concurrent operations

## Contributing

Contributions that improve clarity and learning are especially welcome:

1. Fork the repository
2. Create a feature branch
3. Write clear, well-tested code
4. Ensure tests pass with good coverage
5. Submit a pull request

## Contributors

- [@wshobson](https://github.com/wshobson)
- [@zd87pl](https://github.com/zd87pl)
- [@calclavia](https://github.com/calclavia)

## Future Plans

- **Portfolio Analysis**: Tools for analyzing and optimizing portfolios
- **Backtesting**: Test trading strategies on historical data
- **Sentiment Analysis**: Integration with news and social media data
- **Options Analysis**: Tools for options strategies and pricing
- **Real-time Data**: Support for real-time market feeds
- **Custom Strategies**: Framework for custom trading strategies
- **Alerts**: Price and technical indicator notifications

## Further Reading

Learn more about this project:

- [Building a Stock Analysis Server with MCP, Part 1](https://sethhobson.com/2025/01/building-a-stock-analysis-server-with-mcp-part-1/) - Initial setup and core features
- [Building a Stock Analysis Server with MCP, Part 2](https://sethhobson.com/2025/03/building-a-stock-analysis-server-with-mcp-part-2/) - Advanced analysis tools

## License

This project is licensed under the MIT License - see the LICENSE file for details.