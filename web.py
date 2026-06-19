from flask import Flask, jsonify, render_template_string
import time

app   = Flask(__name__)
START = time.time()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPEED X TempMail Bot — Status</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07070f;--surface:#0f0f1a;--card:#13131f;
  --border:#1c1c2e;--border2:#252540;
  --accent:#7c3aed;--accent2:#06b6d4;--accent3:#f59e0b;
  --green:#22c55e;--red:#ef4444;
  --text:#e2e8f0;--muted:#64748b;--dimmed:#94a3b8;
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;
     display:flex;flex-direction:column;align-items:center;padding:40px 20px}

/* ── noise grain overlay ── */
body::before{content:'';position:fixed;inset:0;opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  pointer-events:none;z-index:0}

.wrap{max-width:560px;width:100%;position:relative;z-index:1}

/* ── header ── */
.header{text-align:center;margin-bottom:40px}
.bolt{font-size:56px;display:block;margin-bottom:12px;
      filter:drop-shadow(0 0 32px #7c3aed99)}
.brand{font-size:30px;font-weight:900;letter-spacing:-1px;
       background:linear-gradient(135deg,#a78bfa,#06b6d4);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.tagline{color:var(--muted);font-size:13px;margin-top:6px;letter-spacing:.5px;text-transform:uppercase}

/* ── card ── */
.card{background:var(--card);border:1px solid var(--border);border-radius:20px;
      padding:28px;margin-bottom:16px;overflow:hidden;position:relative}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,var(--accent),var(--accent2),var(--accent3))}

.card-title{font-size:11px;font-weight:600;letter-spacing:1.5px;
            text-transform:uppercase;color:var(--muted);margin-bottom:20px}

/* ── rows ── */
.row{display:flex;align-items:center;justify-content:space-between;
     padding:14px 0;border-bottom:1px solid var(--border)}
.row:last-child{border-bottom:none;padding-bottom:0}
.row-label{display:flex;align-items:center;gap:10px;font-size:14px;color:var(--dimmed)}
.row-icon{font-size:17px;width:24px;text-align:center}

/* ── badges ── */
.badge{display:inline-flex;align-items:center;gap:6px;padding:5px 13px;
       border-radius:999px;font-size:12px;font-weight:600;letter-spacing:.3px}
.badge-online {background:#22c55e18;color:var(--green);border:1px solid #22c55e35}
.badge-pending{background:#f59e0b18;color:var(--accent3);border:1px solid #f59e0b35}

.dot{width:7px;height:7px;border-radius:50%;background:var(--green);
     animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 #22c55e66}
                 50%{opacity:.7;box-shadow:0 0 0 6px #22c55e00}}

/* ── uptime mono ── */
#uptime{font-family:'JetBrains Mono',monospace;font-size:14px;
        font-weight:600;color:var(--accent2)}

/* ── info grid ── */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.info-box{background:var(--card);border:1px solid var(--border);border-radius:16px;
          padding:20px;text-align:center}
.info-val{font-size:26px;font-weight:900;margin-bottom:4px;
          background:linear-gradient(135deg,#a78bfa,#06b6d4);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.info-lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}

/* ── channel button ── */
.btn{display:block;text-align:center;text-decoration:none;font-weight:700;
     font-size:14px;letter-spacing:.3px;padding:16px;border-radius:14px;
     transition:opacity .2s,transform .15s;margin-bottom:12px;color:#fff;
     background:linear-gradient(135deg,#7c3aed,#06b6d4)}
.btn:hover{opacity:.88;transform:translateY(-1px)}

/* ── api endpoint ── */
.endpoint{background:var(--card);border:1px solid var(--border);border-radius:14px;
          padding:16px 20px;display:flex;align-items:center;gap:12px;margin-bottom:16px}
.method{background:#06b6d418;color:var(--accent2);border:1px solid #06b6d435;
        padding:3px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;
        font-size:11px;font-weight:600;white-space:nowrap}
.path{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--dimmed)}

/* ── footer ── */
.footer{text-align:center;color:var(--muted);font-size:12px;margin-top:24px;
        letter-spacing:.3px;line-height:2}
</style>
</head>
<body>
<div class="wrap">

  <!-- Header -->
  <div class="header">
    <span class="bolt">⚡</span>
    <div class="brand">SPEED X TempMail Bot</div>
    <div class="tagline">Telegram Bot · Status Dashboard</div>
  </div>

  <!-- Stats grid -->
  <div class="grid">
    <div class="info-box">
      <div class="info-val" id="uptime-min">—</div>
      <div class="info-lbl">Uptime (min)</div>
    </div>
    <div class="info-box">
      <div class="info-val">✓</div>
      <div class="info-lbl">All Systems</div>
    </div>
  </div>

  <!-- Status card -->
  <div class="card">
    <div class="card-title">System Status</div>

    <div class="row">
      <div class="row-label"><span class="row-icon">🤖</span> Telegram Bot</div>
      <span class="badge badge-online"><span class="dot"></span> ONLINE</span>
    </div>
    <div class="row">
      <div class="row-label"><span class="row-icon">📧</span> TempMail API</div>
      <span class="badge badge-online"><span class="dot"></span> mail.tm</span>
    </div>
    <div class="row">
      <div class="row-label"><span class="row-icon">🌐</span> Web Server</div>
      <span class="badge badge-online"><span class="dot"></span> RUNNING</span>
    </div>
    <div class="row">
      <div class="row-label"><span class="row-icon">⏱️</span> Uptime</div>
      <span id="uptime" style="color:var(--accent2)">—</span>
    </div>
  </div>

  <!-- Health endpoint -->
  <div class="endpoint">
    <span class="method">GET</span>
    <span class="path">/health</span>
    <span style="margin-left:auto;font-size:12px;color:var(--muted)">JSON status endpoint</span>
  </div>

  <!-- Channel CTA -->
  <a class="btn" href="https://t.me/SPEED_X_OFFICIAL1" target="_blank">
    📢 &nbsp; Join SPEED X Official Channel
  </a>

  <div class="footer">
    Powered by SPEED X &nbsp;·&nbsp; mail.tm API &nbsp;·&nbsp; python-telegram-bot<br>
    <a href="https://t.me/SPEED_X_OFFICIAL1" style="color:var(--accent);text-decoration:none">
      t.me/SPEED_X_OFFICIAL1
    </a>
  </div>
</div>

<script>
const serverStart = {{ start_time }};
function fmt(sec) {
  const d = Math.floor(sec/86400), h = Math.floor(sec%86400/3600),
        m = Math.floor(sec%3600/60), s = Math.floor(sec%60);
  if(d>0) return `${d}d ${h}h ${m}m ${s}s`;
  if(h>0) return `${h}h ${m}m ${s}s`;
  return `${m}m ${s}s`;
}
function tick(){
  const up = Math.floor(Date.now()/1000 - serverStart);
  document.getElementById('uptime').textContent = fmt(up);
  document.getElementById('uptime-min').textContent = Math.floor(up/60);
}
tick(); setInterval(tick, 1000);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML, start_time=int(START))

@app.route("/health")
def health():
    return jsonify({
        "status":         "online",
        "bot":            "SPEED X TempMail Bot",
        "uptime_seconds": int(time.time() - START),
        "mail_api":       "mail.tm",
        "channel":        "https://t.me/SPEED_X_OFFICIAL1"
    })

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
