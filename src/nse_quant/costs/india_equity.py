"""India NSE cash-equity delivery cost model.

COST MODEL: CURRENT 2026 REFERENCE SCHEDULE APPLIED RETROSPECTIVELY
HISTORICAL FEE RECONSTRUCTION: NO

Daily cost totals are the authoritative accounting values. Per-fill costs are
reporting allocations: DP is assigned to sold symbols, then to same-symbol sell
fills pro-rata by turnover; all other components are allocated pro-rata by
turnover within the applicable side. Allocated rows must sum back to daily
totals.

GST is calculated from paise-rounded brokerage, exchange transaction charges,
and SEBI charges pending real contract-note validation. This may differ from a
broker that computes GST from unrounded intermediates, and is covered by the
daily real-record tolerance rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from typing import Iterable, Sequence

MONEY = Decimal("0.01")
RUPEE = Decimal("1")
ZERO = Decimal("0")


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class DPChargeProfile(StrEnum):
    MALE_PRIMARY = "male_primary"
    FEMALE_PRIMARY = "female_primary"


@dataclass(frozen=True)
class CostProfile:
    name: str
    brokerage_rate: Decimal
    stt_buy_rate: Decimal
    stt_sell_rate: Decimal
    exchange_transaction_rate: Decimal
    sebi_turnover_rate: Decimal
    gst_rate: Decimal
    stamp_duty_buy_rate: Decimal
    dp_male_primary: Decimal
    dp_female_primary: Decimal
    checked_on: date

    def dp_charge_for(self, dp_profile: DPChargeProfile | str) -> Decimal:
        profile = DPChargeProfile(dp_profile)
        if profile is DPChargeProfile.MALE_PRIMARY:
            return self.dp_male_primary
        return self.dp_female_primary


ZERODHA_NSE_DELIVERY_2026_08 = CostProfile(
    name="ZERODHA_NSE_DELIVERY_2026_08",
    brokerage_rate=Decimal("0"),
    stt_buy_rate=Decimal("0.001"),
    stt_sell_rate=Decimal("0.001"),
    exchange_transaction_rate=Decimal("0.0000307"),
    sebi_turnover_rate=Decimal("0.000001"),
    gst_rate=Decimal("0.18"),
    stamp_duty_buy_rate=Decimal("0.00015"),
    dp_male_primary=Decimal("15.34"),
    dp_female_primary=Decimal("15.05"),
    checked_on=date(2026, 8, 19),
)


@dataclass(frozen=True)
class Fill:
    trade_date: date
    symbol: str
    side: TradeSide | str
    quantity: int
    price: Decimal | str | int

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, date):
            raise TypeError("trade_date must be a date")
        symbol = self.symbol.strip().upper() if isinstance(self.symbol, str) else ""
        if not symbol:
            raise ValueError("symbol must be non-blank")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an integer")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

        side = TradeSide(self.side)
        price = _to_decimal(self.price, field_name="price")
        if price <= ZERO:
            raise ValueError("price must be positive")

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "price", price)

    @property
    def turnover(self) -> Decimal:
        return money(self.price * Decimal(self.quantity))


@dataclass(frozen=True)
class CostComponents:
    brokerage: Decimal
    stt_buy: Decimal
    stt_sell: Decimal
    exchange_transaction_charge: Decimal
    sebi_turnover_charge: Decimal
    gst: Decimal
    stamp_duty: Decimal
    dp_charges: Decimal

    @property
    def stt(self) -> Decimal:
        return money(self.stt_buy + self.stt_sell)

    @property
    def total_cost(self) -> Decimal:
        return money(
            self.brokerage
            + self.stt
            + self.exchange_transaction_charge
            + self.sebi_turnover_charge
            + self.gst
            + self.stamp_duty
            + self.dp_charges
        )


@dataclass(frozen=True)
class AllocatedFillCost(CostComponents):
    fill: Fill
    allocation_note: str = "REPORTING ALLOCATION; DAILY TOTAL IS AUTHORITATIVE"


@dataclass(frozen=True)
class DailyCostBreakdown(CostComponents):
    trade_date: date | None
    buy_turnover: Decimal
    sell_turnover: Decimal
    allocations: tuple[AllocatedFillCost, ...] = ()

    @property
    def total_turnover(self) -> Decimal:
        return money(self.buy_turnover + self.sell_turnover)


def calculate_daily_costs(
    fills: Iterable[Fill],
    *,
    profile: CostProfile = ZERODHA_NSE_DELIVERY_2026_08,
    dp_profile: DPChargeProfile | str = DPChargeProfile.MALE_PRIMARY,
) -> DailyCostBreakdown:
    """Calculate one trading day's delivery charges from validated fills."""

    daily_fills = list(fills)
    if not daily_fills:
        return DailyCostBreakdown(
            trade_date=None,
            buy_turnover=ZERO,
            sell_turnover=ZERO,
            brokerage=ZERO,
            stt_buy=ZERO,
            stt_sell=ZERO,
            exchange_transaction_charge=ZERO,
            sebi_turnover_charge=ZERO,
            gst=ZERO,
            stamp_duty=ZERO,
            dp_charges=ZERO,
            allocations=(),
        )

    trade_dates = {fill.trade_date for fill in daily_fills}
    if len(trade_dates) != 1:
        raise ValueError("calculate_daily_costs only supports one trade_date")

    buy_turnover = money(
        sum((fill.turnover for fill in daily_fills if fill.side is TradeSide.BUY), ZERO)
    )
    sell_turnover = money(
        sum((fill.turnover for fill in daily_fills if fill.side is TradeSide.SELL), ZERO)
    )
    total_turnover = money(buy_turnover + sell_turnover)

    brokerage = money(total_turnover * profile.brokerage_rate)
    stt_buy = nearest_rupee(buy_turnover * profile.stt_buy_rate)
    stt_sell = nearest_rupee(sell_turnover * profile.stt_sell_rate)
    exchange_transaction_charge = money(
        total_turnover * profile.exchange_transaction_rate
    )
    sebi_turnover_charge = money(total_turnover * profile.sebi_turnover_rate)
    gst = money(
        (brokerage + exchange_transaction_charge + sebi_turnover_charge)
        * profile.gst_rate
    )
    stamp_duty = money(buy_turnover * profile.stamp_duty_buy_rate)

    sold_symbols = {
        fill.symbol for fill in daily_fills if fill.side is TradeSide.SELL
    }
    dp_charges = money(
        Decimal(len(sold_symbols)) * profile.dp_charge_for(dp_profile)
    )

    components = CostComponents(
        brokerage=brokerage,
        stt_buy=stt_buy,
        stt_sell=stt_sell,
        exchange_transaction_charge=exchange_transaction_charge,
        sebi_turnover_charge=sebi_turnover_charge,
        gst=gst,
        stamp_duty=stamp_duty,
        dp_charges=dp_charges,
    )

    return DailyCostBreakdown(
        trade_date=next(iter(trade_dates)),
        buy_turnover=buy_turnover,
        sell_turnover=sell_turnover,
        allocations=allocate_daily_costs(daily_fills, components),
        **components.__dict__,
    )


