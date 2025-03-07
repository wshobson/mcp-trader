# MCP Trader Server

[![smithery badge](https://smithery.ai/badge/mcp-trader)](https://smithery.ai/server/mcp-trader)

A Model Context Protocol (MCP) server for stock traders.

## Features

### Tools

The server provides the following tools for stock analysis and trading:

- **analyze-stock**: Performs technical analysis on a given stock symbol

  - Required argument: `symbol` (string, e.g. "NVDA")
  - Returns comprehensive technical analysis including:
    - Moving average trends (20, 50, 200 SMA)
    - Momentum indicators (RSI, MACD)
    - Volatility metrics (ATR, ADRP)
    - Volume analysis

- **relative-strength**: Calculates a stock's relative strength compared to a benchmark

  - Required argument: `symbol` (string, e.g. "AAPL")
  - Optional argument: `benchmark` (string, default: "SPY")
  - Returns relative strength metrics across multiple timeframes (21, 63, 126, 252 days)
  - Includes performance comparison between the stock and benchmark

- **volume-profile**: Analyzes volume distribution by price

  - Required argument: `symbol` (string, e.g. "MSFT")
  - Optional argument: `lookback_days` (integer, default: 60)
  - Returns volume profile analysis including:
    - Point of Control (POC) - price level with highest volume
    - Value Area (70% of volume range)
    - Top volume price levels

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
  - Returns recommended position size, dollar risk, and potential profit targets

- **suggest-stops**: Suggests stop loss levels based on technical analysis
  - Required argument: `symbol` (string, e.g. "META")
  - Returns multiple stop loss suggestions based on:
    - ATR-based stops (1x, 2x, 3x ATR)
    - Percentage-based stops (2%, 5%, 8%)
    - Technical levels (moving averages, recent swing lows)

### Technical Analysis Capabilities

The server leverages several specialized analysis modules:

- **TechnicalAnalysis**: Core technical indicators and trend analysis

  - Moving averages (SMA 20, 50, 200)
  - Momentum indicators (RSI, MACD)
  - Volatility metrics (ATR, Average Daily Range Percentage)
  - Volume analysis (20-day average volume)

- **RelativeStrength**: Comparative performance analysis

  - Multi-timeframe relative strength scoring (21, 63, 126, 252 days)
  - Performance comparison against benchmark indices
  - Outperformance/underperformance classification

- **VolumeProfile**: Advanced volume analysis

  - Price level volume distribution
  - Point of Control (POC) identification
  - Value Area calculation (70% of volume)

- **PatternRecognition**: Chart pattern detection

  - Support/resistance levels
  - Common chart patterns (head and shoulders, double tops/bottoms, etc.)
  - Confidence scoring for detected patterns

- **RiskAnalysis**: Position sizing and risk management
  - Risk-based position sizing
  - Multiple stop loss strategies
  - R-multiple profit target calculation

### Data Sources

The server uses the [Tiingo API](https://api.tiingo.com/) for market data:

- Historical daily OHLCV data
- Adjusted prices for accurate backtesting
- Up to 1 year of historical data by default

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

This will:

1. Install the MCP Trader server
2. Configure it with your Tiingo API key
3. Set up the Claude Desktop integration

#### Smithery Configuration

The server includes a `smithery.yaml` configuration file that defines:

- Required configuration parameters (Tiingo API key)
- Command function to start the MCP server
- Integration with Claude Desktop

You can customize the Smithery configuration by editing the `smithery.yaml` file.

### Installation

```bash
uv venv --python 3.11
source .venv/bin/activate # On Windows: .venv\Scripts\activate
uv sync
```

### Docker Deployment

The project includes a Dockerfile for containerized deployment:

```bash
# Build the Docker image
docker build -t mcp-trader .

# Run the container with your API key
docker run -e TIINGO_API_KEY=your_api_key_here -p 8000:8000 mcp-trader
```

To run the container in HTTP server mode:

```bash
docker run -e TIINGO_API_KEY=your_api_key_here -p 8000:8000 mcp-trader uv run mcp-trader --http
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

### HTTP Server Mode

The server can also run as a standalone HTTP server for testing or integration with other applications:

```bash
uv run mcp-trader --http
```

This starts an HTTP server on http://localhost:8000 with the following endpoints:

- **GET /list-tools**: Returns a list of available tools and their schemas
- **POST /call-tool**: Executes a tool with the provided arguments
  - Request body format:
    ```json
    {
      "name": "analyze-stock",
      "arguments": {
        "symbol": "AAPL"
      }
    }
    ```
  - Returns an array of content items (text, images, etc.)

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
- numpy ==1.26.4
- pandas >=2.2.3
- pandas-ta >=0.3.14b0
- python-dotenv >=1.0.1
- setuptools >=75.8.0
- ta-lib >=0.6.0
```

## Contributing

Contributions to MCP Trader are welcome! Here are some ways you can contribute:

- **Add new tools**: Implement additional technical analysis tools or trading strategies
- **Improve existing tools**: Enhance the accuracy or performance of current tools
- **Add data sources**: Integrate additional market data providers
- **Documentation**: Improve the documentation or add examples
- **Bug fixes**: Fix issues or improve error handling

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Plans

The MCP Trader project has several planned enhancements:

- **Portfolio Analysis**: Tools for analyzing and optimizing portfolios
- **Backtesting**: Capabilities to test trading strategies on historical data
- **Sentiment Analysis**: Integration with news and social media sentiment data
- **Options Analysis**: Tools for analyzing options strategies and pricing
- **Real-time Data**: Support for real-time market data feeds
- **Custom Strategies**: Framework for implementing and testing custom trading strategies
- **Alerts**: Notification system for price and technical indicator alerts

## Further Reading

Learn more about this project through these detailed blog posts:

- [Building a Stock Analysis Server with MCP, Part 1](https://sethhobson.com/2025/01/building-a-stock-analysis-server-with-mcp-part-1/) - Initial setup, architecture, and core technical analysis features
- [Building a Stock Analysis Server with MCP, Part 2](https://sethhobson.com/2025/03/building-a-stock-analysis-server-with-mcp-part-2/) - Relative Strength, Volume, Pattern Recognition, Risk analysis
