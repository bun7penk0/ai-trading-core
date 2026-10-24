# main.py
# -*- coding: utf-8 -*-
"""
Adaptive V5 US-10stocks Trading Bot — Alpaca Edition
Version: v0.3.5-Alpaca (Robust Snapshot Data Fetching)
"""

import os
import time
import logging
from datetime import datetime

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
# --- เปลี่ยน Import สำหรับดึง Snapshot ---
from alpaca.data.requests import StockSnapshotRequest

# ============================================================
# CONFIG
# ============================================================
CONFIG = {
    "version": "v0.3.5-Alpaca",
    "portfolio": 10000,
    "max_pos": 5,
    "max_pct": 0.22,
    "allocation_v5": {
        "NVDA": 0.1, "META": 0.1, "MSFT": 0.1, "AAPL": 0.1, "TSLA": 0.1,
        "GOOGL": 0.1, "AMZN": 0.1, "AMD": 0.1, "NFLX": 0.1, "AVGO": 0.1,
    },
    "initial_atr": {
        "NVDA": 5.2, "META": 8.5, "MSFT": 4.8, "AAPL": 2.8, "TSLA": 6.5,
        "GOOGL": 3.2, "AMZN": 3.5, "AMD": 4.1, "NFLX": 12.0, "AVGO": 4.5,
    },
    "symbols": [s.strip() for s in os.getenv(
        "ALPACA_SYMBOLS",
        "NVDA,META,MSFT,AAPL,TSLA,GOOGL,AMZN,AMD,NFLX,AVGO"
    ).split(",") if s.strip()],
    "alpaca_api_key": os.getenv("ALPACA_API_KEY", ""),
    "alpaca_secret_key": os.getenv("ALPACA_SECRET_KEY", ""),
    "alpaca_paper": os.getenv("ALPACA_PAPER", "true").lower() in ("true", "1", "yes"),
}

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ADAPTIVE-ALPACA")

# ============================================================
# ALPACA CLIENTS
# ============================================================
def init_clients():
    if not CONFIG["alpaca_api_key"] or not CONFIG["alpaca_secret_key"]:
        raise ValueError("Missing ALPACA_API_KEY / ALPACA_SECRET_KEY in environment")

    trading = TradingClient(
        CONFIG["alpaca_api_key"],
        CONFIG["alpaca_secret_key"],
        paper=CONFIG["alpaca_paper"],
    )
    data = StockHistoricalDataClient(
        CONFIG["alpaca_api_key"],
        CONFIG["alpaca_secret_key"],
    )
    account = trading.get_account()
    log.info(f"Connected: {account.account_number} | "
             f"Paper={CONFIG['alpaca_paper']} | "
             f"Equity={account.equity} | "
             f"BuyingPower={account.buying_power}")
    return trading, data

# ============================================================
# PRICE HELPER (ใช้ Snapshot ดึงราคาปิดวันล่าสุด)
# ============================================================
def get_latest_price(data_client, symbol: str):
    """ดึงราคาปิดของวันซื้อขายล่าสุด พร้อม fallback feed"""
    try:
        req = StockSnapshotRequest(symbol_or_symbols=symbol, feed="iex")
        snapshot = data_client.get_stock_snapshot(req)
        
        if symbol in snapshot:
            snap = snapshot[symbol]
            # ลำดับการหาปราคา: Daily Bar -> Latest Trade -> Latest Quote -> Min Bar
            if snap.daily_bar:
                return float(snap.daily_bar.close)
            elif snap.latest_trade:
                return float(snap.latest_trade.price)
            elif snap.latest_quote:
                return float((snap.latest_quote.bid_price + snap.latest_quote.ask_price) / 2)
            elif snap.minute_bar:
                return float(snap.minute_bar.close)
                
        # Fallback: ถ้า IEX ไม่มีข้อมูล ลองขอผ่าน SIP
        req.feed = "sip"
        snapshot = data_client.get_stock_snapshot(req)
        if symbol in snapshot and snapshot[symbol].daily_bar:
            return float(snapshot[symbol].daily_bar.close)
            
    except Exception as e:
        log.error(f"Snapshot fail {symbol}: {e}")
    return 0.0

# ============================================================
# POSITION SIZING
# ============================================================
def calc_qty(price: float, atr: float, equity: float, alloc_pct: float) -> int:
    if price <= 0 or atr <= 0:
        return 0
    risk_per_trade = equity * alloc_pct * 0.01
    stop_distance = atr * 1.5
    shares = int(risk_per_trade / stop_distance)
    max_shares = int((equity * CONFIG["max_pct"]) / price)
    return max(0, min(shares, max_shares))

# ============================================================
# SIGNAL (Placeholder)
# ============================================================
def get_signal(symbol: str) -> str:
    # TODO: EMA cross / RSI / MACD
    return "HOLD"

# ============================================================
# ORDER
# ============================================================
def place_order(trading_client, symbol: str, side: str, qty: int):
    if qty <= 0:
        return None
    try:
        order = trading_client.submit_order(
            MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
        )
        log.info(f"Order OK {symbol} {side} {qty} @ market | id={order.id}")
        return order
    except Exception as e:
        log.error(f"Order failed {symbol} {side} {qty}: {e}")
        return None

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    log.info(f"=== Starting {CONFIG['version']} ===")
    log.info(f"Symbols: {CONFIG['symbols']}")

    trading, data = init_clients()

    open_symbols = set()
    try:
        positions = trading.get_all_positions()
        open_symbols = {p.symbol for p in positions}
        log.info(f"Existing positions: {open_symbols or 'none'}")
    except Exception as e:
        log.warning(f"Cannot fetch positions: {e}")

    try:
        while True:
            try:
                account = trading.get_account()
                equity = float(account.equity)
            except Exception as e:
                log.error(f"Account fetch failed: {e}")
                time.sleep(30)
                continue

            for symbol in CONFIG["symbols"]:
                if symbol in open_symbols:
                    continue
                if len(open_symbols) >= CONFIG["max_pos"]:
                    break

                # --- ใช้ฟังก์ชัน Snapshot ---
                price = get_latest_price(data, symbol)
                
                # ใช้ ATR เริ่มต้นจาก config (เพราะ Snapshot ไม่มี High/Low ให้คำนวณง่ายๆ)
                atr = CONFIG["initial_atr"].get(symbol, 1.0)

                if price <= 0:
                    log.warning(f"{symbol} no price, skip")
                    continue

                signal = get_signal(symbol)
                log.info(f"{symbol} price={price:.2f} atr={atr:.2f} signal={signal}")

                if signal in ("BUY", "SELL"):
                    qty = calc_qty(price, atr, equity,
                                   CONFIG["allocation_v5"].get(symbol, 0.1))
                    if qty > 0:
                        order = place_order(trading, symbol, signal, qty)
                        if order:
                            open_symbols.add(symbol)

            log.info(f"Equity={equity:.2f} | Open={len(open_symbols)}/"
                     f"{CONFIG['max_pos']} | {sorted(open_symbols)}")
            
            # --- พัก 5 นาที (300 วินาที) เพื่อไม่ให้ถี่เกินไป ---
            log.info("Sleeping for 5 minutes...")
            time.sleep(300)

    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        log.info("=== Shutdown complete ===")

if __name__ == "__main__":
    main()
