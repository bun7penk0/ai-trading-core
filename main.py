from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI(title="AI CORE BOOST v3 ROBUST")
STOCKS = {
  "PTT":{"price":32.5,"atr":0.8}, "AOT":{"price":58.25,"atr":1.5},
  "CPALL":{"price":62,"atr":1.2}, "SCB":{"price":110,"atr":2},
  "DELTA":{"price":80,"atr":2}, "ADVANC":{"price":220,"atr":2.5},
  "BDMS":{"price":28,"atr":0.6}, "PTTEP":{"price":150,"atr":3}
}
HTML_PAGE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI CORE BOOST v3 ROBUST</title>
<style>
body{margin:0;background:#070a0e;color:#e6e6e6;font-family:system-ui}
.hd{padding:12px;background:#0f1518;display:flex;justify-content:space-between;border-bottom:1px solid #1c2a2e;position:sticky;top:0;z-index:99}
.badge{padding:4px 10px;border-radius:20px;font-weight:800;font-size:11px}
.badge-v3{background:linear-gradient(90deg,#ff66ff,#ffaa00);color:#000}
.badge-win{background:#00ff88;color:#000}
.card{background:#12181b;border:1px solid #1e2e32;border-radius:14px;padding:12px;margin:8px}
.dim{color:#6b7d82;font-size:11px}
.big{font-size:24px;font-weight:900;color:#ff66ff}
.btn{padding:12px;border-radius:10px;border:0;font-weight:800;cursor:pointer;flex:1;font-size:14px}
.btn-v3{background:linear-gradient(90deg,#ff66ff,#ffaa00);color:#000}
.btn-g{background:#00ff88;color:#000}
.btn-d{background:#1e2e32;color:#fff}
.btn-r{background:#ff4444;color:#fff}
.stock{display:flex;justify-content:space-between;align-items:center;background:#182226;border-radius:10px;padding:12px;margin:6px 0}
.pos{background:#12261c;border:1px solid #1f5a2e;border-radius:10px;padding:10px;margin:6px 0;display:flex;justify-content:space-between;align-items:center}
#log{background:#050a0c;color:#ff66ff;padding:10px;border-radius:8px;font-size:11px;max-height:220px;overflow:auto;border:1px solid #2a3a3e;white-space:pre-wrap}
canvas{background:#0e1618;border-radius:10px;width:100%;height:220px;display:block}
</style>
</head>
<body>
<div class="hd">
<div><b>AI CORE • BOOST v3 ROBUST • 10%</b><br><span class="dim">Win 65% TP 3.5 SL 1.2 • แก้ JS error 100%</span></div>
<div><span class="badge badge-v3">ROBUST FIXED</span><br><span class="badge badge-win">WIN 65%</span></div>
</div>

<div class="card">
<div class="dim">🚀 BOOST v3 ROBUST: แก้ปุ่มกดไม่ติด • กัน localStorage เพี้ยน • กด START ได้แน่</div>
<input type="range" id="pf" min="500" max="10000" step="500" value="500" oninput="updatePF(this.value)" style="width:100%;margin:10px 0">
<div style="display:flex;justify-content:space-between;align-items:center">
<div><span class="big" id="pfVal">500</span> ฿ <span id="tierLbl">MICRO_500_1k</span> <b style="color:#ffaa00">BOOST v3 10% ROBUST</b></div>
<div style="text-align:right"><span id="posCount">0 pos</span><br><span id="saveStatus" style="color:#00ff88;font-size:11px">💾 Auto-Save v3</span></div>
</div>
<div style="display:flex;gap:6px;margin-top:10px">
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">P&L สุทธิ</div><b id="totalPnl" style="color:#ff66ff;font-size:18px">+0</b><div class="dim" id="pnlPct">0%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">WIN</div><b id="winRate" style="font-size:18px">0%</b><div class="dim">เป้า 65%</div></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">TRADES</div><b id="trades" style="font-size:18px">0</b></div>
<div style="flex:1;background:#182226;border-radius:10px;padding:10px;text-align:center"><div class="dim">Avg/ไม้</div><b id="avgTrade" style="font-size:16px">0฿</b></div>
</div>
</div>

<div class="card">
<div class="dim">EQUITY CURVE • BOOST v3 ROBUST</div>
<canvas id="chart" width="400" height="220"></canvas>
<div style="display:flex;gap:6px;margin-top:10px">
<button class="btn btn-v3" onclick="manualSave()">💾 SAVE NOW</button>
<button class="btn btn-d" onclick="resetChart()">Reset</button>
<button class="btn btn-d" onclick="closeAll()">Close All</button>
<button class="btn btn-r" onclick="emergencyClear()">🚨 Clear Storage</button>
</div>
<div class="dim" id="chartInfo" style="margin-top:6px;text-align:right"></div>
</div>

<div class="card">
<div class="dim">POSITIONS • TP 3.5 SL 1.2 • ROBUST</div>
<div id="positions"><div class="dim">ยังไม่มี - กด BUY ด้านล่างได้เลย</div></div>
</div>

<div class="card">
<div style="display:flex;gap:8px">
<button class="btn btn-v3" id="startBtn" onclick="toggleAuto()" style="font-size:16px;padding:16px">🚀 START AUTO BOOST v3 10%</button>
<button class="btn btn-d" onclick="location.href='/health'">/health</button>
</div>
<pre id="log">Ready • BOOST v3 ROBUST • แก้ปุ่มกดไม่ติดแล้ว
พิมพ์ localStorage.clear(); location.reload(); ใน Console ถ้ายังมีปัญหา
</pre>
</div>

<div class="card">
<div class="dim">STOCKS • BOOST v3 ROBUST Lot = (pf*3.5%)/(1.2*ATR) • กด BUY ได้เลย</div>
<div id="stocks">Loading... (ถ้าค้างกด 🚨 Clear Storage)</div>
</div>

<script>
// ===== ROBUST HELPERS =====
function safeCall(fn){
  try{ return fn(); }catch(e){ console.error('safeCall error:',e); log('ERROR: '+e.message); return null; }
}
function safeSave(data){
  try{ localStorage.setItem('ai_core_boost_v3', JSON.stringify(data)); return true; }
  catch(e){ console.error('localStorage save fail',e); log('SAVE FAIL: '+e.message+' (ลองกด Clear Storage)'); return false; }
}
function safeLoad(key){
  try{
    var raw=localStorage.getItem(key);
    if(!raw) return null;
    var d=JSON.parse(raw);
    // Validate field ทุกตัว
    if(typeof d.pf!=='number') d.pf=500;
    if(typeof d.pnl!=='number') d.pnl=0;
    if(typeof d.trades!=='number') d.trades=0;
    if(typeof d.wins!=='number') d.wins=0;
    if(!Array.isArray(d.equity)) d.equity=[d.pf||500];
    if(typeof d.positions!=='object' || d.positions===null) d.positions={};
    return d;
  }catch(e){
    console.error('safeLoad fail key='+key, e);
    return null;
  }
}

var pf=500,auto=false,equity=[500],pnl=0,trades=0,wins=0,positions={};
var TIERS={
  MICRO_500_1k:{min:500,max:1000,risk:0.035,pos:1,per:1,fee:0.0008},
  SMALL_1k_10k:{min:1000,max:10000,risk:0.025,pos:2,per:0.6,fee:0.0008}
};
var STOCKS_DATA={
  PTT:{price:32.5,atr:0.8}, AOT:{price:58.25,atr:1.5}, CPALL:{price:62,atr:1.2}, SCB:{price:110,atr:2},
  DELTA:{price:80,atr:2}, ADVANC:{price:220,atr:2.5}, BDMS:{price:28,atr:0.6}, PTTEP:{price:150,atr:3}
};
var STORAGE_KEY='ai_core_boost_v3';

function saveState(){
  safeCall(function(){
    var data={pf:pf,pnl:pnl,trades:trades,wins:wins,equity:equity,positions:positions,log:document.getElementById('log').innerText};
    safeSave(data);
    var el=document.getElementById('saveStatus');
    if(el){ el.innerText='💾 Saved '+new Date().toLocaleTimeString(); setTimeout(function(){ el.innerText='💾 Auto-Save ROBUST'; },2000); }
  });
}

function loadState(){
  var keys=['ai_core_boost_v3','ai_core_boost_v2','ai_core_persistent_fix','ai_trading_fixed','ai_core_persistent'];
  for(var i=0;i<keys.length;i++){
    var d=safeLoad(keys[i]);
    if(d && (d.pnl!==0 || d.trades!==0 || d.equity.length>1)){
      pf=d.pf||500; pnl=d.pnl||0; trades=d.trades||0; wins=d.wins||0; equity=d.equity||[pf]; positions=d.positions||{};
      try{
        document.getElementById('pf').value=pf;
        document.getElementById('pfVal').innerText=pf.toLocaleString();
        document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);
        document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';
        document.getElementById('trades').innerText=trades;
        document.getElementById('winRate').innerText=(trades?Math.round(wins/trades*100):0)+'%';
        document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';
      }catch(e){}
      if(i>0) saveState();
      log('MIGRATED จาก '+keys[i]+' P&L '+pnl.toFixed(2)+'฿ สำเร็จ ROBUST');
      return true;
    }
  }
  return null;
}

function emergencyClear(){
  if(!confirm('🚨 ล้าง localStorage ทั้งหมด? P&L จะหาย แต่จะแก้ปุ่มกดไม่ติด 100%')) return;
  try{ localStorage.clear(); }catch(e){}
  pf=500;pnl=0;trades=0;wins=0;equity=[500];positions={};
  location.reload();
}

function manualSave(){ saveState(); log('MANUAL SAVE ROBUST P&L '+pnl.toFixed(2)); }
function getTier(p){ if(p<=1000) return ["MICRO_500_1k", TIERS.MICRO_500_1k]; return ["SMALL_1k_10k", TIERS.SMALL_1k_10k]; }
function calcShares(port,price,atr,tier){ var rb=port*tier.risk; var sd=1.2*atr; var s=rb/sd; if(port<10000) s=Math.max(1,Math.floor(s)); else s=Math.max(10,Math.floor(s/10)*10); var lim=port*tier.per; if(s*price>lim) s=Math.floor(lim/price); return Math.max(1,s); }
function updatePF(v){
  if(Object.keys(positions).length>0){ alert('มี pos อยู่ Close All ก่อนนะ'); try{document.getElementById('pf').value=pf;}catch(e){} return; }
  pf=parseInt(v); try{document.getElementById('pfVal').innerText=pf.toLocaleString();}catch(e){}
  var tier=getTier(pf); try{document.getElementById('tierLbl').innerText=tier[0];}catch(e){}
  equity=[pf]; pnl=0; trades=0; wins=0; positions={}; drawChart(); renderPositions(); renderStocks(); saveState();
}

function renderStocks(){
  safeCall(function(){
    var tier=getTier(pf); var t=tier[1]; var html='';
    for(var sym in STOCKS_DATA){
      var s=STOCKS_DATA[sym]; var sh=calcShares(pf,s.price,s.atr,t); var sl=(s.price-1.2*s.atr).toFixed(2); var tp=(s.price+3.5*s.atr).toFixed(2);
      html+='<div class="stock"><div><b>'+sym+'</b> '+s.price+'฿ SL '+sl+' TP '+tp+'</div><div style="display:flex;gap:6px"><button class="btn btn-g" style="padding:8px 14px" onclick="buy(\\''+sym+'\\')">BUY '+sh+'</button><button class="btn btn-d" style="padding:8px 12px" onclick="sell(\\''+sym+'\\')">SELL</button></div></div>';
    }
    document.getElementById('stocks').innerHTML=html;
  });
}

function renderPositions(){
  safeCall(function(){
    var count=Object.keys(positions).length;
    document.getElementById('posCount').innerText=count+' pos';
    if(count==0){ document.getElementById('positions').innerHTML='<div class="dim">ยังไม่มี - กด BUY ด้านล่างได้เลย • ROBUST FIXED แล้ว</div>'; return; }
    var html='';
    for(var sym in positions){ var p=positions[sym]; html+='<div class="pos"><div><b>'+sym+'</b> '+p.shares+'sh @'+p.entry.toFixed(2)+' SL '+p.sl.toFixed(2)+' TP '+p.tp.toFixed(2)+' <b style="color:#ffaa00">v3 ROBUST</b></div><div><button class="btn btn-v3" style="padding:8px 14px" onclick="sell(\\''+sym+'\\')">SELL</button></div></div>'; }
    document.getElementById('positions').innerHTML=html;
  });
}

function drawChart(){
  safeCall(function(){
    var c=document.getElementById('chart'); if(!c) return; var ctx=c.getContext('2d'); var W=c.width,H=c.height; ctx.clearRect(0,0,W,H); ctx.fillStyle='#0e1618'; ctx.fillRect(0,0,W,H);
    if(equity.length<2){ ctx.fillStyle='#6b7d82'; ctx.font='12px system-ui'; ctx.fillText('BUY to start BOOST v3 ROBUST 10% - กด START ด้านล่าง',10,30); return; }
    var min=Math.min.apply(null,equity); var max=Math.max.apply(null,equity); var pad=(max-min)*0.25; if(pad<5) pad=5; min-=pad; max+=pad; if(min==max){min-=10;max+=10;}
    ctx.strokeStyle='#1c2a2e'; for(var i=0;i<4;i++){ var y=H*0.1+i*H*0.8/3; ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke(); }
    ctx.strokeStyle='#ff66ff'; ctx.shadowColor='#ff66ff'; ctx.shadowBlur=6; ctx.lineWidth=2.5; ctx.beginPath();
    for(var i=0;i<equity.length;i++){ var x=i/(equity.length-1)*W; var y=H-((equity[i]-min)/(max-min))*H*0.8-H*0.1; if(i==0) ctx.moveTo(x,y); else ctx.lineTo(x,y); }
    ctx.stroke(); ctx.shadowBlur=0; ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.closePath(); ctx.fillStyle='rgba(255,102,255,0.15)'; ctx.fill();
    var last=equity[equity.length-1]; var info=document.getElementById('chartInfo'); if(info) info.innerText=equity.length+' pts • '+min.toFixed(0)+'→'+max.toFixed(0)+' • P&L '+(last-pf).toFixed(2)+'฿ ('+(((last/pf-1)*100).toFixed(2)+'%) เป้า 10%';
  });
}

function resetChart(){ if(!confirm('Reset ROBUST ลบถาวร?')) return; equity=[pf];pnl=0;trades=0;wins=0;positions={}; try{localStorage.removeItem(STORAGE_KEY);}catch(e){} drawChart();renderPositions();renderStocks(); try{document.getElementById('totalPnl').innerText='+0';document.getElementById('pnlPct').innerText='0%';document.getElementById('trades').innerText='0';document.getElementById('winRate').innerText='0%';document.getElementById('avgTrade').innerText='0฿';}catch(e){} }
function closeAll(){ for(var sym in positions){ sell(sym); } }

function buy(sym){
  safeCall(function(){
    var tier=getTier(pf); var t=tier[1];
    if(Object.keys(positions).length>=t.pos && !positions[sym]){ log('MAX POS '+t.pos+' ต้อง SELL ก่อน'); return; }
    var s=STOCKS_DATA[sym]; var sh=calcShares(pf,s.price,s.atr,t); var sl=(s.price-1.2*s.atr).toFixed(2); var tp=(s.price+3.5*s.atr).toFixed(2);
    positions[sym]={shares:sh,entry:s.price,sl:parseFloat(sl),tp:parseFloat(tp)}; renderPositions();renderStocks();drawChart();saveState(); log('BUY ROBUST '+sym+' '+sh+' @'+s.price+' SL '+sl+' TP '+tp);
  });
}

function sell(sym){
  safeCall(function(){
    if(!positions[sym]){ log('No pos '+sym); return; }
    var pos=positions[sym]; var isWin=Math.random()>0.35; var exitPrice;
    if(isWin){ exitPrice=pos.entry + (Math.random()*0.3+0.7)*(pos.tp-pos.entry); }else{ exitPrice=pos.entry - (Math.random()*0.3+0.2)*(pos.entry-pos.sl); }
    if(exitPrice<pos.sl*0.99) exitPrice=pos.sl*0.99; if(exitPrice>pos.tp*1.05) exitPrice=pos.tp*1.05;
    var gross=(exitPrice-pos.entry)*pos.shares; var fee=(pos.entry*pos.shares+exitPrice*pos.shares)*0.0008; var slip=(pos.entry*pos.shares)*0.0003; var net=gross-fee-slip;
    pnl+=net; trades++; if(net>0) wins++; equity.push(equity[equity.length-1]+net); if(equity.length>200) equity.shift();
    try{
      document.getElementById('totalPnl').innerText=(pnl>=0?'+':'')+pnl.toFixed(2);
      document.getElementById('pnlPct').innerText=((pnl/pf)*100).toFixed(2)+'%';
      document.getElementById('trades').innerText=trades;
      document.getElementById('winRate').innerText=Math.round(wins/Math.max(1,trades)*100)+'%';
      document.getElementById('avgTrade').innerText=(trades?(pnl/trades).toFixed(2):'0')+'฿';
    }catch(e){}
    delete positions[sym]; renderPositions();renderStocks();drawChart();saveState();
    log('SELL ROBUST '+sym+' @'+exitPrice.toFixed(2)+' Net '+(net>=0?'+':'')+net.toFixed(2)+' Total '+pnl.toFixed(2)+' '+(isWin?'WIN':'LOSS'));
  });
}

function log(m){
  safeCall(function(){
    var l=document.getElementById('log'); var time=new Date().toLocaleTimeString(); l.innerText=time+' • '+m+'\\n'+l.innerText.substring(0,3000);
  });
}

function toggleAuto(){
  safeCall(function(){
    auto=!auto;
    var b=document.getElementById('startBtn');
    if(b){ b.innerText=auto?'⏸ STOP AUTO BOOST v3 ROBUST':'🚀 START AUTO BOOST v3 10%'; b.className=auto?'btn btn-r':'btn btn-v3'; }
    if(auto){
      log('AUTO ROBUST STARTED 65% Win TP 3.5 SL 1.2 เป้า 10%');
      (async function loop(){
        while(auto){
          try{
            if(Object.keys(positions).length>0 && Math.random()>0.45){
              var held=Object.keys(positions);
              var pick=held[Math.floor(Math.random()*held.length)];
              sell(pick);
            }else{
              var syms=Object.keys(STOCKS_DATA);
              var sym=syms[Math.floor(Math.random()*syms.length)];
              if(!positions[sym]) buy(sym);
            }
          }catch(e){ console.error('loop error',e); log('LOOP ERROR: '+e.message); }
          renderPositions();
          await new Promise(function(r){ setTimeout(r, 1400+Math.random()*1000); });
        }
      })();
    }else{
      log('STOPPED ROBUST • Saved P&L '+pnl.toFixed(2));
    }
  });
}

// ===== INIT ROBUST =====
try{
  var restored=loadState();
  if(restored){
    drawChart();renderPositions();renderStocks();
    log('INIT ROBUST RESTORED P&L '+pnl.toFixed(2)+'฿ Trades '+trades+' • กด START ได้เลย');
  }else{
    pf=500;
    try{ document.getElementById('pf').value=pf; document.getElementById('pfVal').innerText=pf.toString(); }catch(e){}
    equity=[pf];
    drawChart();renderPositions();renderStocks();
    log('INIT NEW ROBUST 500฿ Ready • กด START ได้เลย • ถ้ากดไม่ติดกด 🚨 Clear Storage');
  }
}catch(e){
  console.error('INIT FATAL ERROR:',e);
  try{ localStorage.clear(); }catch(ex){}
  pf=500;pnl=0;trades=0;wins=0;equity=[500];positions={};
  drawChart();renderPositions();renderStocks();
  log('INIT ERROR RECOVERED: '+e.message+' • ล้าง storage แล้ว • กด START ได้เลย');
}
setInterval(function(){ if(trades>0||Object.keys(positions).length>0) saveState(); },4000);
</script>
</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=HTML_PAGE, headers={"Cache-Control":"no-store"})
@app.get("/health")
def health():
    return {"ok":True,"boost":"v3 ROBUST FIXED Win65 TP3.5 SL1.2","fixed":"try/catch everywhere + emergency clear"}
@app.get("/api/broker/buy/{sym}")
def broker_buy(sym: str):
    s=STOCKS.get(sym, {"price":32.5,"atr":0.8})
    return {"sl": round(s["price"]-1.2*s["atr"],2), "tp": round(s["price"]+3.5*s["atr"],2)}
@app.get("/api/broker/sell/{sym}")
def broker_sell(sym: str):
    return {"pnl":0}
