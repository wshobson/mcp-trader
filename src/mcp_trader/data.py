import os
import aiohttp
import pandas as pd

from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class MarketData:
    """Handles all market data fetching operations."""

    def __init__(self):
        self.api_key = os.getenv("TIINGO_API_KEY")
        if not self.api_key:
            raise ValueError("TIINGO_API_KEY not found in environment")

        self.headers = {"Content-Type": "application/json", "Authorization": f"Token {self.api_key}"}

    async def get_crypto_historical_data(
        self,
        symbol: str,
        lookback_days: int = 365,
        provider: str = "tiingo",
        quote_currency: str = "usd"
    ) -> pd.DataFrame:
        """
        Fetch historical daily data for a given crypto asset.

        Args:
            symbol (str): The crypto symbol (e.g., 'BTC', 'ETH', or 'BTCUSDT' for Binance).
            lookback_days (int): Number of days to look back from today.
            provider (str): 'tiingo' or 'binance'.
            quote_currency (str): Quote currency (default 'usd' for Tiingo, 'USDT' for Binance).

        Returns:
            pd.DataFrame: DataFrame containing historical crypto market data.

        Raises:
            ValueError: If the symbol is invalid or no data is returned.
            Exception: For other unexpected issues during the fetch operation.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)

        if provider.lower() == "tiingo":
            # Tiingo expects symbols like 'btcusd'
            pair = f"{symbol.lower()}{quote_currency.lower()}"
            url = (
                f"https://api.tiingo.com/tiingo/crypto/prices?"
                f"tickers={pair}&"
                f"startDate={start_date.strftime('%Y-%m-%d')}&"
                f"endDate={end_date.strftime('%Y-%m-%d')}&"
                f"resampleFreq=1day"
            )
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 404:
                            raise ValueError(f"Crypto symbol not found: {symbol}")
                        response.raise_for_status()
                        data = await response.json()

                if not data or not data[0].get("priceData"):
                    raise ValueError(f"No data returned for {symbol} on Tiingo")

                df = pd.DataFrame(data[0]["priceData"])
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
                df["open"] = df["open"].astype(float)
                df["high"] = df["high"].astype(float)
                df["low"] = df["low"].astype(float)
                df["close"] = df["close"].astype(float)
                df["volume"] = df["volume"].astype(float)
                df["symbol"] = pair.upper()
                return df

            except aiohttp.ClientError as e:
                raise ConnectionError(f"Network error while fetching crypto data for {symbol} (Tiingo): {e}")
            except ValueError as ve:
                raise ve
            except Exception as e:
                raise Exception(f"Unexpected error fetching crypto data for {symbol} (Tiingo): {e}")

        elif provider.lower() == "binance":
            # Binance expects symbols like 'BTCUSDT'
            binance_symbol = symbol.upper()
            interval = "1d"
            limit = min(lookback_days, 1000)  # Binance max 1000
            url = (
                f"https://api.binance.com/api/v3/klines?"
                f"symbol={binance_symbol}&interval={interval}&limit={limit}"
            )
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(url) as response:
                        if response.status == 404:
                            raise ValueError(f"Crypto symbol not found: {symbol}")
                        response.raise_for_status()
                        data = await response.json()

                if not data:
                    raise ValueError(f"No data returned for {symbol} on Binance")

                # Binance kline columns:
                # 0: open time, 1: open, 2: high, 3: low, 4: close, 5: volume, 6: close time, ...
                df = pd.DataFrame(data, columns=[
                    "open_time", "open", "high", "low", "close", "volume",
                    "close_time", "quote_asset_volume", "number_of_trades",
                    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
                ])
                df["date"] = pd.to_datetime(df["open_time"], unit="ms")
                df.set_index("date", inplace=True)
                df["open"] = df["open"].astype(float)
                df["high"] = df["high"].astype(float)
                df["low"] = df["low"].astype(float)
                df["close"] = df["close"].astype(float)
                df["volume"] = df["volume"].astype(float)
                df["symbol"] = binance_symbol
                return df[["open", "high", "low", "close", "volume", "symbol"]]

            except aiohttp.ClientError as e:
                raise ConnectionError(f"Network error while fetching crypto data for {symbol} (Binance): {e}")
            except ValueError as ve:
                raise ve
            except Exception as e:
                raise Exception(f"Unexpected error fetching crypto data for {symbol} (Binance): {e}")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def get_historical_data(self, symbol: str, lookback_days: int = 365) -> pd.DataFrame:
        """
        Fetch historical daily data for a given symbol.

        Args:
            symbol (str): The stock symbol to fetch data for.
            lookback_days (int): Number of days to look back from today.

        Returns:
            pd.DataFrame: DataFrame containing historical market data.

        Raises:
            ValueError: If the symbol is invalid or no data is returned.
            Exception: For other unexpected issues during the fetch operation.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        url = (
            f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?"
            f'startDate={start_date.strftime("%Y-%m-%d")}&'
            f'endDate={end_date.strftime("%Y-%m-%d")}'
        )

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 404:
                        raise ValueError(f"Symbol not found: {symbol}")
                    response.raise_for_status()
                    data = await response.json()

            if not data:
                raise ValueError(f"No data returned for {symbol}")

            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

            df[["open", "high", "low", "close"]] = df[["adjOpen", "adjHigh", "adjLow", "adjClose"]].round(2)
            df["volume"] = df["adjVolume"].astype(int)
            df["symbol"] = symbol.upper()

            return df

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Network error while fetching data for {symbol}: {e}")
        except ValueError as ve:
            raise ve  # Propagate value errors (symbol issues, no data, etc.)
        except Exception as e:
            raise Exception(f"Unexpected error fetching data for {symbol}: {e}")
