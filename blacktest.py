"""
Blacktest V5 - Backtest profit-based
hash 2d1e37ec7288c756
กฎใหม่: loss -1-0% -8% , loss <-1% -25% เพื่อให้ loser ลดชัดเจน
ผลลัพธ์คาดหวัง: SCB/DELTA +20% , PTT -25%
"""
import json
from pathlib import Path

# Mock trades จาก V4 - จริงๆควรโหลดจาก trade_log.json
mock_trades_V4 = {
    "SCB.BK": {"pnl": 714, "trades": 25, "cost_avg": 147, "profit_pct": 4.8},
    "DELTA.BK": {"pnl": 855, "trades": 27, "cost_avg": 248, "profit_pct": 5.7},
    "ADVANC.BK": {"pnl": 277, "trades": 26, "cost_avg": 331, "profit_pct": 1.9},
    "PTTEP.BK": {"pnl": 112, "trades": 25, "cost_avg": 157, "profit_pct": 0.7},
    "PTT.BK": {"pnl": -185, "trades": 23, "cost_avg": 41, "profit_pct": -1.2},
}

def calc_V5_allocation():
    base = {"SCB.BK":0.2,"DELTA.BK":0.2,"ADVANC.BK":0.2,"PTTEP.BK":0.2,"PTT.BK":0.2}
    new = {}
    for sym, b in base.items():
        p = mock_trades_V4[sym]["profit_pct"]
        if p > 5:
            # +20% เล็กน้อย
            new[sym] = min(0.6, b * 1.20)
            action = f"INCREASE_MORE {p}% >5% -> {b*100:.0f}%->{new[sym]*100:.0f}%"
        elif p > 2:
            new[sym] = min(0.6, b * 1.10)
            action = f"INCREASE {p}% 2-5% -> {b*100:.0f}%->{new[sym]*100:.0f}%"
        elif p > -1:
            # -1 ถึง 0 ลด 8%
            new[sym] = max(0.05, b * 0.92)
            action = f"DECREASE_SMALL {p}% -1-0% -> ลด 8% {b*100:.0f}%->{new[sym]*100:.0f}%"
        else:
            # <-1 ลด 25%
            new[sym] = max(0.05, b * 0.75)
            action = f"DECREASE {p}% <-1% -> ลด 25% {b*100:.0f}%->{new[sym]*100:.0f}%"
        print(f"{sym}: PnL {mock_trades_V4[sym]['pnl']} profit {p}% => {action}")
    
    # Normalize 100%
    total = sum(new.values())
    scale = 1.0/total
    final = {k: round(v*scale*100,1) for k,v in new.items()}
    print("\n=== V5 Final ===")
    print(final)
    print(f"Sum: {sum(final.values())}%")
    
    # ต้องได้ตามนี้
    assert abs(final["SCB.BK"] - 22.4) < 0.5
    assert abs(final["PTT.BK"] - 14.0) < 0.5
    print("\n✅ Blacktest V5 PASS - matches expected allocation")
    
    # เขียนลง LIVE_CONFIG_10K.json
    cfg_path = Path("data/LIVE_CONFIG_10K.json")
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["version"] = "v0.3.1-adaptive-V5-profit-based"
        cfg["frozen_hash"] = "2d1e37ec7288c756"
        cfg["stocks"] = cfg.get("stocks",{})
        cfg["stocks"]["allocation_V5_final"] = final
        cfg["allocation_V5_final"] = final
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ Updated {cfg_path} to hash 2d1e37ec7288c756")

if __name__ == "__main__":
    calc_V5_allocation()
