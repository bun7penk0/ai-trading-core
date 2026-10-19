
"""
AI Trading Core v0.3.1
Single-file FastAPI application
Paper trading by default.
WARNING: /trade records simulated trades only; no broker integration.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


# =========================================================
# CONFIG
# =========================================================

VERSION = "0.3.1"
PORTFOLIO_BASE = 10_000
FROZEN_AT = "2025-01-15T00:00:00Z"


def _compute_config_hash() -> str:
    raw = f"{PORTFOLIO_BASE}:{VERSION}:LIVE"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


LIVE_CONFIG_10K_HASH = os.getenv(
    "LIVE_CONFIG_10K_HASH",
    "0000000000000000",
)


class FrozenConfig:
    VERSION = VERSION
    PORTFOLIO_BASE = PORTFOLIO_BASE
    FROZEN_AT = FROZEN_AT
    LIVE_CONFIG_10K_HASH = LIVE_CONFIG_10K_HASH

    def verify(self) -> bool:
        return _compute_config_hash() == self.LIVE_CONFIG_10K_HASH

    def self_check(self) -> dict:
        actual = _compute_config_hash()
        return {
            "expected": self.LIVE_CONFIG_10K_HASH,
            "actual": actual,
            "match": actual == self.LIVE_CONFIG_10K_HASH,
        }


CONFIG = FrozenConfig()


# =========================================================
# JSON LOGGING
# =========================================================

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("ai-core")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

_handler = logging.StreamHandler()
_handler.setFormatter(JsonFormatter())
logger.handlers = [_handler]
logger.propagate = False


# =========================================================
# ENVIRONMENT
# =========================================================

API_KEY = os.getenv("API_KEY", "").strip()
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

RATE_LIMIT_PER_MIN = max(
    1, int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
)


# =========================================================
# IN-MEMORY RATE LIMITER
# =========================================================

_hits: Dict[str, Deque[float]] = defaultdict(deque)
_WINDOW = 60.0


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    queue = _hits[ip]

    while queue and now - queue[0] >= _WINDOW:
        queue.popleft()

    if len(queue) >= RATE_LIMIT_PER_MIN:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    queue.append(now)


# =========================================================
# API KEY AUTHENTICATION
# =========================================================

def require_api_key(
    x_api_key: Optional[str] = Header(default=None),
) -> None:
    if not API_KEY:
        if PAPER_TRADING:
            return

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY not configured",
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key",
        )


# =========================================================
# MODELS
# =========================================================

class Signal(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    side: str = Field(..., pattern="^(buy|sell)$")
    qty: float = Field(..., gt=0, allow_inf_nan=False)
    price: Optional[float] = Field(
        default=None, ge=0, allow_inf_nan=False
    )
    note: Optional[str] = Field(default=None, max_length=280)


class TradeResult(BaseModel):
    id: str
    symbol: str
    side: str
    qty: float
    price: float
    paper: bool
    executed_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
    hash: str
    hash_ok: bool
    paper_trading: bool
    frozen_at: str
    time: str


# =========================================================
# IN-MEMORY STORAGE
# WARNING: Data is lost when the process restarts.
# =========================================================

_trades: List[Dict] = []


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    check = CONFIG.self_check()

    logger.info(
        " ".join([
            f"startup version={CONFIG.VERSION}",
            f"paper={PAPER_TRADING}",
            f"hash_expected={check['expected']}",
            f"hash_actual={check['actual']}",
            f"hash_ok={check['match']}",
        ])
    )

    if not check["match"]:
        logger.error(
            "Config hash mismatch. Set "
            f"LIVE_CONFIG_10K_HASH={check['actual']} "
            "in the environment."
        )

    if not PAPER_TRADING and not API_KEY:
        logger.error("LIVE mode without API_KEY; trades blocked.")

    yield

    logger.info("shutdown")


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI Trading Core",
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs" if PAPER_TRADING else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


# =========================================================
# HEALTH / READINESS
# =========================================================

@app.get("/health", response_model=HealthResponse)
def health():
    check = CONFIG.self_check()

    return HealthResponse(
        status="ok",
        version=VERSION,
        hash=check["actual"],
        hash_ok=check["match"],
        paper_trading=PAPER_TRADING,
        frozen_at=FROZEN_AT,
        time=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/ready")
def ready():
    check = CONFIG.self_check()

    if not check["match"]:
        raise HTTPException(
            status_code=503,
            detail="Config hash mismatch",
        )

    if not PAPER_TRADING and not API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Live mode missing API_KEY",
        )

    return {
        "ready": True,
        "time": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================
# TRADING ENDPOINT
# =========================================================

@app.post(
    "/trade",
    response_model=TradeResult,
    dependencies=[
        Depends(rate_limit),
        Depends(require_api_key),
    ],
)
def trade(signal: Signal):
    if not CONFIG.verify():
        raise HTTPException(
            status_code=409,
            detail="Config hash mismatch; trade refused",
        )

    if not PAPER_TRADING:
        raise HTTPException(
            status_code=503,
            detail=(
                "Live trading is disabled in this build. "
                "No broker integration is configured."
            ),
        )

    trade_time = datetime.now(timezone.utc).isoformat()
    trade_id = hashlib.sha256(
        f"{signal.symbol}:{signal.side}:{signal.qty}:"
        f"{time.time_ns()}".encode()
    ).hexdigest()[:12]

    result = TradeResult(
        id=trade_id,
        symbol=signal.symbol.upper(),
        side=signal.side,
        qty=signal.qty,
        price=signal.price if signal.price is not None else 0.0,
        paper=True,
        executed_at=trade_time,
    )

    _trades.append(result.model_dump())

    logger.info(
        f"paper_trade id={result.id} "
        f"symbol={result.symbol} "
        f"side={result.side} qty={result.qty}"
    )

    return result


# =========================================================
# TRADE HISTORY
# =========================================================

@app.get(
    "/trades",
    dependencies=[
        Depends(rate_limit),
        Depends(require_api_key),
    ],
)
def list_trades(limit: int = 50):
    if limit < 1 or limit > 500:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 500",
        )

    return {
        "count": len(_trades),
        "items": _trades[-limit:],
    }


# =========================================================
# CONFIG INFORMATION
# =========================================================

@app.get("/config")
def get_config():
    check = CONFIG.self_check()

    return {
        "version": VERSION,
        "portfolio_base": PORTFOLIO_BASE,
        "frozen_at": FROZEN_AT,
        "hash": check,
        "paper_trading": PAPER_TRADING,
    }


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.exception_handler(HTTPException)
async def http_error_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        f"unhandled {request.method} {request.url.path}",
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# =========================================================
# LOCAL ENTRYPOINT
# =========================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        proxy_headers=True,
    )
