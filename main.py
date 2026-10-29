# main.py
# -*- coding: utf-8 -*-
"""
Adaptive V5 US-10stocks Trading Bot — Hybrid Edition
Version: v0.4.5 (Alpaca Trading + Yahoo Finance Data + Timezone Fix)
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo  # ✅ แก้ไข: เพิ่ม import

# --- Alpaca Imports (สำหรับเทรดเท่านั้น) ---
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# --- Yahoo Finance Imports (สำหรับดึงข้อมูล) ---
import yfinance as yf

# ============================================================
# CONFIG
# ============================================================
def _env_bool(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).strip().lower() in ("true", "1", "yes", "on")

CONFIG = {
    "version": "v0.4.5",  # ✅ แก้ไข: bump version
    "max_pos": 5,
    "max_pct": 0.22,
    "symbols": [s.strip().upper() for s in os.getenv(
        "ALPACA_SYMBOLS", "NVDA,META,MSFT,AAPL,TSLA,GOOGL,AMZN,AMD,NFLX,AVGO"
    ).split(",") if s.strip()],
    "alpaca_api_key": os.getenv("ALPACA_API_KEY", ""),
    "alpaca_secret_key": os.getenv("ALPACA_SECRET_KEY", ""),
    "alpaca_paper": _env_bool("ALPACA_PAPER", "true"),
    "discord_webhook": os.getenv("DISCORD_WEBHOOK_URL", ""),
    "price_sanity_check": _env_bool("PRICE_SANITY_CHECK", "true"),
    "loop_seconds": int(os.getenv("LOOP_SECONDS", "900")),
}

# ✅ แก้ไข: timezone constants
ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

# --- Price sanity bands (lo, hi) ---
PRICE_BANDS = {
    "NVDA":  (40, 500),
    "META":  (150, 1200),
    "MSFT":  (150, 800),
    "AAPL":  (100, 400),
    "TSLA":  (80, 800),
    "GOOGL": (80, 500),
    "AMZN":  (80, 500),
    "AMD":   (50, 400),
    "NFLX":  (400, 2000),
    "AVGO":  (150, 3000),
}

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ADAPTIVE-HYBRID")

class PriceSanityError(Exception): pass

# ============================================================
# NOTIFICATION
# ============================================================
def send_discord(msg: str):
    if not CONFIG["discord_webhook"]: return
    try:
        payload = {"embeds": [{"title": "🤖 AI Trading Alert", "description": msg[:4000], "color": 3447003}]}
        requests.post(CONFIG["discord_webhook"], json=payload, timeout=5)
    except Exception as e:
        log.warning(f"Discord send failed: {e}")

# ============================================================
# ✅ แก้ไข: MARKET CLOCK HELPERS
# ============================================================
def is_market_open_fallback(now_et: datetime) -> bool:
    """Fallback ตรวจสอบเวลาเปิด-ปิดตลาด แบบ manual (กรณี Alpaca clock ผิด)"""
    if now_et.weekday() >= 5:  # เสาร์-อาทิตย์
        return False
    t = now_et.time()
    return time(9, 30) <= t < time(16, 0)


def check_market_status(trading) -> tuple[bool, datetime, str]:
    """
    คืนค่า (is_open, next_open_et, source)
    - source = 'alpaca' หรือ 'fallback'
    - ถ้า Alpaca แจ้งปิด แต่เวลา ET อยู่ในช่วงเปิดจริง → ใช้ fallback
    """
    now_et = datetime.now(ET)
    
    try:
        clock = trading.get_clock()
        is_open_alpaca = bool(clock.is_open)
        # ✅ แก้ไข: astimezone(ET) แทน astimezone() เปล่า ๆ
        next_open_et = clock.next_open.astimezone(ET)
        
        # ✅ แก้ไข: ถ้า Alpaca บอกปิด แต่ ET อยู่ในช่วงเปิด → override
        if not is_open_alpaca and is_market_open_fallback(now_et):
            log.warning(
                f"⚠️ Alpaca clock says CLOSED but ET={now_et.strftime('%H:%M')} "
                f"is within market hours → using fallback"
            )
            return True, now_et, "fallback"
        
        return is_open_alpaca, next_open_et, "alpaca"
    
    except Exception as e:
        log.error(f"get_clock() failed: {e} → using fallback")
        is_open = is_market_open_fallback(now_et)
        return is_open, now_et, "fallback"

# ============================================================
# ALPACA CLIENT (Trading Only)
# ============================================================
def init_trading_client():
    if not CONFIG["alpaca_api_key"] or not CONFIG["alpaca_secret_key"]:
        raise ValueError("Missing ALPACA_API_KEY / ALPACA_SECRET_KEY")

    trading = TradingClient(CONFIG["alpaca_api_key"], CONFIG["alpaca_secret_key"], paper=CONFIG["alpaca_paper"])
    account = trading.get_account()
    equity = float(account.equity)
    log.info(f"Connected: {account.account_number} | Equity=${equity:,.2f} | paper={CONFIG['alpaca_paper']}")
    send_discord(f"✅ **Bot Started** v{CONFIG['version']}\nEquity: ${equity:,.2f}\n(Data via Yahoo Finance)")
    return trading

# ============================================================
# DATA FETCHING (Yahoo Finance)
# ============================================================
def get_market_data(symbol: str):
    """
    ดึงข้อมูลจาก Yahoo Finance แทน Alpaca IEX ที่เพี้ยน
    """
    try:
        ticker = yf.Ticker(symbol)
        # ดึงข้อมูล 3 เดือน (1d interval)
        hist = ticker.history(period="3mo", interval="1d")
        
        if hist.empty:
            raise ValueError("No data returned from Yahoo Finance")

        # 1. ราคาล่าสุด (ใช้ Close ล่าสุด)
        price = float(hist['Close'].iloc[-1])
        
        # 2. คำนวณ ATR (14 วัน)
        atr = 0.0
        if len(hist) >= 15:
            hist['H-L'] = hist['High'] - hist['Low']
            hist['H-PC'] = abs(hist['High'] - hist['Close'].shift(1))
            hist['L-PC'] = abs(hist['Low'] - hist['Close'].shift(1))
            hist['TR'] = hist[['H-L', 'H-PC', 'L-PC']].max(axis=1)
            atr = float(hist['TR'].tail(14).mean())
        else:
            atr = float(hist['High'].iloc[-1] - hist['Low'].iloc[-1])

        # Fallback ATR ถ้าเป็น 0
        if atr <= 0:
            atr = price * 0.02

        # 3. แปลงข้อมูลเป็น List of Bars สำหรับส่งให้ Strategy
        bars = []
        for _, row in hist.iterrows():
            bar = type('Bar', (object,), {
                'close': row['Close'],
                'high': row['High'],
                'low': row['Low'],
                'open': row['Open'],
                'volume': row['Volume']
            })
            bars.append(bar)

        # --- Sanity Check ---
        if CONFIG["price_sanity_check"] and symbol in PRICE_BANDS:
            lo, hi = PRICE_BANDS[symbol]
            if not (lo <= price <= hi):
                raise PriceSanityError(f"{symbol} price={price} outside band ({lo},{hi})")

        return price, atr, bars

    except Exception as e:
        log.error(f"Yahoo Data fail {symbol}: {e}")
        return None, None, None

# ============================================================
# INDICATORS
# ============================================================
def calc_ema(prices, period):
    if len(prices) < period: return 0.0
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]: ema = (p - ema) * multiplier + ema
    return ema

def calc_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i - 1]
        if diff > 0: gains += diff
        else: losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ============================================================
# STRATEGY
# ============================================================
def get_signal(bars):
    if not bars or len(bars) < 30: return "HOLD"
    closes = [float(b.close) for b in bars]
    ema9_now = calc_ema(closes, 9)
    ema21_now = calc_ema(closes, 21)
    ema9_prev = calc_ema(closes[:-1], 9)
    ema21_prev = calc_ema(closes[:-1], 21)
    rsi = calc_rsi(closes, 14)

    if ema9_prev <= ema21_prev and ema9_now > ema21_now and rsi < 70: return "BUY"
    if ema9_prev >= ema21_prev and ema9_now < ema21_now: return "SELL"
    if rsi > 80: return "SELL"
    return "HOLD"

# ============================================================
# RISK & ORDER & POSITION
# ============================================================
def calc_qty(price, atr, equity):
    if price <= 0 or atr <= 0 or equity <= 0: return 0
    risk_amount = equity * 0.01
    stop_dist = atr * 2.0
    if stop_dist <= 0: return 0
    qty = int(risk_amount / stop_dist)
    max_qty = int((equity * CONFIG["max_pct"]) / price)
    return max(0, min(qty, max_qty))

def place_order(trading_client, symbol, side, qty, price):
    if qty <= 0: return None
    try:
        order = trading_client.submit_order(MarketOrderRequest(
            symbol=symbol, qty=qty, side=OrderSide.BUY if side == "BUY" else OrderSide.SELL, time_in_force=TimeInForce.DAY))
        emoji = "🟢" if side == "BUY" else "🔴"
        msg = f"{emoji} **{side}** {qty} × **{symbol}** @ ~${price:.2f}"
        log.info(msg); send_discord(msg)
        return order
    except Exception as e:
        log.error(f"Order failed {symbol}: {e}")
        send_discord(f"❌ Order Failed: {symbol} {side} — {e}")
        return None

def sync_positions(trading_client) -> dict:
    out = {}
    try:
        for p in trading_client.get_all_positions():
            try: out[p.symbol] = float(p.qty)
            except: pass
    except Exception as e: log.warning(f"Cannot fetch positions: {e}")
    return out

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    log.info(f"=== Starting {CONFIG['version']} (Hybrid: Alpaca Trade + Yahoo Data) ===")
    trading = init_trading_client()

    try:
        while True:
            # ✅ แก้ไข: ใช้ helper function + timezone ET + debug log
            now_utc = datetime.now(UTC)
            now_et  = datetime.now(ET)
            
            is_open, next_open_et, source = check_market_status(trading)
            
            log.info(
                f"[CLOCK] UTC={now_utc.strftime('%H:%M')} | "
                f"ET={now_et.strftime('%H:%M %Z')} | "
                f"open={is_open} | src={source} | "
                f"next_open_ET={next_open_et.strftime('%Y-%m-%d %H:%M %Z')}"
            )

            if not is_open:
                log.info(
                    f"Market closed. Next open: "
                    f"{next_open_et.strftime('%Y-%m-%d %H:%M %Z')}. Sleeping 60s."
                )
                time.sleep(60)
                continue

            # --- ส่วนนี้เหมือนเดิมทุกอย่าง ---
            account = trading.get_account()
            equity = float(account.equity)
            open_positions = sync_positions(trading)

            for symbol in CONFIG["symbols"]:
                if len(open_positions) >= CONFIG["max_pos"] and symbol not in open_positions:
                    continue

                price, atr, bars = get_market_data(symbol)
                
                if not price:
                    log.warning(f"{symbol} no data from Yahoo, skip")
                    continue

                signal = get_signal(bars)
                log.info(f"{symbol} | ${price:.2f} | ATR:{atr:.2f} | Sig:{signal} | pos:{open_positions.get(symbol, 0)}")

                if signal == "BUY" and symbol not in open_positions:
                    qty = calc_qty(price, atr, equity)
                    if qty > 0:
                        order = place_order(trading, symbol, "BUY", qty, price)
                        if order: open_positions[symbol] = qty
                            
                elif signal == "SELL" and symbol in open_positions:
                    qty = int(open_positions[symbol])
                    order = place_order(trading, symbol, "SELL", qty, price)
                    if order: open_positions.pop(symbol, None)

            log.info(f"Portfolio: Equity=${equity:,.2f} | Open: {len(open_positions)}/{CONFIG['max_pos']}")
            log.info(f"Sleeping {CONFIG['loop_seconds']}s...")
            time.sleep(CONFIG["loop_seconds"])

    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        log.info("=== Shutdown ===")

if __name__ == "__main__":
    main()
