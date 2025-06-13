#!/usr/bin/env python
# SPY REV CHAD: SPY Reversal Highly Automated Dealer
# An automated trading system for RSI reversal trading with 9 EMA confirmation

import pandas as pd
import numpy as np
import datetime
import time
import pytz
from ib_insync import *


class SPYREVStrategy:
    """RSI Reversal strategy for SPY 0-DTE options.

    The strategy looks for RSI extremes (below 30 for longs, above 70 for shorts)
    followed by price confirmation relative to 9 EMA for entry signals.
    """

    def __init__(
        self,
        ticker: str = "SPY",
        contracts: int = 2,
        underlying_move_target: float = 1.0,
        itm_offset: float = 1.05,
        market_open: str = "08:30:00",
        market_close: str = "15:00:00",
        monitor_start: str = "08:25:00",
        no_new_trades_time: str = "15:30:00",
        force_close_time: str = "14:55:00",
        bar_size: str = "5 mins",
        rsi_period: int = 14,
        ema_period: int = 9,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        paper_trading: bool = True,
        port: int = 7497,
    ):
        self.ticker = ticker
        self.contracts = contracts
        self.underlying_move_target = underlying_move_target
        self.itm_offset = itm_offset
        self.market_open = market_open
        self.market_close = market_close
        self.monitor_start = monitor_start
        self.no_new_trades_time = no_new_trades_time
        self.force_close_time = force_close_time
        self.bar_size = bar_size
        self.rsi_period = rsi_period
        self.ema_period = ema_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.paper_trading = paper_trading
        self.port = port
        # Trading state - can have multiple positions
        self.positions = []  # List of active positions
        self.rsi_signal = None  # "LONG_SETUP" or "SHORT_SETUP" or None
        self.rsi_signal_price = None  # Price when RSI signal occurred
        self.monitoring_started = False

        # IB & timezone
        self.tz = pytz.timezone("US/Central")
        self.ib = IB()

    # ---------------------------------------------------------------------
    # Interactive Brokers helpers
    # ---------------------------------------------------------------------
    def connect_to_ib(self, host: str = "127.0.0.1", client_id: int = 10, max_retries: int = 3) -> bool:
        """Connect to TWS / IB Gateway."""
        port = self.port
        for attempt in range(1, max_retries + 1):
            try:
                if self.ib.isConnected():
                    self.ib.disconnect()
                    time.sleep(1)
                self.ib.connect(host, port, clientId=client_id)
                print(
                    f"Connected to Interactive Brokers {'Paper' if self.paper_trading else 'Live'} trading"
                )
                return True
            except Exception as exc:
                print(f"Connection attempt {attempt}/{max_retries} failed: {exc}")
                time.sleep(2)
        print("Unable to connect after maximum retries – exiting.")
        return False

    def get_stock_contract(self):
        return Stock(self.ticker, "SMART", "USD")

    def get_underlying_price(self) -> float:
        ticker = self.ib.reqTickers(self.get_stock_contract())[0]
        return ticker.marketPrice()

    def get_option_contract(self, right: str) -> Option:
        """Return the ATM 0-DTE option contract for SPY (right="C" or "P")."""
        today = datetime.datetime.now(self.tz).date()
        expiry_str = today.strftime("%Y%m%d")  # 0-DTE (same-day) expiry for SPY

        spot = self.get_underlying_price()
        strike = round(spot)

        contract = Option(
            symbol=self.ticker,
            lastTradeDateOrContractMonth=expiry_str,
            strike=strike,
            right=right,
            exchange="SMART",
            multiplier="100",
            currency="USD",
        )
        details = self.ib.reqContractDetails(contract)
        if details:
            contract = details[0].contract
            self.ib.qualifyContracts(contract)
        return contract

    # ---------------------------------------------------------------------
    # Market & timing helpers
    # ---------------------------------------------------------------------
    def is_market_open(self) -> bool:
        now = datetime.datetime.now(self.tz)
        today = now.date()
        mo = self.tz.localize(
            datetime.datetime.combine(today, datetime.datetime.strptime(self.market_open, "%H:%M:%S").time())
        )
        mc = self.tz.localize(
            datetime.datetime.combine(today, datetime.datetime.strptime(self.market_close, "%H:%M:%S").time())
        )
        return mo <= now <= mc

    def should_start_monitoring(self) -> bool:
        now = datetime.datetime.now(self.tz)
        today = now.date()
        monitor_time = self.tz.localize(
            datetime.datetime.combine(today, datetime.datetime.strptime(self.monitor_start, "%H:%M:%S").time())
        )
        return now >= monitor_time

    def can_open_new_trades(self) -> bool:
        now = datetime.datetime.now(self.tz)
        today = now.date()
        no_new_trades = self.tz.localize(
            datetime.datetime.combine(today, datetime.datetime.strptime(self.no_new_trades_time, "%H:%M:%S").time())
        )
        return now < no_new_trades

    def is_force_close_time(self) -> bool:
        now = datetime.datetime.now(self.tz)
        today = now.date()
        fct = self.tz.localize(
            datetime.datetime.combine(today, datetime.datetime.strptime(self.force_close_time, "%H:%M:%S").time())
        )
        return now >= fct

    # ---------------------------------------------------------------------
    # Data helpers
    # ---------------------------------------------------------------------
    def get_intraday_5min(self, duration: str = "1 D") -> pd.DataFrame | None:
        """Fetch 5-minute historical data for the underlying."""
        contract = self.get_stock_contract()
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting=self.bar_size,
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )
        if not bars:
            return None
        df = util.df(bars)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and 9 EMA indicators."""
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate 9 EMA
        df['ema_9'] = df['close'].ewm(span=self.ema_period, adjust=False).mean()
        
        return df

    # ---------------------------------------------------------------------
    # Trading logic
    # ---------------------------------------------------------------------
    def check_rsi_signal(self, df: pd.DataFrame) -> str | None:
        """Check for RSI extreme conditions on the last completed candle."""
        if len(df) < 2:
            return None
            
        last_candle = df.iloc[-2]  # Last completed candle
        rsi = last_candle['rsi']

        if pd.isna(rsi):
            return None
            
        if rsi < self.rsi_oversold:
            self.rsi_signal_price = last_candle['close']
            return "LONG_SETUP"
        elif rsi > self.rsi_overbought:
            self.rsi_signal_price = last_candle['close']
            return "SHORT_SETUP"
        
        return None

    def check_entry_conditions(self, df: pd.DataFrame) -> str | None:
        """Check if entry conditions are met based on existing RSI signal."""
        if len(df) < 2 or self.rsi_signal is None:
            return None
            
        last_candle = df.iloc[-2]  # Last completed candle
        close_price = last_candle['close']
        ema_9 = last_candle['ema_9']
        
        if pd.isna(ema_9):
            return None
            
        if self.rsi_signal == "LONG_SETUP" and close_price > ema_9:
            return "ENTER_LONG"
        elif self.rsi_signal == "SHORT_SETUP" and close_price < ema_9:
            return "ENTER_SHORT"
            
        return None

    # ---------------------------------------------------------------------
    # Position management
    # ---------------------------------------------------------------------
    def has_position_type(self, position_type: str) -> bool:
        """Check if there's already a position of the specified type (CALL or PUT)."""
        return any(pos['type'] == position_type for pos in self.positions)

    def place_order(self, contract, action: str, quantity: int):
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)
        print(f"{datetime.datetime.now(self.tz)} — {action} {quantity} {contract.localSymbol}")
        return trade

    def enter_position(self, position_type: str):
        """Enter CALL or PUT position."""
        # Check if we already have a position of this type
        if self.has_position_type(position_type):
            print(f"Already have a {position_type} position - skipping entry")
            return

        right = "C" if position_type == "CALL" else "P"
        option_contract = self.get_option_contract(right)
        self.place_order(option_contract, "BUY", self.contracts)

        # Record position details
        position = {
            'type': position_type,
            'contract': option_contract,
            'entry_underlying_price': self.get_underlying_price(),
            'entry_option_price': self.ib.reqTickers(option_contract)[0].marketPrice(),
            'entry_strike': option_contract.strike,
            'stop_loss_price': self.rsi_signal_price,
            'contracts_remaining': self.contracts,
            'half_sold': False,
            'entry_time': datetime.datetime.now(self.tz)
        }
        
        self.positions.append(position)
        
        print(f"Entered {position_type} — Underlying: {position['entry_underlying_price']:.2f}, "
              f"Option: {position['entry_option_price']:.2f}, Strike: {position['entry_strike']}, "
              f"Stop: {position['stop_loss_price']:.2f}")
        
        # Reset signal after entry
        self.rsi_signal = None
        self.rsi_signal_price = None

    def check_stop_loss(self, position: dict, last_candle: pd.Series) -> bool:
        """Check if stop loss should be triggered."""
        close_price = last_candle['close']
        
        if position['type'] == "CALL":
            return close_price < position['stop_loss_price']
        else:  # PUT
            return close_price > position['stop_loss_price']

    def check_profit_targets(self, position: dict) -> str | None:
        """Check profit targets for a position."""
        current_price = self.get_underlying_price()
        option_price = self.ib.reqTickers(position['contract'])[0].marketPrice()
        
        # First profit target: $1.00 move in underlying
        if not position['half_sold']:
            if position['type'] == "CALL":
                if current_price >= position['entry_underlying_price'] + self.underlying_move_target:
                    return "FIRST_TARGET"
            else:  # PUT
                if current_price <= position['entry_underlying_price'] - self.underlying_move_target:
                    return "FIRST_TARGET"
        
        # After first target hit, check breakeven on remaining half
        if position['half_sold']:
            if option_price <= position['entry_option_price']:
                return "BREAKEVEN_STOP"
        
        # Second profit target: $1.05 ITM
        if position['type'] == "CALL":
            if current_price >= position['entry_strike'] + self.itm_offset:
                return "SECOND_TARGET"
        else:  # PUT
            if current_price <= position['entry_strike'] - self.itm_offset:
                return "SECOND_TARGET"
        
        return None

    def exit_position(self, position: dict, reason: str, partial: bool = False):
        """Exit position (full or partial)."""
        if partial and not position['half_sold']:
            # Sell half
            quantity = self.contracts // 2
            position['contracts_remaining'] = self.contracts - quantity
            position['half_sold'] = True
        else:
            # Sell remaining
            quantity = position['contracts_remaining']
            
        self.place_order(position['contract'], "SELL", quantity)
        
        # Calculate P/L
        option_price = self.ib.reqTickers(position['contract'])[0].marketPrice()
        pnl_per_contract = (option_price - position['entry_option_price']) * 100
        
        print(f"Closed {quantity} {position['type']} contracts | Reason: {reason} | "
              f"P/L: ${pnl_per_contract:.2f}/contract")
        
        if not partial or position['contracts_remaining'] == 0:
            # Remove position from list
            self.positions.remove(position)

    def close_all_positions(self, reason: str):
        """Close all open positions."""
        for position in self.positions[:]:  # Copy list to avoid modification during iteration
            self.exit_position(position, reason)

    # ---------------------------------------------------------------------
    # Main loop
    # ---------------------------------------------------------------------
    def reset_daily_state(self):
        """Reset daily trading state."""
        self.positions = []
        self.rsi_signal = None
        self.rsi_signal_price = None
        self.monitoring_started = False

    def run(self):
        if not self.connect_to_ib():
            return

        try:
            print("Starting SPY REV strategy …")
            while True:
                now = datetime.datetime.now(self.tz)

                # Handle market hours
                if not self.is_market_open():
                    if self.positions:
                        print("Market closed — force exiting open positions.")
                        self.close_all_positions("Market closed")
                    self.reset_daily_state()
                    print("Market closed. Waiting for next market open.")
                    time.sleep(60)
                    continue

                # Force-close time
                if self.is_force_close_time() and self.positions:
                    print("Force-close time reached — closing all positions.")
                    self.close_all_positions("2:55 PM force close")

                # Check if we should start monitoring
                if not self.monitoring_started and self.should_start_monitoring():
                    self.monitoring_started = True
                    print("Started monitoring RSI signals at 8:25 AM.")

                if not self.monitoring_started:
                    time.sleep(30)
                    continue

                # Get historical data and calculate indicators
                df = self.get_intraday_5min()
                if df is None or len(df) < self.rsi_period + 5:
                    print("Insufficient historical data — waiting…")
                    time.sleep(30)
                    continue

                df = self.calculate_indicators(df)
                last_candle = df.iloc[-2]  # Last completed candle

                # Check for new RSI signals (only if we can open new trades)
                if self.can_open_new_trades() and self.rsi_signal is None:
                    new_signal = self.check_rsi_signal(df)
                    if new_signal:
                        self.rsi_signal = new_signal
                        print(f"RSI signal detected: {new_signal} at price {self.rsi_signal_price:.2f}")

                # Check for entry conditions
                if self.rsi_signal and self.can_open_new_trades():
                    entry_signal = self.check_entry_conditions(df)
                    if entry_signal == "ENTER_LONG":
                        self.enter_position("CALL")
                    elif entry_signal == "ENTER_SHORT":
                        self.enter_position("PUT")

                # Manage existing positions
                for position in self.positions[:]:  # Copy to avoid modification during iteration
                    # Check stop loss
                    if self.check_stop_loss(position, last_candle):
                        self.exit_position(position, "Stop loss")
                        continue

                    # Check profit targets
                    target_result = self.check_profit_targets(position)
                    if target_result == "FIRST_TARGET":
                        self.exit_position(position, "First profit target", partial=True)
                    elif target_result == "BREAKEVEN_STOP":
                        self.exit_position(position, "Breakeven stop")
                    elif target_result == "SECOND_TARGET":
                        self.exit_position(position, "Second profit target")

                # Sleep before next iteration
                time.sleep(5)

        except KeyboardInterrupt:
            print("User interrupted — shutting down.")
        except Exception as exc:
            print(f"Unhandled error: {exc}")
        finally:
            if self.positions:
                self.close_all_positions("Shutdown")
            self.ib.disconnect()
            print("Disconnected from Interactive Brokers.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SPY REV (Reversal) trading strategy")
    parser.add_argument("--ticker", type=str, default="SPY", help="Underlying ticker symbol")
    parser.add_argument("--contracts", type=int, default=2, help="Number of option contracts to trade")
    parser.add_argument("--underlying_move_target", type=float, default=1.0, help="First profit target (underlying $ move)")
    parser.add_argument("--itm_offset", type=float, default=1.05, help="Underlying distance beyond strike for second target")
    parser.add_argument("--rsi_period", type=int, default=14, help="RSI calculation period")
    parser.add_argument("--ema_period", type=int, default=9, help="EMA calculation period")
    parser.add_argument("--rsi_oversold", type=float, default=30.0, help="RSI oversold level")
    parser.add_argument("--rsi_overbought", type=float, default=70.0, help="RSI overbought level")
    parser.add_argument("--paper_trading", action="store_true", help="Use paper trading account")
    parser.add_argument("--port", type=int, default=7497, help="Port number")
    args = parser.parse_args()

    strategy = SPYREVStrategy(
        ticker=args.ticker,
        contracts=args.contracts,
        underlying_move_target=args.underlying_move_target,
        itm_offset=args.itm_offset,
        rsi_period=args.rsi_period,
        ema_period=args.ema_period,
        rsi_oversold=args.rsi_oversold,
        rsi_overbought=args.rsi_overbought,
        paper_trading=args.paper_trading,
        port=args.port,
    )
    strategy.run() 
