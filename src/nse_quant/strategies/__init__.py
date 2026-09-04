"""Pre-registered strategy specifications."""

from nse_quant.strategies.momentum import (
    FiftyTwoWeekHighInputSummary,
    FiftyTwoWeekHighScore,
    FiftyTwoWeekHighSignal,
    MarketRegime,
    MarketRegimeSignal,
    MomentumScore,
    MomentumSignal,
    RegimeExposureSummary,
    RegimeFilteredMomentumSignal,
    generate_weekly_52_week_high_hysteresis_signals,
    generate_weekly_hysteresis_momentum_signals,
    generate_weekly_momentum_signals,
    generate_weekly_regime_filtered_hysteresis_momentum_signals,
    summarize_52_week_high_input,
    summarize_regime_exposure,
)

__all__ = [
    "FiftyTwoWeekHighInputSummary",
    "FiftyTwoWeekHighScore",
    "FiftyTwoWeekHighSignal",
    "MarketRegime",
    "MarketRegimeSignal",
    "MomentumScore",
    "MomentumSignal",
    "RegimeExposureSummary",
    "RegimeFilteredMomentumSignal",
    "generate_weekly_52_week_high_hysteresis_signals",
    "generate_weekly_hysteresis_momentum_signals",
    "generate_weekly_momentum_signals",
    "generate_weekly_regime_filtered_hysteresis_momentum_signals",
    "summarize_52_week_high_input",
    "summarize_regime_exposure",
]
