# ... (โค้ดเดิมทั้งหมดของคุณ) ...

app = FastAPI(...)

# ===== เพิ่ม 3 บรรทัดนี้ แก้ Not Found =====
@app.get("/", include_in_schema=False)
def root():
    chk = CONFIG.self_check()
    return {
        "name": "AI Trading Core v0.3.1",
        "status": "ok",
        "version": CONFIG.VERSION,
        "hash": CONFIG.LIVE_CONFIG_10K_HASH,
        "hash_ok": chk["match"],
        "hash_actual": chk["actual"],
        "paper_trading": PAPER_TRADING,
        "endpoints": {
            "health": "/health",
            "health_alias": "/api/health",
            "ready": "/ready",
            "docs": "/docs" if PAPER_TRADING else "disabled in live",
            "trade": "/trade"
        },
        "backtest": "V4 P&L 1771 (17.7%) 126 trades WR42.1% PF1.44 DD5.4% -> V5 SCB 22.4% DELTA 22.4% ADVANC 20.6% PTTEP 20.6% PTT 14.0%",
        "time": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health", response_model=HealthResponse)
def health():
    ...

@app.get("/api/health", ...)
def health_api_alias(): return health()

# ... ที่เหลือเหมือนเดิม ...
