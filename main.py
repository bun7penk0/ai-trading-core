import json, os
from fastapi import FastAPI
from pathlib import Path

app = FastAPI(title="AI Trading Core v0.3.1-adaptive-10K")

def load_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    cfg = load_json("data/LIVE_CONFIG_10K.json")
    tiers = load_json("data/ADAPTIVE_TIERS.json")
    return {
        "status": "LIVE",
        "version": cfg.get("version","v0.3.1-adaptive-10K"),
        "tier": cfg.get("tier","SMALL_1k_10k"),
        "portfolio": cfg.get("portfolio",10000),
        "tier_config": cfg.get("tier_config"),
        "live_params": cfg.get("live_params"),
        "lot_examples": cfg.get("lot_examples"),
        "stocks_SET": cfg.get("stocks",{}).get("SET",[]),
        "formula": "shares = (portfolio * risk%) / (1.8 * ATR)",
        "example_PTT": "PTT 69sh cost 2242฿",
        "db": bool(os.getenv("DATABASE_URL")),
        "redis": bool(os.getenv("REDIS_URL"))
    }

@app.get("/api/health")
def health():
    return {"status":"LIVE","db":bool(os.getenv("DATABASE_URL")),"redis":bool(os.getenv("REDIS_URL"))}

@app.get("/api/config")
def config():
    return load_json("data/ADAPTIVE_TIERS.json")

@app.get("/api/live-config")
def live_config():
    return load_json("data/LIVE_CONFIG_10K.json")

@app.get("/api/lot")
def lot():
    return load_json("data/LIVE_CONFIG_10K.json").get("lot_examples",{})
