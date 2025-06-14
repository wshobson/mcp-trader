from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from src.mcp_trader.data import MarketData


@pytest.mark.asyncio
async def test_get_crypto_historical_data_tiingo_success():
    mock_response = [
        {
            "ticker": "btcusd",
            "priceData": [
                {
                    "date": "2024-05-01T00:00:00Z",
                    "open": 60000,
                    "high": 60500,
                    "low": 59500,
                    "close": 60200,
                    "volume": 1000,
                },
                {
                    "date": "2024-05-02T00:00:00Z",
                    "open": 60200,
                    "high": 61000,
                    "low": 60000,
                    "close": 60800,
                    "volume": 1200,
                },
            ],
        }
    ]
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_session.__aenter__.return_value = mock_response_obj
        mock_get.return_value = mock_session

        md = MarketData()
        df = await md.get_crypto_historical_data("BTC", lookback_days=2, provider="tiingo")
        assert isinstance(df, pd.DataFrame)
        assert "open" in df.columns
        assert df.shape[0] == 2


@pytest.mark.asyncio
async def test_get_crypto_historical_data_binance_success():
    mock_response = [
        [
            1714521600000,
            "60000",
            "60500",
            "59500",
            "60200",
            "1000",
            1714607999999,
            "0",
            0,
            "0",
            "0",
            "0",
        ],
        [
            1714608000000,
            "60200",
            "61000",
            "60000",
            "60800",
            "1200",
            1714694399999,
            "0",
            0,
            "0",
            "0",
            "0",
        ],
    ]
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_session.__aenter__.return_value = mock_response_obj
        mock_get.return_value = mock_session

        md = MarketData()
        df = await md.get_crypto_historical_data("BTCUSDT", lookback_days=2, provider="binance")
        assert isinstance(df, pd.DataFrame)
        assert "open" in df.columns
        assert df.shape[0] == 2


@pytest.mark.asyncio
async def test_get_crypto_historical_data_tiingo_no_data():
    mock_response = [{"ticker": "btcusd", "priceData": []}]
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_session.__aenter__.return_value = mock_response_obj
        mock_get.return_value = mock_session

        md = MarketData()
        with pytest.raises(ValueError):
            await md.get_crypto_historical_data("BTC", lookback_days=2, provider="tiingo")


@pytest.mark.asyncio
async def test_get_crypto_historical_data_binance_no_data():
    mock_response = []
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_session.__aenter__.return_value = mock_response_obj
        mock_get.return_value = mock_session

        md = MarketData()
        with pytest.raises(ValueError):
            await md.get_crypto_historical_data("BTCUSDT", lookback_days=2, provider="binance")
