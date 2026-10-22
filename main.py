# main.py
# -*- coding: utf-8 -*-
"""
Adaptive V5 US-10stocks Trading Bot
Version: v0.3.2-adaptive-V5-US-10stocks
"""

import time
import logging
from datetime import datetime

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("[WARN] MetaTrader5 not installed. Running in SIMULATION mode.")

# ============================================================
# CONFIG
# ============================================================
CONFIG = {
    "version": "v0.3.2-adaptive-V5-US-10stocks",
    "portfolio": 10000,
    "max_pos": 5,
    "max_pct": 0.22,
    "allocation_v5": {
        "NVDA": 0.1, "META": 0.1, "MSFT": 0.1, "AAPL": 0.1, "TSLA": 0.1,
        "GOOGL": 0.1, "AMZN": 0.1, "AMD": 0.1, "NFLX": 0.1, "AVGO": 0.1,
    },
    "initial_prices": {
        "NVDA": 175, "META": 500, "MSFT": 430, "AAPL": 225, "TSLA": 250,
        "GOOGL": 175, "AMZN": 200, "AMD": 160, "NFLX": 700, "AVGO": 210,
    },
    "initial_atr": {
        "NVDA": 5.2, "META": 8.5, "MSFT": 4.8, "AAPL": 2.8, "TSLA": 6.5,
        "GOOGL": 3.2, "AMZN": 3.5, "AMD": 4.1, "NFLX": 12.0, "AVGO": 4.5,
    },
    "mt5_server": "Exness-MT5Trial17",
    "mt5_login": "464110288",
    "symbols": ["NVDA", "META", "MSFT", "AAPL", "TSLA",
                "GOOGL", "AMZN", "AMD", "NFLX", "AVGO"],
}

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ADAPTIVE-V5")


# ============================================================
# MT5 SETUP
# ============================================================
def init_mt5() -> bool:
    if not MT5_AVAILABLE:
        return False
    if not mt5.initialize():
        log.error(f"mt5.initialize() failed: {mt5.last_error()}")
        return False
    acc = mt5.account_info()
    if acc is None:
        log.error("Cannot retrieve account info.")
        mt5.shutdown()
        return False
    log.info(f"Connected: {acc.login} @ {acc.server} | Balance: {acc.balance}")
    return True


# ============================================================
# POSITION SIZING
# ============================================================
def calc_lot_size(symbol: str, price: float, atr: float,
                  equity: float, alloc_pct: float) -> float:
    """Risk-based lot sizing (1R = 1.5 * ATR stop distance)."""
    risk_per_trade = equity * alloc_pct * 0.01  # 1% of allocated capital
    stop_distance = atr * 1.5
    if stop_distance <= 0 or price <= 0:
        return 0.0
    shares = risk_per_trade / stop_distance
    lots = shares / price
    return max(round(lots, 2), 0.01)


# ============================================================
# SIGNAL (placeholder – adapt to your strategy)
# ============================================================
def get_signal(symbol: str) -> str:
    """
    Returns 'BUY', 'SELL', or 'HOLD'.
    TODO: implement real indicator logic (EMA cross, RSI, etc.)
    """
    return "HOLD"


# ============================================================
# TRADE EXECUTION
# ============================================================
def place_order(symbol: str, side: str, lot: float, price: float):
    if not MT5_AVAILABLE:
        log.info(f"[SIM] {side} {lot} {symbol} @ {price}")
        return None

    order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log.warning(f"No tick for {symbol}")
        return None

    price = tick.ask if side == "BUY" else tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 20250302,
        "comment": "adaptive-v5",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        log.error(f"Order failed {symbol}: {result}")
        return None
    log.info(f"Order OK {symbol} {side} {lot} @ {price}")
    return result


# ============================================================
# MAIN LOOP
# ============================================================
def main():
    log.info(f"=== Starting {CONFIG['version']} ===")

    live = init_mt5()
    if not live:
        log.warning("Running in SIMULATION mode.")

    # Portfolio state
    equity = CONFIG["portfolio"]
    open_positions = {}  # symbol -> {side, lot, entry}
    max_pos = CONFIG["max_pos"]
    max_pct = CONFIG["max_pct"]

    try:
        while True:
            for symbol in CONFIG["symbols"]:
                if symbol in open_positions:
                    continue
                if len(open_positions) >= max_pos:
                    break

                price = CONFIG["initial_prices"].get(symbol, 0)
                atr = CONFIG["initial_atr"].get(symbol, 0)

                if live:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick:
                        price = tick.last or tick.bid
                    info = mt5.symbol_info(symbol)
                    # Optional: compute real ATR from bars here

                signal = get_signal(symbol)
                if signal in ("BUY", "SELL"):
                    lot = calc_lot_size(
                        symbol, price, atr, equity,
                        CONFIG["allocation_v5"].get(symbol, 0.1),
                    )
                    # Cap by max_pct of equity
                    max_notional = equity * max_pct
                    lot = min(lot, max_notional / price if price else lot)

                    if lot > 0:
                        result = place_order(symbol, signal, lot, price)
                        if result or not live:
                            open_positions[symbol] = {
                                "side": signal, "lot": lot, "entry": price,
                                "time": datetime.now(),
                            }

            # Log status
            log.info(f"Equity: {equity:.2f} | Open: {len(open_positions)}/"
                     f"{max_pos} | Positions: {list(open_positions.keys())}")

            # Scan interval
            time.sleep(60)

    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        if live:
            mt5.shutdown()
        log.info("=== Shutdown complete ===")


if __name__ == "__main__":
    main()
