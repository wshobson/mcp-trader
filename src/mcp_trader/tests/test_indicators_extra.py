"""Additional tests for indicators module to improve coverage."""

import pandas as pd
import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from mcp_trader.indicators import RelativeStrength, VolumeProfile, PatternRecognition, RiskAnalysis


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
    df.set_index('date', inplace=True)
    
    return df


class TestRelativeStrength:
    """Test cases for RelativeStrength class."""
    
    @pytest.mark.asyncio
    async def test_calculate_rs_success(self):
        """Test successful relative strength calculation."""
        # Mock market data
        mock_market_data = AsyncMock()
        
        stock_df = create_test_df(300)
        benchmark_df = create_test_df(300)
        
        mock_market_data.get_historical_data.side_effect = [stock_df, benchmark_df]
        
        rs_scores = await RelativeStrength.calculate_rs(
            mock_market_data, "AAPL", "SPY", [21, 63]
        )
        
        # Check structure
        assert 'RS_21d' in rs_scores
        assert 'RS_63d' in rs_scores
        assert 'Return_21d' in rs_scores
        assert 'Return_63d' in rs_scores
        assert 'Benchmark_21d' in rs_scores
        assert 'Benchmark_63d' in rs_scores
        assert 'Excess_21d' in rs_scores
        assert 'Excess_63d' in rs_scores
        
        # Verify RS scores are in valid range
        assert 1 <= rs_scores['RS_21d'] <= 99
        assert 1 <= rs_scores['RS_63d'] <= 99
    
    @pytest.mark.asyncio
    async def test_calculate_rs_insufficient_data(self):
        """Test RS calculation with insufficient data."""
        mock_market_data = AsyncMock()
        
        # Create DataFrames with insufficient data
        stock_df = create_test_df(50)
        benchmark_df = create_test_df(50)
        
        mock_market_data.get_historical_data.side_effect = [stock_df, benchmark_df]
        
        # Should skip periods with insufficient data
        rs_scores = await RelativeStrength.calculate_rs(
            mock_market_data, "AAPL", "SPY", [21, 63, 252]
        )
        
        # 21-day should be present, but not 252-day
        assert 'RS_21d' in rs_scores
        assert 'RS_252d' not in rs_scores


class TestVolumeProfile:
    """Test cases for VolumeProfile class."""
    
    def test_analyze_volume_profile_success(self):
        """Test successful volume profile analysis."""
        df = create_test_df(50)
        
        profile = VolumeProfile.analyze_volume_profile(df, num_bins=10)
        
        # Check structure
        assert 'price_min' in profile
        assert 'price_max' in profile
        assert 'bin_width' in profile
        assert 'bins' in profile
        assert 'point_of_control' in profile
        assert 'value_area_low' in profile
        assert 'value_area_high' in profile
        
        # Verify bins
        assert len(profile['bins']) == 10
        
        # Check each bin
        for bin_data in profile['bins']:
            assert 'price_low' in bin_data
            assert 'price_high' in bin_data
            assert 'price_mid' in bin_data
            assert 'volume' in bin_data
            assert 'volume_percent' in bin_data
            assert 0 <= bin_data['volume_percent'] <= 100
        
        # Verify value area relationships
        assert profile['value_area_low'] <= profile['point_of_control']
        assert profile['point_of_control'] <= profile['value_area_high']
    
    def test_analyze_volume_profile_insufficient_data(self):
        """Test volume profile with insufficient data."""
        df = create_test_df(10)
        
        with pytest.raises(Exception, match="Error analyzing volume profile"):
            VolumeProfile.analyze_volume_profile(df)


class TestPatternRecognition:
    """Test cases for PatternRecognition class."""
    
    def test_detect_patterns_sufficient_data(self):
        """Test pattern detection with sufficient data."""
        df = create_test_df(100)
        
        patterns = PatternRecognition.detect_patterns(df)
        
        # Check structure
        assert 'patterns' in patterns
        assert isinstance(patterns['patterns'], list)
        
        # If patterns found, verify structure
        for pattern in patterns['patterns']:
            assert 'type' in pattern
            assert 'confidence' in pattern
            if 'start_date' in pattern:
                assert 'end_date' in pattern
            if 'price_level' in pattern:
                assert isinstance(pattern['price_level'], (int, float))
    
    def test_detect_patterns_insufficient_data(self):
        """Test pattern detection with insufficient data."""
        df = create_test_df(30)
        
        patterns = PatternRecognition.detect_patterns(df)
        
        assert 'patterns' in patterns
        assert 'message' in patterns
        assert patterns['patterns'] == []
        assert "Not enough data" in patterns['message']


class TestRiskAnalysis:
    """Test cases for RiskAnalysis class."""
    
    def test_calculate_position_size_success(self):
        """Test successful position size calculation."""
        result = RiskAnalysis.calculate_position_size(
            price=100.0,
            stop_price=95.0,
            risk_amount=1000.0,
            account_size=50000.0,
            max_risk_percent=2.0
        )
        
        # Check structure
        assert 'recommended_shares' in result
        assert 'dollar_risk' in result
        assert 'risk_per_share' in result
        assert 'position_cost' in result
        assert 'account_percent_risked' in result
        assert 'r_multiples' in result
        
        # Verify calculations
        assert result['risk_per_share'] == 5.0
        assert result['recommended_shares'] == 200
        assert result['dollar_risk'] == 1000.0
        assert result['position_cost'] == 20000.0
        assert result['account_percent_risked'] == 2.0
        
        # Check R-multiples
        assert result['r_multiples']['r1'] == 105.0
        assert result['r_multiples']['r2'] == 110.0
        assert result['r_multiples']['r3'] == 115.0
    
    def test_calculate_position_size_invalid_inputs(self):
        """Test position size calculation with invalid inputs."""
        # Negative price
        with pytest.raises(Exception, match="Error calculating position size"):
            RiskAnalysis.calculate_position_size(
                price=-100.0,
                stop_price=95.0,
                risk_amount=1000.0,
                account_size=50000.0
            )
        
        # Stop price above entry price for long position
        with pytest.raises(Exception, match="Error calculating position size"):
            RiskAnalysis.calculate_position_size(
                price=100.0,
                stop_price=105.0,
                risk_amount=1000.0,
                account_size=50000.0
            )
        
        # Zero risk per share
        with pytest.raises(Exception, match="Error calculating position size"):
            RiskAnalysis.calculate_position_size(
                price=100.0,
                stop_price=100.0,
                risk_amount=1000.0,
                account_size=50000.0
            )
    
    def test_suggest_stop_levels_success(self):
        """Test successful stop level suggestions."""
        df = create_test_df(50)
        df['atr'] = 2.5  # Add ATR column
        df['sma_20'] = 98.0
        df['sma_50'] = 96.0
        
        stops = RiskAnalysis.suggest_stop_levels(df)
        
        # Check all expected stop types
        assert 'atr_1x' in stops
        assert 'atr_2x' in stops
        assert 'atr_3x' in stops
        assert 'percent_2' in stops
        assert 'percent_5' in stops
        assert 'percent_8' in stops
        assert 'sma_20' in stops
        assert 'sma_50' in stops
        assert 'recent_swing' in stops
        
        # Verify relationships
        assert stops['atr_1x'] > stops['atr_2x'] > stops['atr_3x']
        assert stops['percent_2'] > stops['percent_5'] > stops['percent_8']
    
    def test_suggest_stop_levels_insufficient_data(self):
        """Test stop levels with insufficient data."""
        df = create_test_df(10)
        
        with pytest.raises(Exception, match="Error suggesting stop levels"):
            RiskAnalysis.suggest_stop_levels(df)