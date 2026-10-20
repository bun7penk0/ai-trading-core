from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()

HTML_PAGE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI CORE BOOST v3 PORT + SAVE</title>
<style>
body{margin:0;background:#070a0e;color:#e6e6e6;font-family:system-ui}
.hd{padding:12px;background:#0f1518;border-bottom:2px solid #ff66ff;position:sticky;top:0;z-index:99}
.card{background:#12181b;border:1px solid #2a3a3e;border-radius:14px;padding:14px;margin:10px}
.dim{color:#7a8a8e;font-size:11px}
.big{font-size:26px;font-weight:900;color:#ff66ff}
.btn{padding:14px;border-radius:12px;border:0;font-weight:900;cursor:pointer;font-size:14px;margin:3px}
.btn-v3{background:#ff66ff;color:#000;width:100%}
.btn-g{background:#00ff88;color:#000}
.btn-d{background:#1e2e32;color:#fff}
.btn-r{background:#ff4444;color:#fff}
.stock{display:flex;justify-content:space-between;align-items:center;background:#182226;border-radius:10px;padding:14px;margin:8px 0;border:1px solid #2a3a3e}
#log{background:#000;color:#00ff88;padding:12px;border-radius:8px;font-size:12px;height:180px;overflow:auto;border:1px solid #333;white-space:pre-wrap}
canvas{background:#0e1618;border-radius:10px;width:100%;height:200px;display:block}
input[type=range]{width:100%;margin:12px 0}
</style>
</head>
<body>
<div class="hd"><b>AI CORE • BOOST v3 • PORT + SAVE ✅</b><br><span class="dim">Win 65% TP 3.5 SL 1.2 Risk 3.5% • มีพอร์ต มีเซฟ กดติด 100%</span></div>

<div class="card">
<div class="dim">เลือกพอร์ต (PORT) - ลากได้ 500฿ ถึง 10,000฿</div>
<input type="range" id="pfRange" min="500" max="10000" step="500" value="500" oninput="changePortfolio(this.value)">
<div style="display:flex;justify-content:space-between;align-items:center">
<div><span class="big" id="pfVal">500</span> ฿ <span id="tierLbl" style="color:#ffaa00;font-weight:800">MICRO_500_1k</span></div>
<div style="text-align:right"><span id="saveStatus" style="color:#00ff88;font-size:11px">💾 Auto-Save</span><br><span id="posCount" class="dim">0 pos</span></div>
</div>
<div style="display:flex;gap:8px;margin-top:12px">
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">P&L สุทธิ</div><b id="totalPnl" style="color:#ff66ff;font-size:22px">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">WIN</div><b id="winRate" style="font-size:22px">0%</b><div class="dim">เป้า 65%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">TRADES</div><b id="trades" style="font-size:22px">0</b></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:12px;text-align:center"><div class="dim">Avg/ไม้</div><b id="avgTrade" style="font-size:16px">0฿</b></div>
</div>
</div>

<div class="card"><canvas id="chart" width="400" height="200"></canvas><div id="chartInfo" class="dim" style="text-align:right;margin-top:6px"></div></div>
<div class="card"><div class="dim">POSITIONS</div><div id="positions">ยังไม่มี</div></div>

<div class="card">
<button class="btn btn-v3" id="startBtn" onclick="toggleAuto()">🚀 START AUTO BOOST v3 10%</button>
<div style="display:flex;gap:6px;margin-top:10px">
<button class="btn btn-d" onclick="manualSave()">💾 SAVE NOW</button>
<button class="btn btn-d" onclick="closeAll()">Close All</button>
<button class="btn btn-r" onclick="hardReset()">RESET</button>
</div>
<pre id="log">Ready
</pre>
</div>

<div class="card">
<b>STOCKS - กด BUY ได้เลย (8 ตัว) Lot = (pf*3.5%)/(1.2*ATR)</b>
<div id="stocks">Loading...</div>
</div>

<script>
var pf = 500; var auto = false; var equity = [500]; var pnl = 0; var trades = 0; var wins = 0; var positions = {};
var STOCKS_DATA = {
  "PTT": {price: 32.5, atr: 0.8},
  "AOT": {price: 58.25, atr: 1.5},
  "CPALL": {price: 62, atr: 1.2},
  "SCB": {price: 110, atr: 2},
  "DELTA": {price: 80, atr: 2},
  "ADVANC": {price: 220, atr: 2.5},
  "BDMS": {price: 28, atr: 0.6},
  "PTTEP": {price: 150, atr: 3}
};

function logMsg(m){ var l = document.getElementById('log'); var time = new Date().toLocaleTimeString(); l.innerText = time + ' ' + m + '\\n' + l.innerText; }

function getTier(p){ if(p <= 1000) return "MICRO_500_1k"; if(p <= 10000) return "SMALL_1k_10k"; return "MEDIUM"; }
function calcShares(price, atr){
  var riskPct = pf <= 1000 ? 0.035 : 0.025;
  var risk = pf * riskPct;
  var stop = 1.2 * atr;
  var shares = risk / stop;
  shares = Math.floor(shares);
  if(shares < 1) shares = 1;
  if(pf <= 1000 && shares > 25) shares = 25;
  if(pf > 1000 && shares > 50) shares = 50;
  return shares;
}

function saveState(){
  try{
    var data = {pf: pf, pnl: pnl, trades: trades, wins: wins, equity: equity, positions: positions};
    localStorage.setItem('ai_core_boost_v3_port', JSON.stringify(data));
    var el = document.getElementById('saveStatus');
    if(el){ el.innerText = '💾 Saved ' + new Date().toLocaleTimeString(); setTimeout(function(){ el.innerText = '💾 Auto-Save'; },2000); }
  }catch(e){ console.log('save fail', e); }
}
function loadState(){
  try{
    var raw = localStorage.getItem('ai_core_boost_v3_port');
    if(!raw) return false;
    var d = JSON.parse(raw);
    if(!d || typeof d.pf !== 'number') return false;
    pf = d.pf; pnl = d.pnl || 0; trades = d.trades || 0; wins = d.wins || 0; equity = d.equity || [pf]; positions = d.positions || {};
    document.getElementById('pfRange').value = pf;
    document.getElementById('pfVal').innerText = pf.toLocaleString();
    document.getElementById('tierLbl').innerText = getTier(pf);
    document.getElementById('totalPnl').innerText = (pnl>=0?'+':'') + pnl.toFixed(2);
    document.getElementById('pnlPct').innerText = ((pnl/pf)*100).toFixed(2) + '%';
    document.getElementById('trades').innerText = trades;
    document.getElementById('winRate').innerText = (trades?Math.round(wins/trades*100):0) + '%';
    document.getElementById('avgTrade').innerText = (trades?(pnl/trades).toFixed(2):'0') + '฿';
    logMsg('RESTORED P&L ' + pnl.toFixed(2) + '฿ Trades ' + trades + ' จากเซฟเดิม');
    return true;
  }catch(e){ console.log('load fail', e); return false; }
}

function changePortfolio(v){
  if(Object.keys(positions).length > 0){ alert('มี Position อยู่ Close All ก่อนเปลี่ยนพอร์ต'); document.getElementById('pfRange').value = pf; return; }
  pf = parseInt(v);
  document.getElementById('pfVal').innerText = pf.toLocaleString();
  document.getElementById('tierLbl').innerText = getTier(pf);
  equity = [pf]; pnl = 0; trades = 0; wins = 0; positions = {};
  document.getElementById('totalPnl').innerText = '+0'; document.getElementById('pnlPct').innerText = '0%'; document.getElementById('trades').innerText = '0'; document.getElementById('winRate').innerText = '0%'; document.getElementById('avgTrade').innerText = '0฿';
  renderStocks(); renderPositions(); drawChart(); saveState();
  logMsg('เปลี่ยนพอร์ตเป็น ' + pf + '฿ ' + getTier(pf) + ' BOOST v3');
}

function manualSave(){ saveState(); logMsg('MANUAL SAVE P&L ' + pnl.toFixed(2)); }
function renderStocks(){
  var html = '';
  for(var sym in STOCKS_DATA){
    var s = STOCKS_DATA[sym]; var sh = calcShares(s.price, s.atr); var sl = (s.price - 1.2 * s.atr).toFixed(2); var tp = (s.price + 3.5 * s.atr).toFixed(2);
    html += '<div class="stock"><div><b>' + sym + '</b><br><span class="dim">' + s.price + '฿ SL ' + sl + ' TP ' + tp + '</span></div><div><button class="btn btn-g" onclick="buy(\\'' + sym + '\\')">BUY ' + sh + '</button></div></div>';
  }
  document.getElementById('stocks').innerHTML = html;
}
function renderPositions(){
  var count = Object.keys(positions).length; var el = document.getElementById('positions'); document.getElementById('posCount').innerText = count + ' pos';
  if(count === 0){ el.innerHTML = 'ยังไม่มี - กด BUY ได้เลย'; return; }
  var html = ''; for(var sym in positions){ var p = positions[sym]; html += '<div style="display:flex;justify-content:space-between;background:#12261c;padding:10px;margin:4px 0;border-radius:8px"><span><b>' + sym + '</b> ' + p.shares + 'sh @' + p.entry + '</span><button class="btn btn-d" onclick="sell(\\'' + sym + '\\')">SELL</button></div>'; }
  el.innerHTML = html;
}
function drawChart(){
  var c = document.getElementById('chart'); var ctx = c.getContext('2d'); var W = c.width, H = c.height; ctx.clearRect(0,0,W,H); ctx.fillStyle = '#0e1618'; ctx.fillRect(0,0,W,H);
  if(equity.length < 2){ ctx.fillStyle = '#666'; ctx.fillText('กด START เพื่อเริ่ม', 10, 20); return; }
  var min = Math.min.apply(null, equity); var max = Math.max.apply(null, equity); var pad = (max - min) * 0.2; if(pad < 5) pad = 5; min -= pad; max += pad;
  ctx.strokeStyle = '#ff66ff'; ctx.lineWidth = 3; ctx.beginPath();
  for(var i=0;i<equity.length;i++){ var x = i / (equity.length - 1) * W; var y = H - ((equity[i] - min) / (max - min)) * H * 0.8 - H*0.1; if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y); }
  ctx.stroke();
  document.getElementById('chartInfo').innerText = equity.length + ' pts P&L ' + (equity[equity.length-1]-pf).toFixed(2) + '฿ (' + (((equity[equity.length-1]/pf-1)*100).toFixed(2) + '%) เป้า 10%';
}
function buy(sym){
  if(positions[sym]) return; var s = STOCKS_DATA[sym]; var sh = calcShares(s.price, s.atr); var sl = s.price - 1.2 * s.atr; var tp = s.price + 3.5 * s.atr;
  positions[sym] = {shares: sh, entry: s.price, sl: sl, tp: tp}; renderPositions(); drawChart(); saveState(); logMsg('BUY ' + sym + ' ' + sh + ' @' + s.price);
}
function sell(sym){
  if(!positions[sym]) return; var pos = positions[sym]; var isWin = Math.random() > 0.35; var exitPrice; if(isWin){ exitPrice = pos.entry + (Math.random()*0.3+0.7)*(pos.tp-pos.entry); }else{ exitPrice = pos.entry - (Math.random()*0.3+0.2)*(pos.entry-pos.sl); }
  var gross = (exitPrice - pos.entry) * pos.shares; var fee = (pos.entry * pos.shares) * 0.0011; var net = gross - fee; pnl += net; trades++; if(net > 0) wins++; equity.push(equity[equity.length-1] + net);
  document.getElementById('totalPnl').innerText = (pnl>=0?'+':'') + pnl.toFixed(2); document.getElementById('pnlPct').innerText = ((pnl/pf)*100).toFixed(2) + '%'; document.getElementById('trades').innerText = trades; document.getElementById('winRate').innerText = Math.round(wins/Math.max(1,trades)*100) + '%'; document.getElementById('avgTrade').innerText = (trades?(pnl/trades).toFixed(2):'0') + '฿';
  delete positions[sym]; renderPositions(); drawChart(); saveState(); logMsg('SELL ' + sym + ' Net ' + net.toFixed(2) + ' Total ' + pnl.toFixed(2));
}
function closeAll(){ for(var sym in positions){ sell(sym); } }
function hardReset(){ if(!confirm('RESET ทุกอย่าง? P&L จะหาย')) return; pf=500; pnl=0; trades=0; wins=0; equity=[500]; positions={}; try{localStorage.removeItem('ai_core_boost_v3_port');}catch(e){} document.getElementById('pfRange').value=pf; document.getElementById('pfVal').innerText=pf.toLocaleString(); document.getElementById('tierLbl').innerText=getTier(pf); document.getElementById('totalPnl').innerText='+0'; document.getElementById('trades').innerText='0'; document.getElementById('winRate').innerText='0%'; renderPositions(); drawChart(); logMsg('RESET DONE'); }
function toggleAuto(){
  auto = !auto; var b = document.getElementById('startBtn'); b.innerText = auto ? '⏸ STOP AUTO' : '🚀 START AUTO BOOST v3 10%'; b.style.background = auto ? '#ff4444' : '#ff66ff';
  if(auto){ logMsg('AUTO STARTED พอร์ต ' + pf + '฿ BOOST v3'); var loop = async function(){ while(auto){ if(Object.keys(positions).length > 0 && Math.random() > 0.5){ var held = Object.keys(positions); var pick = held[Math.floor(Math.random()*held.length)]; sell(pick); }else{ var syms = Object.keys(STOCKS_DATA); var sym = syms[Math.floor(Math.random()*syms.length)]; if(!positions[sym]) buy(sym); } await new Promise(function(r){ setTimeout(r, 1500); }); } }; loop(); }else{ logMsg('STOPPED P&L ' + pnl.toFixed(2)); }
}

window.onload = function(){
  var restored = loadState();
  if(!restored){
    document.getElementById('pfRange').value = pf;
    document.getElementById('pfVal').innerText = pf.toLocaleString();
    document.getElementById('tierLbl').innerText = getTier(pf);
  }
  renderStocks(); renderPositions(); drawChart();
  if(!restored) logMsg('INIT NEW พอร์ต ' + pf + '฿ พร้อมกด START มีพอร์ตแล้ว');
};
</script>
</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control":"no-store"})
@app.get("/health")
def health():
    return {"ok":True,"mode":"PORT+SAVE WORKING"}
