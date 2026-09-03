"""Pre-registered strategy specifications."""

from nse_quant.strategies.momentum import (
    MarketRegime,
    MarketRegimeSignal,
    MomentumScore,
    MomentumSignal,
    RegimeExposureSummary,
    RegimeFilteredMomentumSignal,
    generate_weekly_hysteresis_momentum_signals,
    generate_weekly_momentum_signals,
    generate_weekly_regime_filtered_hysteresis_momentum_signals,
    summarize_regime_exposure,
)

__all__ = [
    "MarketRegime",
    "MarketRegimeSignal",
    "MomentumScore",
    "MomentumSignal",
    "RegimeExposureSummary",
    "RegimeFilteredMomentumSignal",
    "generate_weekly_hysteresis_momentum_signals",
    "generate_weekly_momentum_signals",
    "generate_weekly_regime_filtered_hysteresis_momentum_signals",
    "summarize_regime_exposure",
]
