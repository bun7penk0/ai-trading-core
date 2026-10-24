# main.py
# -*- coding: utf-8 -*-
"""
Adaptive V5 US-10stocks Trading Bot — Alpaca Edition
Version: v0.3.4-Alpaca (Fixed Data Fetching)
"""

import os
import time
import logging
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
# --- เปลี่ยน Import สำหรับดึง Bar ---
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ============================================================
# CONFIG
# ============================================================
CONFIG = {
    "version": "v0.3.4-Alpaca",
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
# PRICE HELPER (Fixed: ใช้ Bars แทน Quote)
# ============================================================
def get_latest_bar(data_client, symbol: str):
    """ดึงแท่งเทียนล่าสุดคืนค่า (close_price, atr_approx)"""
    try:
        # ขอย้อนหลัง 3 วัน เพื่อกันวันหยุด/เสาร์อาทิตย์
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day, # ใช้ Day เพื่อลด Rate Limit
            start=datetime.now() - timedelta(days=3),
            limit=2, # เอา 2 แท่งล่าสุดมาคำนวณ ATR แบบง่าย
            feed="iex", # บัญชีฟรี
            adjustment="raw"
        )
        bars = data_client.get_stock_bars(request_params)
        
        # ถ้า iex ไม่มีข้อมูล ให้ลอง sip (เผื่ออนาคตอัปเกรด)
        if symbol not in bars or len(bars[symbol]) == 0:
            request_params.feed = "sip"
            bars = data_client.get_stock_bars(request_params)

        if symbol in bars and len(bars[symbol]) > 0:
            latest = bars[symbol][-1]
            price = float(latest.close)
            # คำนวณ ATR แบบบ้านๆ จาก High-Low ของแท่งล่าสุด
            atr = float(latest.high - latest.low) if latest.high and latest.low else 0.0
            return price, atr
    except Exception as e:
        log.warning(f"Bar fetch fail {symbol}: {e}")
    return 0.0, 0.0

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

                # --- ใช้ฟังก์ชันใหม่ ---
                price, atr = get_latest_bar(data, symbol)
                
                # ถ้าดึงราคาไม่ได้จริงๆ ให้ใช้ ATR เริ่มต้นจาก config
                if atr == 0:
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
            
            # --- เปลี่ยนเวลาพักเป็น 15 นาที (900 วินาที) ---
            log.info("Sleeping for 15 minutes...")
            time.sleep(900)

    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        log.info("=== Shutdown complete ===")

if __name__ == "__main__":
    main()
