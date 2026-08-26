"""Decimal portfolio accounting primitives for Phase 1 backtests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum
from typing import Iterable, Mapping

from nse_quant.backtest.data import BacktestBar, DailyBars


MONEY = Decimal("0.01")
ZERO = Decimal("0")


class BacktestAccountingError(RuntimeError):
    """Raised when a portfolio operation would break accounting rules."""


class FillSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: int

    def __post_init__(self) -> None:
        clean_symbol = _symbol(self.symbol)
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an integer")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        object.__setattr__(self, "symbol", clean_symbol)


@dataclass(frozen=True)
class PortfolioFill:
    trade_date: date
    sequence: int
    symbol: str
    side: FillSide | str
    quantity: int
    price: Decimal | str | int
    fees: Decimal | str | int = ZERO

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, date):
            raise TypeError("trade_date must be a date")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise TypeError("sequence must be an integer")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an integer")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        price = _decimal(self.price, "price")
        fees = _decimal(self.fees, "fees")
        if price <= ZERO:
            raise ValueError("price must be positive")
        if fees < ZERO:
            raise ValueError("fees must be non-negative")

        object.__setattr__(self, "symbol", _symbol(self.symbol))
        object.__setattr__(self, "side", FillSide(self.side))
        object.__setattr__(self, "price", price)
        object.__setattr__(self, "fees", money(fees))

    @property
    def turnover(self) -> Decimal:
        return money(self.price * Decimal(self.quantity))


@dataclass(frozen=True)
class PortfolioSnapshot:
    trade_date: date
    cash: Decimal
    positions: tuple[Position, ...]
    holdings_value: Decimal
    nav: Decimal

    def __post_init__(self) -> None:
        if self.nav != money(self.cash + self.holdings_value):
            raise BacktestAccountingError("NAV invariant failed")


@dataclass(frozen=True)
class PortfolioState:
    cash: Decimal
    positions: tuple[Position, ...] = ()

    def __post_init__(self) -> None:
        cash = money(_decimal(self.cash, "cash"))
        if cash < ZERO:
            raise BacktestAccountingError("cash must be non-negative")
        symbols = [position.symbol for position in self.positions]
        duplicates = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
        if duplicates:
            raise BacktestAccountingError(f"duplicate positions: {duplicates}")
        object.__setattr__(self, "cash", cash)
        object.__setattr__(
            self,
            "positions",
            tuple(sorted(self.positions, key=lambda position: position.symbol)),
        )

    @classmethod
    def starting_cash(cls, amount: Decimal | str | int) -> PortfolioState:
        return cls(cash=_decimal(amount, "amount"))

    @property
    def positions_by_symbol(self) -> dict[str, Position]:
        return {position.symbol: position for position in self.positions}

    def apply_fills(self, fills: Iterable[PortfolioFill]) -> PortfolioState:
        """Apply explicit fills in deterministic fill order."""

        state = self
        for fill in sorted(
            fills,
            key=lambda item: (item.trade_date, item.sequence, item.symbol, item.side.value),
        ):
            state = state._apply_fill(fill)
        return state

    def mark_to_market(
        self,
        trade_date: date,
        bars: DailyBars | Mapping[str, BacktestBar],
    ) -> PortfolioSnapshot:
        """Value all holdings at adjusted close and assert the NAV invariant."""

        if isinstance(bars, DailyBars):
            if bars.trade_date != trade_date:
                raise BacktestAccountingError(
                    f"valuation date mismatch: {trade_date} vs {bars.trade_date}"
                )
            bars_by_symbol = bars.by_symbol
        else:
            bars_by_symbol = {_symbol(symbol): bar for symbol, bar in bars.items()}

        holdings_value = ZERO
        for position in self.positions:
            try:
                bar = bars_by_symbol[position.symbol]
            except KeyError:
                raise BacktestAccountingError(
                    f"missing close for held symbol {position.symbol} on {trade_date}"
                ) from None
            holdings_value = money(
                holdings_value
                + money(bar.adjusted_close * Decimal(position.quantity))
            )

        return PortfolioSnapshot(
            trade_date=trade_date,
            cash=self.cash,
            positions=self.positions,
            holdings_value=holdings_value,
            nav=money(self.cash + holdings_value),
        )

    def _apply_fill(self, fill: PortfolioFill) -> PortfolioState:
        positions = self.positions_by_symbol
        if fill.side is FillSide.BUY:
            next_cash = money(self.cash - fill.turnover - fill.fees)
            if next_cash < ZERO:
                raise BacktestAccountingError(
                    f"BUY {fill.symbol} would make cash negative"
                )
            current = positions.get(fill.symbol)
            next_quantity = fill.quantity if current is None else current.quantity + fill.quantity
            positions[fill.symbol] = Position(fill.symbol, next_quantity)
            return PortfolioState(cash=next_cash, positions=tuple(positions.values()))

        current = positions.get(fill.symbol)
        if current is None or current.quantity < fill.quantity:
            raise BacktestAccountingError(
                f"SELL {fill.symbol} exceeds held quantity"
            )
        next_cash = money(self.cash + fill.turnover - fill.fees)
        if next_cash < ZERO:
            raise BacktestAccountingError(
                f"SELL {fill.symbol} would make cash negative after fees"
            )
        next_quantity = current.quantity - fill.quantity
        if next_quantity == 0:
            del positions[fill.symbol]
        else:
            positions[fill.symbol] = Position(fill.symbol, next_quantity)
        return PortfolioState(cash=next_cash, positions=tuple(positions.values()))


def money(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY, rounding=ROUND_HALF_UP)


def _decimal(value: Decimal | str | int, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise TypeError(f"{field_name} must not be a binary float")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    raise TypeError(f"{field_name} must be Decimal, str, or int")


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise ValueError("symbol must be non-blank")
    return symbol
