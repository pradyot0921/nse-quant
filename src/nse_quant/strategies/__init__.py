"""Pre-registered strategy specifications."""

from nse_quant.strategies.momentum import (
    MomentumScore,
    MomentumSignal,
    generate_weekly_hysteresis_momentum_signals,
    generate_weekly_momentum_signals,
)

__all__ = [
    "MomentumScore",
    "MomentumSignal",
    "generate_weekly_hysteresis_momentum_signals",
    "generate_weekly_momentum_signals",
]
