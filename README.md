## Branch: feature/crypto-asset-data

This branch extends the project to support pulling and analyzing data for crypto assets, providing a robust foundation for trading system development.

---

## Crypto Asset Analysis

### Supported Providers

- **Tiingo Crypto API** (requires `TIINGO_API_KEY` in your environment)
- **Binance** (no API key required for public data)

### How to Use

The `analyze-crypto` tool allows you to analyze any crypto asset using technical indicators, with data sourced from either Tiingo or Binance.

#### Example: Analyze BTC with Tiingo

```json
{
  "name": "analyze-crypto",
  "arguments": {
    "symbol": "BTC",
    "provider": "tiingo",
    "lookback_days": 30,
    "quote_currency": "usd"
  }
}
```

#### Example: Analyze BTCUSDT with Binance

```json
{
  "name": "analyze-crypto",
  "arguments": {
    "symbol": "BTCUSDT",
    "provider": "binance",
    "lookback_days": 30
  }
}
```

- `symbol`: Crypto symbol (e.g., "BTC", "ETH", or "BTCUSDT" for Binance)
- `provider`: `"tiingo"` or `"binance"` (default: `"tiingo"`)
- `lookback_days`: Number of days of historical data (default: 365)
- `quote_currency`: For Tiingo, the quote currency (default: "usd")

### Environment Setup

- For Tiingo, set your API key:  
  ```bash
  export TIINGO_API_KEY=your_key_here
  ```

### Running Tests

Integration and unit tests are provided for both providers:

```bash
# Integration test (requires server running on http://localhost:8000)
python src/mcp_trader/tests/test_analyze_crypto.py

# Unit tests (pytest required)
pytest src/mcp_trader/tests/test_marketdata_crypto.py
```

---

For more details, see the code in `src/mcp_trader/data.py` and `src/mcp_trader/server.py`.
