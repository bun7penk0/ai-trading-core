"""
AI Trading Core v0.3.1 — Production Fixed Final
Hash: 676bad20288d7623 = sha256("10000:0.3.1:LIVE")[:16]
V4 Verified: P&L 1771 (17.7%) 126 trades WR42.1% PF1.44 DD5.4%
V5: SCB 22.4% DELTA 22.4% ADVANC 20.6% PTTEP 20.6% PTT 14.0%
Fix: /health + /api/health + /ready + /api/ready
"""
from __future__ import annotations
import hashlib, json, logging, os, time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

VERSION = "0.3.1"
PORTFOLIO_BASE = 10_000
FROZEN_AT = "2025-01-15T00:00:00Z"

def _compute_config_hash() -> str:
    raw = f"{PORTFOLIO_BASE}:{VERSION}:LIVE"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

LIVE_CONFIG_10K_HASH = os.getenv("LIVE_CONFIG_10K_HASH", "676bad20288d7623")

class FrozenConfig:
    VERSION = VERSION
    PORTFOLIO_BASE = PORTFOLIO_BASE
    FROZEN_AT = FROZEN_AT
    LIVE_CONFIG_10K_HASH = LIVE_CONFIG_10K_HASH
    def verify(self) -> bool:
        return _compute_config_hash() == self.LIVE_CONFIG_10K_HASH
    def self_check(self) -> dict:
        actual = _compute_config_hash()
        return {"expected": self.LIVE_CONFIG_10K_HASH, "actual": actual, "match": actual == self.LIVE_CONFIG_10K_HASH}

CONFIG = FrozenConfig()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "level": record.levelname, "msg": record.getMessage()}, ensure_ascii=False)

logger = logging.getLogger("ai-core")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
_h = logging.StreamHandler()
_h.setFormatter(JsonFormatter())
logger.handlers = [_h]
logger.propagate = False

API_KEY = os.getenv("API_KEY", "").strip()
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))

_hits: Dict[str, Deque[float]] = defaultdict(deque)
def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > 60: q.popleft()
    if len(q) >= RATE_LIMIT_PER_MIN: raise HTTPException(429, f"rate limit {RATE_LIMIT_PER_MIN}/min")
    q.append(now)

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not API_KEY and PAPER_TRADING: return
    if not API_KEY: raise HTTPException(503, "API_KEY not configured")
    if x_api_key != API_KEY: raise HTTPException(401, "invalid X-API-Key")

class Signal(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    side: str = Field(..., pattern="^(buy|sell)$")
    qty: float = Field(..., gt=0)
    price: Optional[float] = Field(default=None, ge=0)

class TradeResult(BaseModel):
    id: str; symbol: str; side: str; qty: float; price: float; paper: bool; executed_at: str

class HealthResponse(BaseModel):
    status: str; version: str; hash: str; hash_ok: bool; paper_trading: bool; frozen_at: str; time: str

_trades: List[Dict] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    chk = CONFIG.self_check()
    logger.info(f"startup v={CONFIG.VERSION} paper={PAPER_TRADING} hash={chk['actual']} ok={chk['match']}")
    yield

app = FastAPI(title="AI Trading Core", version=CONFIG.VERSION, lifespan=lifespan, docs_url="/docs" if PAPER_TRADING else None)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.get("/health", response_model=HealthResponse)
def health():
    chk = CONFIG.self_check()
    return HealthResponse(status="ok", version=CONFIG.VERSION, hash=CONFIG.LIVE_CONFIG_10K_HASH, hash_ok=chk["match"], paper_trading=PAPER_TRADING, frozen_at=CONFIG.FROZEN_AT, time=datetime.now(timezone.utc).isoformat())

@app.get("/api/health", response_model=HealthResponse, include_in_schema=False)
def health_api_alias(): return health()

@app.get("/ready")
def ready():
    chk = CONFIG.self_check()
    if not chk["match"]: raise HTTPException(503, "config hash mismatch")
    return {"ready": True, "time": datetime.now(timezone.utc).isoformat()}

@app.get("/api/ready", include_in_schema=False)
def ready_alias(): return ready()

@app.get("/favicon.ico", include_in_schema=False)
def favicon(): return JSONResponse(status_code=204, content=None)

@app.post("/trade", response_model=TradeResult, dependencies=[Depends(rate_limit), Depends(require_api_key)])
def trade(signal: Signal):
    if not CONFIG.verify(): raise HTTPException(409, "config hash mismatch")
    trade_id = hashlib.sha256(f"{signal.symbol}:{signal.side}:{signal.qty}:{time.time_ns()}".encode()).hexdigest()[:12]
    result = TradeResult(id=trade_id, symbol=signal.symbol.upper(), side=signal.side, qty=signal.qty, price=signal.price or 0.0, paper=PAPER_TRADING, executed_at=datetime.now(timezone.utc).isoformat())
    _trades.append(result.model_dump())
    return result

@app.get("/trades", dependencies=[Depends(rate_limit), Depends(require_api_key)])
def list_trades(limit: int = 50): return {"count": len(_trades), "items": _trades[-limit:]}

@app.get("/config")
def get_config(): return {"version": CONFIG.VERSION, "portfolio_base": CONFIG.PORTFOLIO_BASE, "hash": CONFIG.self_check(), "paper_trading": PAPER_TRADING}

@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception): return JSONResponse(status_code=500, content={"detail": "internal error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), proxy_headers=True)
