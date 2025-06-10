import asyncio
import json
import aiohttp

async def test_analyze_crypto_tiingo():
    """Test the analyze-crypto tool with BTC (Tiingo)."""
    async with aiohttp.ClientSession() as session:
        payload = {
            "name": "analyze-crypto",
            "arguments": {
                "symbol": "BTC",
                "provider": "tiingo",
                "lookback_days": 30,
                "quote_currency": "usd"
            },
        }
        async with session.post(
            "http://localhost:8000/call-tool", json=payload
        ) as response:
            print(f"Tiingo status: {response.status}")
            result = await response.json()
            print(json.dumps(result, indent=2))

async def test_analyze_crypto_binance():
    """Test the analyze-crypto tool with BTCUSDT (Binance)."""
    async with aiohttp.ClientSession() as session:
        payload = {
            "name": "analyze-crypto",
            "arguments": {
                "symbol": "BTCUSDT",
                "provider": "binance",
                "lookback_days": 30
            },
        }
        async with session.post(
            "http://localhost:8000/call-tool", json=payload
        ) as response:
            print(f"Binance status: {response.status}")
            result = await response.json()
            print(json.dumps(result, indent=2))

async def main():
    await test_analyze_crypto_tiingo()
    await test_analyze_crypto_binance()

if __name__ == "__main__":
    asyncio.run(main())
