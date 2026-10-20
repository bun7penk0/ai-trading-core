import uuid
from dataclasses import dataclass, field

@dataclass
class Consent:
    consent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    shares: int = 0
    price: float = 0.0

class RiskGate:
    def __init__(self, max_risk_pct: float = 0.02, atr_mult: float = 2.0):
        self.max_risk_pct = max_risk_pct
        self.atr_mult = atr_mult

    def calc_position_size(self, price: float, atr: float, currency: str = "THB"):
        if price <= 0 or atr <= 0:
            return 0, "invalid price/atr"
        risk_budget = 10000 * self.max_risk_pct
        stop_dist = self.atr_mult * atr
        shares = int(risk_budget // stop_dist) if stop_dist > 0 else 0
        return shares, f"risk_budget={risk_budget:.0f} stop_dist={stop_dist:.2f}"

    def can_enter(self, symbol, shares, price, atr, currency, date_str):
        checks = []
        if shares <= 0: checks.append("shares<=0")
        if price <= 0: checks.append("price<=0")
        if checks: return None, checks
        return Consent(symbol=symbol, shares=shares, price=price), checks
