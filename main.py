# main.py
# -*- coding: utf-8 -*-
"""
Adaptive V5 US-10stocks Trading Bot — Alpaca Edition
Version: v0.4.1 (Discord Integration)
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ============================================================
# CONFIG
# ============================================================
CONFIG = {
    "version": "v0.4.1",
    "max_pos": 5,
    "max_pct": 0.22,
    "symbols": [s.strip() for s in os.getenv(
        "ALPACA_SYMBOLS", "NVDA,META,MSFT,AAPL,TSLA,GOOGL,AMZN,AMD,NFLX,AVGO"
    ).split(",") if s.strip()],
    "alpaca_api_key": os.getenv("ALPACA_API_KEY", ""),
    "alpaca_secret_key": os.getenv("ALPACA_SECRET_KEY", ""),
    "alpaca_paper": os.getenv("ALPACA_PAPER", "true").lower() in ("true", "1", "yes"),
    "discord_webhook": os.getenv("DISCORD_WEBHOOK_URL", ""), # <--- เปลี่ยนเป็น Discord
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
# NOTIFICATION (DISCORD)
# ============================================================
def send_discord(msg: str):
    if not CONFIG["discord_webhook"]:
        return
    try:
        # ส่งข้อความแบบ Embed สวยๆ ไปที่ Discord
        payload = {
            "embeds": [{
                "title": "🤖 AI Trading Alert",
                "description": msg,
                "color": 3447003 # สีฟ้า
            }]
        }
        requests.post(CONFIG["discord_webhook"], json=payload, timeout=5)
    except Exception as e:
        log.warning(f"Discord send failed: {e}")

# ============================================================
# ALPACA CLIENTS
# ============================================================
def init_clients():
    if not CONFIG["alpaca_api_key"] or not CONFIG["alpaca_secret_key"]:
        raise ValueError("Missing ALPACA keys")
    
    trading = TradingClient(CONFIG["alpaca_api_key"], CONFIG["alpaca_secret_key"], paper=CONFIG["alpaca_paper"])
    data = StockHistoricalDataClient(CONFIG["alpaca_api_key"], CONFIG["alpaca_secret_key"])
    
    account = trading.get_account()
    log.info(f"Connected: {account.account_number} | Equity=${float(account.equity):,.2f}")
    
    # แจ้งเตือนตอนเริ่มระบบ
    send_discord(f"✅ **Bot Started**\nVersion: {CONFIG['version']}\nEquity: ${float(account.equity):,.2f}")
    return trading, data

# ============================================================
# DATA FETCHING
# ============================================================
def get_market_data(data_client, symbol):
    try:
        # 1. Snapshot
        req = StockSnapshotRequest(symbol_or_symbols=symbol, feed="iex")
        snap = data_client.get_stock_snapshot(req)
        
        price, atr = 0.0, 0.0
        if symbol in snap and snap[symbol].daily_bar:
            bar = snap[symbol].daily_bar
            price = float(bar.close)
            atr = float(bar.high - bar.low)
        
        # 2. Bars
        req_bars = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=90),
            feed="iex"
        )
        bars_resp = data_client.get_stock_bars(req_bars)
        bars = bars_resp[symbol] if symbol in bars_resp else []
        
        return price, atr, bars
    except Exception as e:
        log.error(f"Data fail {symbol}: {e}")
        return 0.0, 0.0, []

# ============================================================
# INDICATORS
# ============================================================
def calc_ema(prices, period):
    if len(prices) < period: return 0.0
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = (p - ema) * multiplier + ema
    return ema

def calc_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    gains, losses = 0, 0
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i-1]
        if diff > 0: gains += diff
        else: losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ============================================================
# STRATEGY LOGIC
# ============================================================
def get_signal(bars):
    if not bars or len(bars) < 30: return "HOLD"
    
    closes = [float(b.close) for b in bars]
    ema9_now = calc_ema(closes, 9)
    ema21_now = calc_ema(closes, 21)
    ema9_prev = calc_ema(closes[:-1], 9)
    ema21_prev = calc_ema(closes[:-1], 21)
    rsi = calc_rsi(closes, 14)
    
    if ema9_prev <= ema21_prev and ema9_now > ema21_now and rsi < 70:
        return "BUY"
    elif ema9_prev >= ema21_prev and ema9_now < ema21_now:
        return "SELL"
    elif rsi > 80:
        return "SELL"
    return "HOLD"

# ============================================================
# RISK & ORDER
# ============================================================
def calc_qty(price, atr, equity):
    if price <= 0 or atr <= 0: return 0
    risk_amount = equity * 0.01
    stop_dist = atr * 2.0
    qty = int(risk_amount / stop_dist)
    max_qty = int((equity * CONFIG["max_pct"]) / price)
    return max(0, min(qty, max_qty))

def place_order(trading_client, symbol, side, qty, price):
    try:
        order = trading_client.submit_order(
            MarketOrderRequest(
                symbol=symbol, qty=qty,
                side=OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
        )
        # แจ้งเตือน Discord
        emoji = "🟢" if side == "BUY" else "🔴"
        msg = f"{emoji} **{side}** {qty} shares of **{symbol}** @ ~${price:.2f}"
        log.info(msg)
        send_discord(msg)
        return order
    except Exception as e:
        log.error(f"Order failed {symbol}: {e}")
        send_discord(f"❌ Order Failed: {symbol} {side} - {e}")
        return None

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    log.info(f"=== Starting {CONFIG['version']} ===")
    trading, data = init_clients()

    open_positions = {}
    try:
        for p in trading.get_all_positions():
            open_positions[p.symbol] = float(p.qty)
        log.info(f"Existing positions: {open_positions or 'none'}")
    except Exception as e:
        log.warning(f"Cannot fetch positions: {e}")

    try:
        while True:
            account = trading.get_account()
            equity = float(account.equity)
            
            for symbol in CONFIG["symbols"]:
                if len(open_positions) >= CONFIG["max_pos"] and symbol not in open_positions:
                    continue
                    
                price, atr, bars = get_market_data(data, symbol)
                
                if price <= 0:
                    log.warning(f"{symbol} no price, skip")
                    continue
                
                signal = get_signal(bars)
                log.info(f"{symbol} | ${price:.2f} | ATR:{atr:.2f} | Sig:{signal}")

                if signal == "BUY" and symbol not in open_positions:
                    qty = calc_qty(price, atr, equity)
                    if qty > 0:
                        order = place_order(trading, symbol, "BUY", qty, price)
                        if order: open_positions[symbol] = qty
                            
                elif signal == "SELL" and symbol in open_positions:
                    qty = int(open_positions[symbol])
                    order = place_order(trading, symbol, "SELL", qty, price)
                    if order: del open_positions[symbol]

            log.info(f"Portfolio: Equity=${equity:,.2f} | Open: {len(open_positions)}/{CONFIG['max_pos']}")
            log.info("Sleeping for 15 minutes...")
            time.sleep(900)

    except KeyboardInterrupt:
        log.info("Stopped.")
    finally:
        log.info("=== Shutdown ===")

if __name__ == "__main__":
    main()