def money(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY, rounding=ROUND_HALF_UP)


def nearest_rupee(amount: Decimal) -> Decimal:
    return amount.quantize(RUPEE, rounding=ROUND_HALF_UP)


def allocate_daily_costs(
    fills: Sequence[Fill],
    daily: CostComponents,
) -> tuple[AllocatedFillCost, ...]:
    """Allocate authoritative daily costs to fills for reporting/reconciliation."""

    total_turnovers = [fill.turnover for fill in fills]
    buy_turnovers = [
        fill.turnover if fill.side is TradeSide.BUY else ZERO for fill in fills
    ]
    sell_turnovers = [
        fill.turnover if fill.side is TradeSide.SELL else ZERO for fill in fills
    ]

    brokerage = _allocate_by_weight(daily.brokerage, total_turnovers)
    stt_buy = _allocate_by_weight(daily.stt_buy, buy_turnovers)
    stt_sell = _allocate_by_weight(daily.stt_sell, sell_turnovers)
    exchange = _allocate_by_weight(
        daily.exchange_transaction_charge, total_turnovers
    )
    sebi = _allocate_by_weight(daily.sebi_turnover_charge, total_turnovers)
    gst = _allocate_by_weight(daily.gst, total_turnovers)
    stamp = _allocate_by_weight(daily.stamp_duty, buy_turnovers)
    dp = _allocate_dp_by_sold_symbol(fills, daily.dp_charges)

    return tuple(
        AllocatedFillCost(
            fill=fill,
            brokerage=brokerage[index],
            stt_buy=stt_buy[index],
            stt_sell=stt_sell[index],
            exchange_transaction_charge=exchange[index],
            sebi_turnover_charge=sebi[index],
            gst=gst[index],
            stamp_duty=stamp[index],
            dp_charges=dp[index],
        )
        for index, fill in enumerate(fills)
    )


def _allocate_by_weight(amount: Decimal, weights: Sequence[Decimal]) -> list[Decimal]:
    if amount == ZERO or not weights:
        return [ZERO for _ in weights]

    total_weight = sum(weights, ZERO)
    if total_weight == ZERO:
        return [ZERO for _ in weights]

    allocations = [money(amount * weight / total_weight) for weight in weights]
    return _add_rounding_remainder(allocations, amount, weights)


def _allocate_dp_by_sold_symbol(
    fills: Sequence[Fill], daily_dp_charges: Decimal
) -> list[Decimal]:
    sell_symbols = sorted({fill.symbol for fill in fills if fill.side is TradeSide.SELL})
    if not sell_symbols:
        return [ZERO for _ in fills]

    per_symbol_charges = _allocate_by_weight(
        daily_dp_charges, [Decimal(1) for _ in sell_symbols]
    )
    charges_by_symbol = dict(zip(sell_symbols, per_symbol_charges, strict=True))
    allocations = [ZERO for _ in fills]

    for symbol in sell_symbols:
        symbol_weights = [
            fill.turnover
            if fill.side is TradeSide.SELL and fill.symbol == symbol
            else ZERO
            for fill in fills
        ]
        symbol_allocations = _allocate_by_weight(
            charges_by_symbol[symbol], symbol_weights
        )
        allocations = [
            money(current + allocated)
            for current, allocated in zip(allocations, symbol_allocations, strict=True)
        ]

    return allocations


def _add_rounding_remainder(
    allocations: list[Decimal], amount: Decimal, weights: Sequence[Decimal]
) -> list[Decimal]:
    remainder = money(amount - sum(allocations, ZERO))
    if remainder == ZERO:
        return allocations

    eligible = [index for index, weight in enumerate(weights) if weight > ZERO]
    if not eligible:
        return allocations

    penny = MONEY if remainder > ZERO else -MONEY
    for offset in range(int(abs(remainder / MONEY))):
        index = eligible[offset % len(eligible)]
        allocations[index] = money(allocations[index] + penny)

    return allocations


def _to_decimal(value: Decimal | str | int, *, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise TypeError(f"{field_name} must not be a binary float")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    raise TypeError(f"{field_name} must be Decimal, str, or int")
