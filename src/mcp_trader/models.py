"""
Pydantic models for MCP Trader data structures.

This module provides type-safe data models for all data structures used
throughout the MCP trader application, including market data responses,
technical analysis results, and risk calculations.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Market Data Models


class CandleData(BaseModel):
    """Represents a single candlestick in market data."""

    date: datetime = Field(..., description="Timestamp of the candle")
    open: float = Field(..., ge=0, description="Opening price")
    high: float = Field(..., ge=0, description="High price")
    low: float = Field(..., ge=0, description="Low price")
    close: float = Field(..., ge=0, description="Closing price")
    volume: float = Field(..., ge=0, description="Trading volume")
    symbol: str = Field(..., description="Trading symbol")

    @field_validator("high")
    def high_gte_low(cls, v, info):
        """Ensure high price is greater than or equal to low price."""
        if "low" in info.data and v < info.data["low"]:
            raise ValueError("High price must be >= low price")
        return v

    @field_validator("high")
    def high_gte_open_close(cls, v, info):
        """Ensure high price is greater than or equal to open and close."""
        if "open" in info.data and v < info.data["open"]:
            raise ValueError("High price must be >= open price")
        if "close" in info.data and v < info.data["close"]:
            raise ValueError("High price must be >= close price")
        return v

    @field_validator("low")
    def low_lte_open_close(cls, v, info):
        """Ensure low price is less than or equal to open and close."""
        if "open" in info.data and v > info.data["open"]:
            raise ValueError("Low price must be <= open price")
        if "close" in info.data and v > info.data["close"]:
            raise ValueError("Low price must be <= close price")
        return v


class MarketDataResponse(BaseModel):
    """Response from market data fetch operations."""

    symbol: str = Field(..., description="Trading symbol")
    data: list[CandleData] = Field(..., description="Historical candle data")
    provider: Literal["tiingo", "binance"] = Field(..., description="Data provider")
    lookback_days: int = Field(..., gt=0, description="Number of days of data")
    quote_currency: str | None = Field(None, description="Quote currency for crypto pairs")


# Technical Analysis Models


class TrendStatus(BaseModel):
    """Current trend status based on moving averages and indicators."""

    above_20sma: bool = Field(..., description="Price above 20-day SMA")
    above_50sma: bool = Field(..., description="Price above 50-day SMA")
    above_200sma: bool = Field(..., description="Price above 200-day SMA")
    sma_20_50_bullish: bool = Field(..., alias="20_50_bullish", description="20 SMA above 50 SMA")
    sma_50_200_bullish: bool = Field(
        ..., alias="50_200_bullish", description="50 SMA above 200 SMA"
    )
    rsi: float = Field(..., ge=0, le=100, description="Relative Strength Index")
    macd_bullish: bool = Field(..., description="MACD line above signal line")

    model_config = ConfigDict(populate_by_name=True)


class TechnicalIndicators(BaseModel):
    """Collection of technical indicators for a given symbol."""

    sma_20: float | None = Field(None, description="20-day Simple Moving Average")
    sma_50: float | None = Field(None, description="50-day Simple Moving Average")
    sma_200: float | None = Field(None, description="200-day Simple Moving Average")
    atr: float = Field(..., ge=0, description="Average True Range (14)")
    adrp: float = Field(..., ge=0, description="Average Daily Range Percentage")
    avg_20d_vol: float = Field(..., ge=0, description="20-day Average Volume")
    rsi: float = Field(..., ge=0, le=100, description="Relative Strength Index (14)")
    macd: float | None = Field(None, description="MACD line value")
    macd_signal: float | None = Field(None, description="MACD signal line value")
    macd_histogram: float | None = Field(None, description="MACD histogram value")


class TechnicalAnalysisResult(BaseModel):
    """Complete technical analysis result for a symbol."""

    symbol: str = Field(..., description="Trading symbol")
    current_price: float = Field(..., ge=0, description="Latest closing price")
    trend_status: TrendStatus = Field(..., description="Current trend analysis")
    indicators: TechnicalIndicators = Field(..., description="Technical indicators")
    analysis_date: datetime = Field(
        default_factory=datetime.utcnow, description="Analysis timestamp"
    )


# Relative Strength Models


class RelativeStrengthPeriod(BaseModel):
    """Relative strength metrics for a single time period."""

    period_days: int = Field(..., gt=0, description="Period length in days")
    rs_score: float = Field(..., ge=1, le=99, description="Relative strength score (1-99)")
    stock_return: float = Field(..., description="Stock return percentage")
    benchmark_return: float = Field(..., description="Benchmark return percentage")
    excess_return: float = Field(..., description="Excess return over benchmark")

    @field_validator("excess_return")
    def validate_excess_return(cls, v, info):
        """Ensure excess return equals stock return minus benchmark return."""
        if "stock_return" in info.data and "benchmark_return" in info.data:
            expected = info.data["stock_return"] - info.data["benchmark_return"]
            if abs(v - expected) > 0.01:  # Allow small floating point differences
                raise ValueError("Excess return must equal stock return minus benchmark return")
        return v


class RelativeStrengthResult(BaseModel):
    """Complete relative strength analysis result."""

    symbol: str = Field(..., description="Stock symbol")
    benchmark: str = Field(..., description="Benchmark symbol")
    periods: list[RelativeStrengthPeriod] = Field(..., description="RS metrics by period")
    analysis_date: datetime = Field(
        default_factory=datetime.utcnow, description="Analysis timestamp"
    )


# Volume Profile Models


class VolumeBin(BaseModel):
    """Single price bin in volume profile."""

    price_low: float = Field(..., ge=0, description="Lower bound of price bin")
    price_high: float = Field(..., ge=0, description="Upper bound of price bin")
    price_mid: float = Field(..., ge=0, description="Midpoint of price bin")
    volume: int = Field(..., ge=0, description="Total volume in bin")
    volume_percent: float = Field(..., ge=0, le=100, description="Percentage of total volume")

    @field_validator("price_high")
    def validate_price_range(cls, v, info):
        """Ensure price_high > price_low."""
        if "price_low" in info.data and v <= info.data["price_low"]:
            raise ValueError("price_high must be greater than price_low")
        return v

    @field_validator("price_mid")
    def validate_price_mid(cls, v, info):
        """Ensure price_mid is between price_low and price_high."""
        if "price_low" in info.data and "price_high" in info.data:
            expected = (info.data["price_low"] + info.data["price_high"]) / 2
            if abs(v - expected) > 0.01:
                raise ValueError("price_mid must be the average of price_low and price_high")
        return v


class VolumeProfileResult(BaseModel):
    """Complete volume profile analysis result."""

    symbol: str = Field(..., description="Trading symbol")
    price_min: float = Field(..., ge=0, description="Minimum price in profile")
    price_max: float = Field(..., ge=0, description="Maximum price in profile")
    bin_width: float = Field(..., gt=0, description="Width of each price bin")
    bins: list[VolumeBin] = Field(..., description="Volume distribution by price")
    point_of_control: float = Field(..., ge=0, description="Price level with highest volume")
    value_area_low: float = Field(..., ge=0, description="Lower bound of value area (70% volume)")
    value_area_high: float = Field(..., ge=0, description="Upper bound of value area (70% volume)")
    lookback_days: int = Field(..., gt=0, description="Days analyzed")

    @field_validator("price_max")
    def validate_price_range(cls, v, info):
        """Ensure price_max > price_min."""
        if "price_min" in info.data and v <= info.data["price_min"]:
            raise ValueError("price_max must be greater than price_min")
        return v

    @field_validator("value_area_high")
    def validate_value_area(cls, v, info):
        """Ensure value area is within price range."""
        if "value_area_low" in info.data and v <= info.data["value_area_low"]:
            raise ValueError("value_area_high must be greater than value_area_low")
        if "price_max" in info.data and v > info.data["price_max"]:
            raise ValueError("value_area_high cannot exceed price_max")
        return v


# Pattern Detection Models


class ChartPattern(BaseModel):
    """Detected chart pattern."""

    type: Literal[
        "Double Bottom",
        "Double Top",
        "Resistance Breakout",
        "Support Breakdown",
        "Head and Shoulders",
        "Inverse Head and Shoulders",
        "Triangle",
        "Flag",
        "Wedge",
    ] = Field(..., description="Pattern type")
    start_date: str | None = Field(None, description="Pattern start date")
    end_date: str | None = Field(None, description="Pattern end date")
    price_level: float = Field(..., ge=0, description="Key price level")
    confidence: Literal["Low", "Medium", "High"] = Field(..., description="Pattern confidence")
    additional_info: dict[str, Any] | None = Field(None, description="Pattern-specific details")


class PatternDetectionResult(BaseModel):
    """Pattern detection analysis result."""

    symbol: str = Field(..., description="Trading symbol")
    patterns: list[ChartPattern] = Field(..., description="Detected patterns")
    message: str | None = Field(None, description="Analysis message or warning")
    analysis_date: datetime = Field(
        default_factory=datetime.utcnow, description="Analysis timestamp"
    )


# Risk Analysis Models


class RMultiples(BaseModel):
    """R-Multiple price targets based on risk."""

    r1: float = Field(..., ge=0, description="1R target (1:1 risk/reward)")
    r2: float = Field(..., ge=0, description="2R target (2:1 risk/reward)")
    r3: float = Field(..., ge=0, description="3R target (3:1 risk/reward)")


class PositionSizeResult(BaseModel):
    """Position sizing calculation result."""

    symbol: str = Field(..., description="Trading symbol")
    entry_price: float = Field(..., ge=0, description="Entry price")
    stop_price: float = Field(..., ge=0, description="Stop loss price")
    recommended_shares: int = Field(..., ge=0, description="Recommended position size")
    dollar_risk: float = Field(..., ge=0, description="Dollar amount at risk")
    risk_per_share: float = Field(..., ge=0, description="Risk per share")
    position_cost: float = Field(..., ge=0, description="Total position cost")
    account_percent_risked: float = Field(
        ..., ge=0, le=100, description="Percentage of account risked"
    )
    r_multiples: RMultiples = Field(..., description="R-multiple targets")

    @field_validator("risk_per_share")
    def validate_risk_per_share(cls, v, info):
        """Ensure risk per share matches entry - stop price."""
        if "entry_price" in info.data and "stop_price" in info.data:
            expected = abs(info.data["entry_price"] - info.data["stop_price"])
            if abs(v - expected) > 0.01:
                raise ValueError("risk_per_share must equal |entry_price - stop_price|")
        return v


class StopLevelSuggestions(BaseModel):
    """Suggested stop loss levels."""

    symbol: str = Field(..., description="Trading symbol")
    current_price: float = Field(..., ge=0, description="Current price")
    atr_1x: float = Field(..., ge=0, description="1x ATR stop")
    atr_2x: float = Field(..., ge=0, description="2x ATR stop")
    atr_3x: float = Field(..., ge=0, description="3x ATR stop")
    percent_2: float = Field(..., ge=0, description="2% stop")
    percent_5: float = Field(..., ge=0, description="5% stop")
    percent_8: float = Field(..., ge=0, description="8% stop")
    sma_20: float | None = Field(None, ge=0, description="20-day SMA stop")
    sma_50: float | None = Field(None, ge=0, description="50-day SMA stop")
    sma_200: float | None = Field(None, ge=0, description="200-day SMA stop")
    recent_swing: float | None = Field(None, ge=0, description="Recent swing low")

    @field_validator("atr_1x", "atr_2x", "atr_3x", "percent_2", "percent_5", "percent_8")
    def validate_stops_below_price(cls, v, info):
        """Ensure stop levels are below current price (for long positions)."""
        if "current_price" in info.data and v >= info.data["current_price"]:
            raise ValueError("Stop level must be below current price for long positions")
        return v


# Analysis Request/Response Models


class AnalyzeStockRequest(BaseModel):
    """Request model for stock analysis."""

    symbol: str = Field(..., description="Stock symbol to analyze")
    lookback_days: int | None = Field(365, gt=0, description="Days of historical data")


class AnalyzeCryptoRequest(BaseModel):
    """Request model for crypto analysis."""

    symbol: str = Field(..., description="Crypto symbol to analyze")
    provider: Literal["tiingo", "binance"] = Field("tiingo", description="Data provider")
    lookback_days: int | None = Field(365, gt=0, description="Days of historical data")
    quote_currency: str | None = Field("usd", description="Quote currency")


class RelativeStrengthRequest(BaseModel):
    """Request model for relative strength analysis."""

    symbol: str = Field(..., description="Stock symbol to analyze")
    benchmark: str = Field("SPY", description="Benchmark symbol")
    lookback_periods: list[int] = Field(
        default=[21, 63, 126, 252], description="Periods in trading days"
    )


class VolumeProfileRequest(BaseModel):
    """Request model for volume profile analysis."""

    symbol: str = Field(..., description="Stock symbol to analyze")
    lookback_days: int = Field(60, gt=0, description="Days to analyze")
    num_bins: int = Field(10, gt=0, le=50, description="Number of price bins")


class PatternDetectionRequest(BaseModel):
    """Request model for pattern detection."""

    symbol: str = Field(..., description="Stock symbol to analyze")
    lookback_days: int = Field(90, gt=0, description="Days to analyze")


class PositionSizeRequest(BaseModel):
    """Request model for position sizing."""

    symbol: str = Field(..., description="Stock symbol")
    price: float | None = Field(0, ge=0, description="Entry price (0 for current)")
    stop_price: float = Field(..., ge=0, description="Stop loss price")
    risk_amount: float = Field(..., gt=0, description="Dollar amount to risk")
    account_size: float = Field(..., gt=0, description="Total account size")
    max_risk_percent: float = Field(2.0, gt=0, le=10, description="Max account percent to risk")


class StopSuggestionRequest(BaseModel):
    """Request model for stop level suggestions."""

    symbol: str = Field(..., description="Stock symbol to analyze")
    lookback_days: int = Field(60, gt=0, description="Days for calculation")


# Error Models


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


# Aggregate Analysis Models


class ComprehensiveAnalysis(BaseModel):
    """Complete analysis combining multiple tools."""

    symbol: str = Field(..., description="Trading symbol")
    technical_analysis: TechnicalAnalysisResult = Field(..., description="Technical indicators")
    relative_strength: RelativeStrengthResult | None = Field(None, description="RS analysis")
    volume_profile: VolumeProfileResult | None = Field(None, description="Volume analysis")
    patterns: PatternDetectionResult | None = Field(None, description="Pattern detection")
    risk_analysis: dict[str, Any] | None = Field(None, description="Risk metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
