# main.py
# -*- coding: utf-8 -*-
"""
Adaptive V5 US-10stocks Trading Bot — Alpaca Edition
Version: v0.4.2 (Live-only data + sanity checks + Discord)
"""

import os
import re
import time
import logging
import requests
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ============================================================
# CONFIG
# ============================================================
def _env_bool(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).strip().lower() in ("true", "1", "yes", "on")


CONFIG = {
    "version": "v0.4.2",
    "max_pos": 5,
    "max_pct": 0.22,
    "symbols": [s.strip().upper() for s in os.getenv(
        "ALPACA_SYMBOLS", "NVDA,META,MSFT,AAPL,TSLA,GOOGL,AMZN,AMD,NFLX,AVGO"
    ).split(",") if s.strip()],
    "alpaca_api_key": os.getenv("ALPACA_API_KEY", ""),
    "alpaca_secret_key": os.getenv("ALPACA_SECRET_KEY", ""),
    "alpaca_paper": _env_bool("ALPACA_PAPER", "true"),
    "discord_webhook": os.getenv("DISCORD_WEBHOOK_URL", ""),
    # --- v0.4.2 new safety flags ---
    "allow_dummy_data": _env_bool("ALLOW_DUMMY_DATA", "false"),
    "price_sanity_check": _env_bool("PRICE_SANITY_CHECK", "true"),
    "feed": os.getenv("ALPACA_FEED", "iex"),          # iex / sip
    "loop_seconds": int(os.getenv("LOOP_SECONDS", "900")),
}

# --- Price sanity bands (lo, hi) ปรับได้ตาม universe จริง ---
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
log = logging.getLogger("ADAPTIVE-ALPACA")

# ============================================================
# ERRORS
# ============================================================
class StaleDataError(Exception):
    pass


class PriceSanityError(Exception):
    pass


# ============================================================
# TICKER NORMALIZATION
# กัน string แบบ 【entity-AMD¦canonical_name=AMD】 หลุดเข้ามา
# ============================================================
_ENTITY_RE = re.compile(r"entity-([A-Z][A-Z0-9\.\-]{0,6})", re.IGNORECASE)
_TICKER_RE = re.compile(r"^[A-Z][A-Z0-9\.\-]{0,6}$")


def normalize_ticker(raw: str) -> str:
    if raw is None:
        return ""
    s = str(raw).strip()
    # 1. ลองดึงจาก pattern entity-XXX
    m = _ENTITY_RE.search(s)
    if m:
        s = m.group(1)
    s = s.upper().strip(" .")
    # 2. ต้อง match ticker pattern ไม่งั้นทิ้ง
    if not _TICKER_RE.match(s):
        log.error(f"TICKER_REJECT raw={raw!r} normalized={s!r}")
        return ""
    return s


