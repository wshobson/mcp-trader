import pandas as pd
import pandas_ta as ta

from typing import Dict, Any


class TechnicalAnalysis:
    """Technical analysis toolkit with improved performance and readability."""

    @staticmethod
    def add_core_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add a core set of technical indicators."""
        try:
            # Adding trend indicators
            df["sma_20"] = ta.sma(df["close"], length=20)
            df["sma_50"] = ta.sma(df["close"], length=50)
            df["sma_200"] = ta.sma(df["close"], length=200)

            # Adding volatility indicators and volume
            daily_range = df["high"].sub(df["low"])
            adr = daily_range.rolling(window=20).mean()
            df["adrp"] = adr.div(df["close"]).mul(100)
            df["avg_20d_vol"] = df["volume"].rolling(window=20).mean()

            # Adding momentum indicators
            df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
            df["rsi"] = ta.rsi(df["close"], length=14)
            macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
            if macd is not None:
                df = pd.concat([df, macd], axis=1)

            return df

        except KeyError as e:
            raise KeyError(f"Missing column in input DataFrame: {str(e)}")
        except Exception as e:
            raise Exception(f"Error calculating indicators: {str(e)}")

    @staticmethod
    def check_trend_status(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the current trend status."""
        if df.empty:
            raise ValueError("DataFrame is empty. Ensure it contains valid data.")

        latest = df.iloc[-1]
        return {
            "above_20sma": latest["close"] > latest["sma_20"],
            "above_50sma": latest["close"] > latest["sma_50"],
            "above_200sma": latest["close"] > latest["sma_200"],
            "20_50_bullish": latest["sma_20"] > latest["sma_50"],
            "50_200_bullish": latest["sma_50"] > latest["sma_200"],
            "rsi": latest["rsi"],
            "macd_bullish": latest.get("MACD_12_26_9", 0) > latest.get("MACDs_12_26_9", 0),
        }
