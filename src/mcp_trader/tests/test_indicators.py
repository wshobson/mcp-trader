"""Tests for technical indicators module."""

import pandas as pd
import pytest
import numpy as np
from datetime import datetime, timedelta

from mcp_trader.indicators import TechnicalAnalysis


def create_test_df(days=100):
    """Create a test DataFrame with OHLCV data."""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Create realistic price data
    np.random.seed(42)
    base_price = 100
    prices = []
    
    for i in range(days):
        # Add some trend and volatility
        trend = i * 0.1
        noise = np.random.randn() * 2
        price = base_price + trend + noise
        prices.append(price)
    
    # Create OHLCV data
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p + np.random.rand() * 2 for p in prices],
        'low': [p - np.random.rand() * 2 for p in prices],
        'close': [p + np.random.randn() * 0.5 for p in prices],
        'volume': [1000000 + np.random.randint(-100000, 100000) for _ in range(days)]
    })
    
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    return df


class TestTechnicalAnalysis:
    """Test cases for TechnicalAnalysis class."""
    
    def test_add_core_indicators(self):
        """Test adding core technical indicators."""
        df = create_test_df(250)  # Enough data for 200 SMA
        result = TechnicalAnalysis.add_core_indicators(df)
        
        # Check that all indicators were added
        expected_columns = [
            'sma_20', 'sma_50', 'sma_200',
            'adrp', 'avg_20d_vol', 'atr', 'rsi',
            'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'
        ]
        
        for col in expected_columns:
            assert col in result.columns, f"Missing indicator: {col}"
        
        # Verify some calculations
        assert not result['sma_20'].iloc[19:].isna().any()
        assert not result['sma_50'].iloc[49:].isna().any()
        assert not result['sma_200'].iloc[199:].isna().any()
        
        # RSI should be between 0 and 100
        rsi_values = result['rsi'].dropna()
        assert (rsi_values >= 0).all() and (rsi_values <= 100).all()
    
    def test_add_core_indicators_missing_column(self):
        """Test error handling when required column is missing."""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            # Missing 'low' and 'close' columns
            'volume': [1000, 1100, 1200]
        })
        
        with pytest.raises(KeyError, match="Missing column"):
            TechnicalAnalysis.add_core_indicators(df)
    
    def test_check_trend_status(self):
        """Test trend status analysis."""
        df = create_test_df(250)
        df = TechnicalAnalysis.add_core_indicators(df)
        
        status = TechnicalAnalysis.check_trend_status(df)
        
        # Check all expected keys are present
        expected_keys = [
            'above_20sma', 'above_50sma', 'above_200sma',
            '20_50_bullish', '50_200_bullish', 'rsi', 'macd_bullish'
        ]
        
        for key in expected_keys:
            assert key in status, f"Missing key: {key}"
        
        # Verify boolean values
        assert status['above_20sma'] in [True, False]
        assert status['above_50sma'] in [True, False]
        assert status['above_200sma'] in [True, False]
        assert status['20_50_bullish'] in [True, False]
        assert status['50_200_bullish'] in [True, False]
        assert status['macd_bullish'] in [True, False]
        
        # RSI should be a float
        assert isinstance(status['rsi'], (float, np.floating))
    
    def test_check_trend_status_empty_df(self):
        """Test error handling for empty DataFrame."""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame is empty"):
            TechnicalAnalysis.check_trend_status(df)
    
    def test_macd_analysis(self):
        """Test MACD analysis functionality."""
        df = create_test_df(250)  # Need more data for 200 SMA
        df = TechnicalAnalysis.add_core_indicators(df)
        
        # Verify MACD columns exist
        assert 'MACD_12_26_9' in df.columns
        assert 'MACDh_12_26_9' in df.columns
        assert 'MACDs_12_26_9' in df.columns
        
        # Test trend status includes MACD signal
        status = TechnicalAnalysis.check_trend_status(df)
        assert 'macd_bullish' in status
        assert status['macd_bullish'] in [True, False]
    
    def test_volume_analysis(self):
        """Test volume-based indicators."""
        df = create_test_df(50)
        df = TechnicalAnalysis.add_core_indicators(df)
        
        # Check volume indicators
        assert 'avg_20d_vol' in df.columns
        
        # Verify calculations
        manual_avg = df['volume'].rolling(window=20).mean()
        pd.testing.assert_series_equal(
            df['avg_20d_vol'].iloc[19:],
            manual_avg.iloc[19:],
            check_names=False
        )
    
    def test_volatility_indicators(self):
        """Test volatility indicators like ATR and ADRP."""
        df = create_test_df(50)
        df = TechnicalAnalysis.add_core_indicators(df)
        
        # Check volatility indicators
        assert 'atr' in df.columns
        assert 'adrp' in df.columns
        
        # ATR should be positive
        atr_values = df['atr'].dropna()
        assert (atr_values > 0).all()
        
        # ADRP should be a reasonable percentage
        adrp_values = df['adrp'].dropna()
        assert (adrp_values > 0).all()
        assert (adrp_values < 20).all()  # Assuming less than 20% daily range