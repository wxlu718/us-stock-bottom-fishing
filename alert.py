import yfinance as yf
import requests
import os
from datetime import datetime

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LAST_ALERT_FILE = "last_alert.txt"   # GitHub automatically persists this file

# Your exact thresholds from the table
THRESHOLDS = {
    "phase1_10y": 4.30,          # 10Y < 4.3%
    "phase1_tlt_up": 6.0,        # TLT >= +6% from recent low
    "phase2_sahm": False,        # placeholder (can be extended later)
    "phase2_ism": 42,
    "phase2_nfp": 100000,
    "phase3_vix": 35,
    "phase3_drawdown": 15.0,     # SPX drawdown >=15%
    "phase3_pe": 18.0,
    "risk_10y_break": 4.60       # risk control: 10Y >4.6%
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def load_last_state():
    try:
        with open(LAST_ALERT_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return 0

def save_last_state(value):
    with open(LAST_ALERT_FILE, "w") as f:
        f.write(str(value))

# ================== FETCH LIVE DATA ==================
def get_data():
    tlt = yf.Ticker("TLT").history(period="5d")["Close"]
    spx = yf.Ticker("^GSPC").history(period="1y")["Close"]
    vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
    tn10 = yf.Ticker("^TNX").history(period="1d")["Close"].iloc[-1] / 100   # convert to decimal

    current_tlt = tlt.iloc[-1]
    tlt_change = (current_tlt - tlt.iloc[0]) / tlt.iloc[0] * 100

    spx_high = spx.max()
    spx_current = spx.iloc[-1]
    drawdown = (spx_current - spx_high) / spx_high * 100 * -1   # positive = drawdown

    # Approximate SPX forward P/E via SPY
    spy_info = yf.Ticker("SPY").info
    fwd_pe = spy_info.get("forwardPE", 20.0)

    return {
        "10y": tn10,
        "tlt_change": tlt_change,
        "vix": vix,
        "drawdown": drawdown,
        "fwd_pe": fwd_pe,
        "tlt_price": current_tlt
    }

# ================== MAIN LOGIC ==================
data = get_data()
now = datetime.now().strftime("%Y-%m-%d %H:%M")

msg = f"📢 <b>Stock Bottom-Fishing Alert {now} (UTC+8)</b>\n"

triggered = False

# Phase 1 (prerequisite)
if data["10y"] < THRESHOLDS["phase1_10y"] and data["tlt_change"] >= THRESHOLDS["phase1_tlt_up"]:
    msg += "✅ <b>Phase 1 TRIGGERED!</b> 10Y < 4.3% + TLT +6% → Start DCA stocks (+20-30%)\n"
    triggered = True

# Phase 3 (sentiment & valuation)
if data["vix"] > THRESHOLDS["phase3_vix"] or data["drawdown"] >= THRESHOLDS["phase3_drawdown"] or data["fwd_pe"] <= THRESHOLDS["phase3_pe"]:
    msg += f"✅ <b>Phase 3 TRIGGERED!</b> VIX {data['vix']:.1f} / Drawdown {data['drawdown']:.1f}% / PE {data['fwd_pe']:.1f} → Go heavy or full position (+30-40%)\n"
    triggered = True

# Risk control
if data["10y"] > THRESHOLDS["risk_10y_break"]:
    msg += "🚨 <b>RISK CONTROL TRIGGERED!</b> 10Y > 4.6% → PAUSE all stock adding!\n"
    triggered = True

# Send only on first trigger (anti-duplicate)
last = load_last_state()
if triggered and (last != 1):
    send_telegram(msg)
    save_last_state(1)
elif not triggered:
    save_last_state(0)   # reset state

print("✅ Check complete", data)
