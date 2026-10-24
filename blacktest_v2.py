# backtest.py
# -*- coding: utf-8 -*-
"""
Backtest Script for Adaptive V5 Strategy (EMA 9/21 + RSI)
"""

import os
import logging
from datetime import datetime, timedelta

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ============================================================
# CONFIG
# ============================================================
API_KEY = os.getenv("ALPACA_API_KEY", "ใส่_KEY_ของคุณตรงนี้")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "ใส่_SECRET_ของคุณตรงนี้")
SYMBOLS = ["NVDA", "META", "MSFT", "AAPL", "TSLA", "GOOGL", "AMZN", "AMD", "NFLX", "AVGO"]
STARTING_CAPITAL = 10000 # เริ่มทดสอบด้วย 10,000 USD
RISK_PER_TRADE = 0.01    # เสี่ยง 1% ต่อการเทรด 1 ครั้ง

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("BACKTEST")

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
# MAIN BACKTEST LOGIC
# ============================================================
def run_backtest():
    log.info(f"=== เริ่มการทดสอบย้อนหลัง (Backtest) ===")
    log.info(f"หุ้นที่ทดสอบ: {SYMBOLS}")
    log.info(f"เงินทุนเริ่มต้น: ${STARTING_CAPITAL:,.2f}\n")

    data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    
    total_trades = 0
    wins = 0
    losses = 0
    total_pnl = 0.0
    
    # เก็บสถิติรายหุ้น
    stock_stats = {s: {"trades": 0, "pnl": 0.0} for s in SYMBOLS}

    for symbol in SYMBOLS:
        log.info(f"--- กำลังประมวลผล: {symbol} ---")
        
        # ดึงข้อมูลย้อนหลัง 2 ปี (เพื่อให้มีแท่งเทียนพอสำหรับ EMA 21)
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=730),
            feed="iex"
        )
        
        try:
            bars = data_client.get_stock_bars(req)[symbol]
        except Exception as e:
            log.error(f"ดึงข้อมูล {symbol} ไม่ได้: {e}")
            continue

        if len(bars) < 30:
            log.warning(f"ข้อมูลไม่พอสำหรับ {symbol}")
            continue

        in_position = False
        entry_price = 0.0
        qty = 0

        # วนลูปดูแท่งเทียนทีละวัน
        for i in range(25, len(bars)):
            current_bar = bars[i]
            closes = [b.close for b in bars[:i+1]]
            price = float(current_bar.close)
            atr = float(current_bar.high - current_bar.low)

            # คำนวณอินดิเคเตอร์
            ema9 = calc_ema(closes, 9)
            ema21 = calc_ema(closes, 21)
            ema9_prev = calc_ema(closes[:-1], 9)
            ema21_prev = calc_ema(closes[:-1], 21)
            rsi = calc_rsi(closes, 14)

            # --- สัญญาณซื้อ ---
            if not in_position:
                if ema9_prev <= ema21_prev and ema9 > ema21 and rsi < 70:
                    in_position = True
                    entry_price = price
                    # คำนวณจำนวนหุ้นจาก Risk
                    risk_amount = STARTING_CAPITAL * RISK_PER_TRADE
                    stop_dist = atr * 2.0 if atr > 0 else price * 0.05
                    qty = int(risk_amount / stop_dist)
                    if qty == 0: qty = 1 # ซื้อขั้นต่ำ 1 หุ้น

            # --- สัญญาณขาย ---
            elif in_position:
                # ขายเมื่อ EMA ตัดลง หรือ RSI Overbought
                if (ema9_prev >= ema21_prev and ema9 < ema21) or rsi > 80:
                    pnl = (price - entry_price) * qty
                    total_pnl += pnl
                    total_trades += 1
                    stock_stats[symbol]["trades"] += 1
                    stock_stats[symbol]["pnl"] += pnl
                    
                    if pnl > 0: wins += 1
                    else: losses += 1
                    
                    in_position = False

    # ============================================================
    # สรุปผลลัพธ์
    # ============================================================
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    final_equity = STARTING_CAPITAL + total_pnl
    roi = (total_pnl / STARTING_CAPITAL) * 100

    log.info("\n=========================================")
    log.info("           สรุปผลการทดสอบ (2 ปี)          ")
    log.info("=========================================")
    log.info(f"จำนวนการเทรดทั้งหมด: {total_trades} ครั้ง")
    log.info(f"Win Rate: {win_rate:.1f}% (ชนะ {wins} / แพ้ {losses})")
    log.info(f"กำไร/ขาดทุนสุทธิ (P&L): ${total_pnl:,.2f}")
    log.info(f"ผลตอบแทน (ROI): {roi:.2f}%")
    log.info(f"เงินทุนสุดท้าย: ${final_equity:,.2f}")
    
    log.info("\n--- สถิติรายหุ้น ---")
    for s, data in stock_stats.items():
        log.info(f"{s}: {data['trades']} เทรด | P&L: ${data['pnl']:,.2f}")
    log.info("=========================================\n")

if __name__ == "__main__":
    run_backtest()
