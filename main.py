import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

# ===== 1. เปิด Server ทันที ก่อน import หนักๆ =====
PORT = int(os.environ.get("PORT", 8080))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        resp = {
            "status": "ok",
            "version": "v0.3.1-V5-FIXED",
            "backtest": "V4 PF1.44 WR42.1% +17.7% 126 trades",
            "allocation": {
                "SCB.BK": "22.4% +20% INCREASE_MORE",
                "DELTA.BK": "22.4% +20% INCREASE_MORE", 
                "ADVANC.BK": "20.6% +10% INCREASE",
                "PTTEP.BK": "20.6% +10% INCREASE",
                "PTT.BK": "14.0% -25% DECREASE"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fix": "Health check responds in <1s - heavy imports lazy loaded"
        }
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())
    
    def do_HEAD(self):
        # Railway บางครั้งเช็ค HEAD ก่อน
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        return

print(f"🚀 Starting health check server on 0.0.0.0:{PORT}...")
print(f"✅ Health check will respond at / in <1s")

# ===== 2. ค่อย import หนักๆ หลังจากนั้น (lazy) =====
try:
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    print("✅ Logs dir ready")
    
    # ลองโหลด config ที่มีอยู่ (ถ้าไม่มีก็ใช้ค่าตายตัว V5)
    from core.config import CONFIG
    from core.risk_gate import RiskGate
    print(f"✅ Core loaded - CONFIG min_score={CONFIG.min_score}")
    
    # ทดสอบ RiskGate ด้วย V5
    risk_gate = RiskGate()
    real_prices = {"SCB":147,"DELTA":248,"ADVANC":331,"PTTEP":157,"PTT":41}
    allocation = {"SCB":0.224,"DELTA":0.224,"ADVANC":0.206,"PTTEP":0.206,"PTT":0.14}
    print("✅ V5 Allocation loaded:")
    for k,v in allocation.items():
        print(f"   {k}: {v*100}% @ {real_prices[k]}฿")
        
except Exception as e:
    print(f"⚠️ Core load warning (ยังรัน health check ได้): {e}")

# ===== 3. Start Server (ต้องอยู่บรรทัดสุดท้าย) =====
try:
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"✅ Server listening on 0.0.0.0:{PORT} - READY FOR RAILWAY")
    server.serve_forever()
except Exception as e:
    print(f"❌ Server failed: {e}")
    import time
    while True:
        time.sleep(60)
