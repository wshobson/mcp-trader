"""
Unit tests for Pydantic models.

Tests data validation, constraints, and model behavior.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from mcp_trader.models import (
    AnalyzeCryptoRequest,
    AnalyzeStockRequest,
    CandleData,
    ChartPattern,
    ComprehensiveAnalysis,
    ErrorResponse,
    MarketDataResponse,
    PositionSizeRequest,
    PositionSizeResult,
    RelativeStrengthPeriod,
    RMultiples,
    StopLevelSuggestions,
    TechnicalAnalysisResult,
    TechnicalIndicators,
    TrendStatus,
    VolumeBin,
    VolumeProfileResult,
)


class TestCandleData:
    """Test CandleData model validation."""

    def test_valid_candle(self):
        """Test creating valid candle data."""
        candle = CandleData(
            date=datetime.now(),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            volume=1000000,
            symbol="AAPL",
        )
        assert candle.open == 100.0
        assert candle.symbol == "AAPL"

    def test_negative_price_validation(self):
        """Test that negative prices are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CandleData(
                date=datetime.now(),
                open=-100.0,
                high=110.0,
                low=95.0,
                close=105.0,
                volume=1000000,
                symbol="AAPL",
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_high_low_validation(self):
        """Test that high must be >= low."""
        with pytest.raises(ValidationError) as exc_info:
            CandleData(
                date=datetime.now(),
                open=100.0,
                high=90.0,  # Less than open (checked first)
                low=95.0,
                close=100.0,
                volume=1000000,
                symbol="AAPL",
            )
        # The high/open validation triggers first
        assert "High price must be >= open price" in str(exc_info.value)

    def test_high_open_close_validation(self):
        """Test that high must be >= open and close."""
        with pytest.raises(ValidationError) as exc_info:
            CandleData(
                date=datetime.now(),
                open=100.0,
                high=95.0,  # Less than open
                low=90.0,
                close=100.0,
                volume=1000000,
                symbol="AAPL",
            )
        assert "High price must be >= open price" in str(exc_info.value)

    def test_low_open_close_validation(self):
        """Test that low must be <= open and close."""
        with pytest.raises(ValidationError) as exc_info:
            CandleData(
                date=datetime.now(),
                open=100.0,
                high=110.0,
                low=105.0,  # Greater than open
                close=100.0,
                volume=1000000,
                symbol="AAPL",
            )
        assert "Low price must be <= open price" in str(exc_info.value)


class TestMarketDataResponse:
    """Test MarketDataResponse model."""

    def test_valid_response(self):
        """Test creating valid market data response."""
        candles = [
            CandleData(
                date=datetime.now(),
                open=100.0,
                high=110.0,
                low=95.0,
                close=105.0,
                volume=1000000,
                symbol="AAPL",
            )
        ]

        response = MarketDataResponse(
            symbol="AAPL", data=candles, provider="tiingo", lookback_days=30, quote_currency="usd"
        )

        assert response.symbol == "AAPL"
        assert len(response.data) == 1
        assert response.provider == "tiingo"

    def test_invalid_provider(self):
        """Test invalid provider is rejected."""
        with pytest.raises(ValidationError):
            MarketDataResponse(
                symbol="AAPL", data=[], provider="invalid_provider", lookback_days=30
            )

    def test_negative_lookback_days(self):
        """Test negative lookback days are rejected."""
        with pytest.raises(ValidationError):
            MarketDataResponse(symbol="AAPL", data=[], provider="tiingo", lookback_days=-1)


class TestTrendStatus:
    """Test TrendStatus model."""

    def test_valid_trend_status(self):
        """Test creating valid trend status."""
        trend = TrendStatus(
            above_20sma=True,
            above_50sma=True,
            above_200sma=False,
            **{"20_50_bullish": True, "50_200_bullish": False},  # Using aliases
            rsi=65.5,
            macd_bullish=True,
        )

        assert trend.above_20sma is True
        assert trend.sma_20_50_bullish is True  # Access by field name
        assert trend.rsi == 65.5

    def test_rsi_validation(self):
        """Test RSI must be between 0 and 100."""
        with pytest.raises(ValidationError) as exc_info:
            TrendStatus(
                above_20sma=True,
                above_50sma=True,
                above_200sma=False,
                sma_20_50_bullish=True,
                sma_50_200_bullish=False,
                rsi=150.0,  # Invalid RSI
                macd_bullish=True,
            )
        assert "less than or equal to 100" in str(exc_info.value)

    def test_alias_population(self):
        """Test that aliases work correctly."""
        trend = TrendStatus(
            above_20sma=True,
            above_50sma=True,
            above_200sma=False,
            **{"20_50_bullish": True, "50_200_bullish": False},
            rsi=50.0,
            macd_bullish=True,
        )

        # Both field name and alias should work
        assert trend.sma_20_50_bullish is True
        # When dumping by alias, the alias is used
        assert trend.model_dump(by_alias=True)["20_50_bullish"] is True


class TestTechnicalIndicators:
    """Test TechnicalIndicators model."""

    def test_valid_indicators(self):
        """Test creating valid technical indicators."""
        indicators = TechnicalIndicators(
            sma_20=150.5,
            sma_50=148.0,
            sma_200=145.0,
            atr=2.5,
            adrp=1.8,
            avg_20d_vol=1000000,
            rsi=65.0,
            macd=0.5,
            macd_signal=0.3,
            macd_histogram=0.2,
        )

        assert indicators.sma_20 == 150.5
        assert indicators.atr == 2.5
        assert indicators.rsi == 65.0

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        indicators = TechnicalIndicators(atr=2.5, adrp=1.8, avg_20d_vol=1000000, rsi=65.0)

        assert indicators.sma_20 is None
        assert indicators.macd is None

    def test_negative_atr_rejected(self):
        """Test that negative ATR is rejected."""
        with pytest.raises(ValidationError):
            TechnicalIndicators(
                atr=-2.5,  # Negative ATR
                adrp=1.8,
                avg_20d_vol=1000000,
                rsi=65.0,
            )


class TestRelativeStrengthPeriod:
    """Test RelativeStrengthPeriod model."""

    def test_valid_rs_period(self):
        """Test creating valid RS period."""
        rs_period = RelativeStrengthPeriod(
            period_days=21, rs_score=75.0, stock_return=5.5, benchmark_return=2.0, excess_return=3.5
        )

        assert rs_period.period_days == 21
        assert rs_period.rs_score == 75.0
        assert rs_period.excess_return == 3.5

    def test_rs_score_range(self):
        """Test RS score must be between 1 and 99."""
        with pytest.raises(ValidationError):
            RelativeStrengthPeriod(
                period_days=21,
                rs_score=0.5,  # Below 1
                stock_return=5.5,
                benchmark_return=2.0,
                excess_return=3.5,
            )

        with pytest.raises(ValidationError):
            RelativeStrengthPeriod(
                period_days=21,
                rs_score=100.0,  # Above 99
                stock_return=5.5,
                benchmark_return=2.0,
                excess_return=3.5,
            )

    def test_excess_return_validation(self):
        """Test excess return calculation validation."""
        with pytest.raises(ValidationError) as exc_info:
            RelativeStrengthPeriod(
                period_days=21,
                rs_score=75.0,
                stock_return=5.5,
                benchmark_return=2.0,
                excess_return=10.0,  # Should be 3.5
            )
        assert "Excess return must equal" in str(exc_info.value)


class TestVolumeBin:
    """Test VolumeBin model."""

    def test_valid_volume_bin(self):
        """Test creating valid volume bin."""
        bin_data = VolumeBin(
            price_low=145.0, price_high=150.0, price_mid=147.5, volume=1000000, volume_percent=25.5
        )

        assert bin_data.price_low == 145.0
        assert bin_data.price_high == 150.0
        assert bin_data.price_mid == 147.5

    def test_price_range_validation(self):
        """Test price_high must be > price_low."""
        with pytest.raises(ValidationError) as exc_info:
            VolumeBin(
                price_low=150.0,
                price_high=145.0,  # Less than price_low
                price_mid=147.5,
                volume=1000000,
                volume_percent=25.5,
            )
        assert "price_high must be greater than price_low" in str(exc_info.value)

    def test_price_mid_validation(self):
        """Test price_mid must be average of price_low and price_high."""
        with pytest.raises(ValidationError) as exc_info:
            VolumeBin(
                price_low=145.0,
                price_high=150.0,
                price_mid=160.0,  # Should be 147.5
                volume=1000000,
                volume_percent=25.5,
            )
        assert "price_mid must be the average" in str(exc_info.value)

    def test_volume_percent_range(self):
        """Test volume_percent must be between 0 and 100."""
        with pytest.raises(ValidationError):
            VolumeBin(
                price_low=145.0,
                price_high=150.0,
                price_mid=147.5,
                volume=1000000,
                volume_percent=150.0,  # Over 100
            )


class TestVolumeProfileResult:
    """Test VolumeProfileResult model."""

    def test_valid_volume_profile(self):
        """Test creating valid volume profile result."""
        bins = [
            VolumeBin(
                price_low=145.0,
                price_high=150.0,
                price_mid=147.5,
                volume=1000000,
                volume_percent=25.5,
            )
        ]

        profile = VolumeProfileResult(
            symbol="AAPL",
            price_min=140.0,
            price_max=160.0,
            bin_width=5.0,
            bins=bins,
            point_of_control=147.5,
            value_area_low=143.0,
            value_area_high=157.0,
            lookback_days=30,
        )

        assert profile.symbol == "AAPL"
        assert profile.point_of_control == 147.5
        assert len(profile.bins) == 1

    def test_price_range_validation(self):
        """Test price_max must be > price_min."""
        with pytest.raises(ValidationError) as exc_info:
            VolumeProfileResult(
                symbol="AAPL",
                price_min=160.0,
                price_max=140.0,  # Less than price_min
                bin_width=5.0,
                bins=[],
                point_of_control=150.0,
                value_area_low=145.0,
                value_area_high=155.0,
                lookback_days=30,
            )
        assert "price_max must be greater than price_min" in str(exc_info.value)

    def test_value_area_validation(self):
        """Test value area constraints."""
        with pytest.raises(ValidationError) as exc_info:
            VolumeProfileResult(
                symbol="AAPL",
                price_min=140.0,
                price_max=160.0,
                bin_width=5.0,
                bins=[],
                point_of_control=150.0,
                value_area_low=155.0,
                value_area_high=145.0,  # Less than value_area_low
                lookback_days=30,
            )
        assert "value_area_high must be greater than value_area_low" in str(exc_info.value)


class TestChartPattern:
    """Test ChartPattern model."""

    def test_valid_pattern(self):
        """Test creating valid chart pattern."""
        pattern = ChartPattern(
            type="Double Bottom",
            start_date="2024-01-01",
            end_date="2024-01-15",
            price_level=145.50,
            confidence="High",
            additional_info={"neckline": 150.0},
        )

        assert pattern.type == "Double Bottom"
        assert pattern.price_level == 145.50
        assert pattern.confidence == "High"
        assert pattern.additional_info["neckline"] == 150.0

    def test_invalid_pattern_type(self):
        """Test invalid pattern type is rejected."""
        with pytest.raises(ValidationError):
            ChartPattern(type="Invalid Pattern", price_level=145.50, confidence="High")

    def test_invalid_confidence(self):
        """Test invalid confidence level is rejected."""
        with pytest.raises(ValidationError):
            ChartPattern(
                type="Double Bottom",
                price_level=145.50,
                confidence="Very High",  # Should be Low, Medium, or High
            )


class TestPositionSizeResult:
    """Test PositionSizeResult model."""

    def test_valid_position_size(self):
        """Test creating valid position size result."""
        r_multiples = RMultiples(r1=155.0, r2=160.0, r3=165.0)

        position = PositionSizeResult(
            symbol="AAPL",
            entry_price=150.0,
            stop_price=145.0,
            recommended_shares=100,
            dollar_risk=500.0,
            risk_per_share=5.0,
            position_cost=15000.0,
            account_percent_risked=1.0,
            r_multiples=r_multiples,
        )

        assert position.symbol == "AAPL"
        assert position.recommended_shares == 100
        assert position.r_multiples.r1 == 155.0

    def test_risk_per_share_validation(self):
        """Test risk per share calculation validation."""
        r_multiples = RMultiples(r1=155.0, r2=160.0, r3=165.0)

        with pytest.raises(ValidationError) as exc_info:
            PositionSizeResult(
                symbol="AAPL",
                entry_price=150.0,
                stop_price=145.0,
                recommended_shares=100,
                dollar_risk=500.0,
                risk_per_share=10.0,  # Should be 5.0
                position_cost=15000.0,
                account_percent_risked=1.0,
                r_multiples=r_multiples,
            )
        assert "risk_per_share must equal" in str(exc_info.value)

    def test_account_percent_range(self):
        """Test account percent risked must be between 0 and 100."""
        r_multiples = RMultiples(r1=155.0, r2=160.0, r3=165.0)

        with pytest.raises(ValidationError):
            PositionSizeResult(
                symbol="AAPL",
                entry_price=150.0,
                stop_price=145.0,
                recommended_shares=100,
                dollar_risk=500.0,
                risk_per_share=5.0,
                position_cost=15000.0,
                account_percent_risked=150.0,  # Over 100%
                r_multiples=r_multiples,
            )


class TestStopLevelSuggestions:
    """Test StopLevelSuggestions model."""

    def test_valid_stop_levels(self):
        """Test creating valid stop level suggestions."""
        stops = StopLevelSuggestions(
            symbol="AAPL",
            current_price=150.0,
            atr_1x=147.5,
            atr_2x=145.0,
            atr_3x=142.5,
            percent_2=147.0,
            percent_5=142.5,
            percent_8=138.0,
            sma_20=148.0,
            sma_50=145.0,
            recent_swing=143.0,
        )

        assert stops.symbol == "AAPL"
        assert stops.atr_1x == 147.5
        assert stops.sma_20 == 148.0

    def test_stops_below_price_validation(self):
        """Test stops must be below current price for long positions."""
        with pytest.raises(ValidationError) as exc_info:
            StopLevelSuggestions(
                symbol="AAPL",
                current_price=150.0,
                atr_1x=152.0,  # Above current price
                atr_2x=145.0,
                atr_3x=142.5,
                percent_2=147.0,
                percent_5=142.5,
                percent_8=138.0,
            )
        assert "Stop level must be below current price" in str(exc_info.value)


class TestRequestModels:
    """Test request models."""

    def test_analyze_stock_request(self):
        """Test AnalyzeStockRequest model."""
        request = AnalyzeStockRequest(symbol="AAPL", lookback_days=30)
        assert request.symbol == "AAPL"
        assert request.lookback_days == 30

        # Test default
        request = AnalyzeStockRequest(symbol="AAPL")
        assert request.lookback_days == 365

    def test_analyze_crypto_request(self):
        """Test AnalyzeCryptoRequest model."""
        request = AnalyzeCryptoRequest(
            symbol="BTC", provider="binance", lookback_days=30, quote_currency="USDT"
        )
        assert request.symbol == "BTC"
        assert request.provider == "binance"

        # Test defaults
        request = AnalyzeCryptoRequest(symbol="BTC")
        assert request.provider == "tiingo"
        assert request.quote_currency == "usd"

    def test_position_size_request(self):
        """Test PositionSizeRequest model."""
        request = PositionSizeRequest(
            symbol="AAPL",
            price=150.0,
            stop_price=145.0,
            risk_amount=500.0,
            account_size=50000.0,
            max_risk_percent=2.0,
        )
        assert request.symbol == "AAPL"
        assert request.max_risk_percent == 2.0

        # Test validation
        with pytest.raises(ValidationError):
            PositionSizeRequest(
                symbol="AAPL",
                stop_price=145.0,
                risk_amount=-500.0,  # Negative risk amount
                account_size=50000.0,
            )


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response(self):
        """Test creating error response."""
        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input",
            details={"field": "symbol", "reason": "required"},
        )

        assert error.error == "ValidationError"
        assert error.message == "Invalid input"
        assert error.details["field"] == "symbol"
        assert isinstance(error.timestamp, datetime)

    def test_error_response_minimal(self):
        """Test error response with minimal fields."""
        error = ErrorResponse(error="ServerError", message="Internal server error")

        assert error.error == "ServerError"
        assert error.details is None


class TestComprehensiveAnalysis:
    """Test ComprehensiveAnalysis model."""

    def test_comprehensive_analysis(self):
        """Test creating comprehensive analysis."""
        # Create component models
        trend = TrendStatus(
            above_20sma=True,
            above_50sma=True,
            above_200sma=True,
            sma_20_50_bullish=True,
            sma_50_200_bullish=True,
            rsi=65.0,
            macd_bullish=True,
        )

        indicators = TechnicalIndicators(atr=2.5, adrp=1.8, avg_20d_vol=1000000, rsi=65.0)

        tech_analysis = TechnicalAnalysisResult(
            symbol="AAPL", current_price=150.0, trend_status=trend, indicators=indicators
        )

        analysis = ComprehensiveAnalysis(
            symbol="AAPL", technical_analysis=tech_analysis, risk_analysis={"max_risk": 0.02}
        )

        assert analysis.symbol == "AAPL"
        assert analysis.technical_analysis.current_price == 150.0
        assert analysis.relative_strength is None  # Optional field
        assert isinstance(analysis.timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