# ============================================================
# NOTIFICATION (DISCORD)
# ============================================================
def send_discord(msg: str):
    if not CONFIG["discord_webhook"]:
        return
    try:
        payload = {
            "embeds": [{
                "title": "🤖 AI Trading Alert",
                "description": msg[:4000],
                "color": 3447003,
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
        raise ValueError("Missing ALPACA_API_KEY / ALPACA_SECRET_KEY")

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
    equity = float(account.equity)
    log.info(f"Connected: {account.account_number} | Equity=${equity:,.2f} | paper={CONFIG['alpaca_paper']}")
    send_discord(
        f"✅ **Bot Started** v{CONFIG['version']}\n"
        f"Equity: ${equity:,.2f}\n"
        f"Sanity={CONFIG['price_sanity_check']} | AllowDummy={CONFIG['allow_dummy_data']}"
    )
    return trading, data


# ============================================================
# DATA FETCHING — LIVE ONLY (no file fallback)
# ============================================================
def get_latest_price(data_client, symbol: str) -> float:
    """ดึงราคา live ล่าสุด — fail = raise, ไม่ fallback"""
    try:
        req = StockLatestTradeRequest(symbol_or_symbols=symbol, feed=CONFIG["feed"])
        trade = data_client.get_stock_latest_trade(req)
        if symbol not in trade:
            raise StaleDataError(f"no trade returned for {symbol}")
        price = float(trade[symbol].price)
    except StaleDataError:
        raise
    except Exception as e:
        raise StaleDataError(f"{symbol}: {e}") from e

    if not price or price < 1.0:
        raise StaleDataError(f"{symbol}: invalid price={price}")

    # sanity band
    if CONFIG["price_sanity_check"] and symbol in PRICE_BANDS:
        lo, hi = PRICE_BANDS[symbol]
        if not (lo <= price <= hi):
            raise PriceSanityError(
                f"{symbol} price={price} outside band ({lo},{hi}) — likely ticker map bug"
            )
    return price


def get_bars(data_client, symbol: str, days: int = 90):
    try:
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=days),
            feed=CONFIG["feed"],
        )
        resp = data_client.get_stock_bars(req)
        return resp[symbol] if symbol in resp else []
    except Exception as e:
        log.warning(f"Bars fail {symbol}: {e}")
        return []


def get_market_data(data_client, symbol: str):
    """
    Return (price, atr, bars) หรือ raise ถ้า live fail
    atr คำนวณจาก true range ของ 14 bars ล่าสุด (fallback high-low ของ bar ล่าสุด)
    """
    price = get_latest_price(data_client, symbol)
    bars = get_bars(data_client, symbol, days=90)

    atr = 0.0
    if bars and len(bars) >= 15:
        # ATR(14) แบบง่าย
        trs = []
        for i in range(1, 15):
            h = float(bars[-i].high)
            l = float(bars[-i].low)
            c_prev = float(bars[-i - 1].close)
            tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
            trs.append(tr)
        atr = sum(trs) / len(trs)
    elif bars:
        b = bars[-1]
        atr = float(b.high) - float(b.low)

    return price, atr, bars


# ============================================================
# INDICATORS
# ============================================================
def calc_ema(prices, period):
    if len(prices) < period:
        return 0.0
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = (p - ema) * multiplier + ema
    return ema


def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i - 1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ============================================================
# STRATEGY
# ============================================================
def get_signal(bars):
    if not bars or len(bars) < 30:
        return "HOLD"
    closes = [float(b.close) for b in bars]
    ema9_now = calc_ema(closes, 9)
    ema21_now = calc_ema(closes, 21)
    ema9_prev = calc_ema(closes[:-1], 9)
    ema21_prev = calc_ema(closes[:-1], 21)
    rsi = calc_rsi(closes, 14)

    if ema9_prev <= ema21_prev and ema9_now > ema21_now and rsi < 70:
        return "BUY"
    if ema9_prev >= ema21_prev and ema9_now < ema21_now:
        return "SELL"
    if rsi > 80:
        return "SELL"
    return "HOLD"


# ============================================================
# RISK & ORDER
# ============================================================
def calc_qty(price, atr, equity):
    if price <= 0 or atr <= 0 or equity <= 0:
        return 0
    risk_amount = equity * 0.01
    stop_dist = atr * 2.0
    if stop_dist <= 0:
        return 0
    qty = int(risk_amount / stop_dist)
    max_qty = int((equity * CONFIG["max_pct"]) / price)
    return max(0, min(qty, max_qty))


def place_order(trading_client, symbol, side, qty, price):
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
        emoji = "🟢" if side == "BUY" else "🔴"
        msg = f"{emoji} **{side}** {qty} × **{symbol}** @ ~${price:.2f}"
        log.info(msg)
        send_discord(msg)
        return order
    except Exception as e:
        log.error(f"Order failed {symbol}: {e}")
        send_discord(f"❌ Order Failed: {symbol} {side} — {e}")
        return None


# ============================================================
# POSITION SYNC (source of truth = broker)
# ============================================================
def sync_positions(trading_client) -> dict:
    out = {}
    try:
        for p in trading_client.get_all_positions():
            try:
                out[p.symbol] = float(p.qty)
            except Exception:
                continue
    except Exception as e:
        log.warning(f"Cannot fetch positions: {e}")
    return out


# ============================================================
# MAIN LOOP
# ============================================================
def main():
    log.info(f"=== Starting {CONFIG['version']} ===")
    log.info(f"Symbols: {CONFIG['symbols']}")
    log.info(
        f"Safety: allow_dummy={CONFIG['allow_dummy_data']} "
        f"sanity={CONFIG['price_sanity_check']} feed={CONFIG['feed']}"
    )
    if CONFIG["allow_dummy_data"]:
        log.warning("ALLOW_DUMMY_DATA=true — NOT recommended for production")

    trading, data = init_clients()

    try:
        while True:
            account = trading.get_account()
            equity = float(account.equity)

            # sync จาก broker ทุกรอบ — dict จะได้ตรงกับความจริง
            open_positions = sync_positions(trading)

            for raw_symbol in CONFIG["symbols"]:
                symbol = normalize_ticker(raw_symbol)
                if not symbol:
                    continue

                if len(open_positions) >= CONFIG["max_pos"] and symbol not in open_positions:
                    continue

                # --- ดึงข้อมูล live เท่านั้น ---
                try:
                    price, atr, bars = get_market_data(data, symbol)
                except PriceSanityError as e:
                    log.error(f"PRICE_SANITY_FAIL {e} — SKIP {symbol} (NOT HOLD)")
                    send_discord(f"⚠️ **PRICE_SANITY_FAIL** `{symbol}` — skipped\n{e}")
                    continue
                except StaleDataError as e:
                    log.error(f"LIVE_FAIL {e} — SKIP {symbol} (NOT HOLD)")
                    continue
                except Exception as e:
                    log.error(f"UNKNOWN_FAIL {symbol}: {e} — SKIP")
                    continue

                signal = get_signal(bars)
                log.info(
                    f"{symbol} | ${price:.2f} | ATR:{atr:.2f} | "
                    f"Sig:{signal} | pos:{open_positions.get(symbol, 0)}"
                )

                if signal == "BUY" and symbol not in open_positions:
                    qty = calc_qty(price, atr, equity)
                    if qty > 0:
                        order = place_order(trading, symbol, "BUY", qty, price)
                        if order:
                            # อัปเดต local เพื่อให้ loop นี้ไม่ BUY ซ้ำ
                            open_positions[symbol] = qty

                elif signal == "SELL" and symbol in open_positions:
                    qty = int(open_positions[symbol])
                    order = place_order(trading, symbol, "SELL", qty, price)
                    if order:
                        open_positions.pop(symbol, None)

            log.info(
                f"Portfolio: Equity=${equity:,.2f} | "
                f"Open: {len(open_positions)}/{CONFIG['max_pos']} {list(open_positions)}"
            )
            log.info(f"Sleeping {CONFIG['loop_seconds']}s...")
            time.sleep(CONFIG["loop_seconds"])

    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        log.info("=== Shutdown ===")


if __name__ == "__main__":
    main()
