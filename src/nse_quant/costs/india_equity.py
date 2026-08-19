"""India NSE cash-equity delivery cost model.

COST MODEL: CURRENT 2026 REFERENCE SCHEDULE APPLIED RETROSPECTIVELY
HISTORICAL FEE RECONSTRUCTION: NO
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from typing import Iterable

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
        if profile is DPChargeProfile.FEMALE_PRIMARY:
            return self.dp_female_primary
        raise ValueError(f"Unsupported DP profile: {dp_profile}")


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
class DailyCostBreakdown:
    trade_date: date | None
    buy_turnover: Decimal
    sell_turnover: Decimal
    brokerage: Decimal
    stt_buy: Decimal
    stt_sell: Decimal
    exchange_transaction_charge: Decimal
    sebi_turnover_charge: Decimal
    gst: Decimal
    stamp_duty: Decimal
    dp_charges: Decimal

    @property
    def total_turnover(self) -> Decimal:
        return money(self.buy_turnover + self.sell_turnover)

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

    return DailyCostBreakdown(
        trade_date=next(iter(trade_dates)),
        buy_turnover=buy_turnover,
        sell_turnover=sell_turnover,
        brokerage=brokerage,
        stt_buy=stt_buy,
        stt_sell=stt_sell,
        exchange_transaction_charge=exchange_transaction_charge,
        sebi_turnover_charge=sebi_turnover_charge,
        gst=gst,
        stamp_duty=stamp_duty,
        dp_charges=dp_charges,
    )


def money(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY, rounding=ROUND_HALF_UP)


def nearest_rupee(amount: Decimal) -> Decimal:
    return amount.quantize(RUPEE, rounding=ROUND_HALF_UP)


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
