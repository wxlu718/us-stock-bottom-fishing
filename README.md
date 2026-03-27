# Stock Bottom-Fishing Alert System

**Automated 24/7 Telegram alerts** for Herman Jin’s macro logic (TLT-first + Phase 1–3 + risk control).  
Built with GitHub Actions — zero cost, no PC required, runs forever.

## How It Works
- Checks market data **every 5 minutes** using `yfinance`
- Only sends alert when a new phase/risk condition is **first triggered** (no spam)
- Based on your exact add-position logic (Phase 1 is prerequisite)

## Project Structure


.
├── .github/workflows/alert.yml     # GitHub Actions schedule + environment
├── alert.py                        # Main logic + thresholds
└── README.md                       # ← You are here




## How to Modify Logic in the Future (Super Easy)

### 1. Change thresholds / messages
Open `alert.py` → go to the `THRESHOLDS` section (lines 18–28):

```python
THRESHOLDS = {
    "phase1_10y": 4.30,          # ← change any number here
    "phase1_tlt_up": 6.0,
    "phase3_vix": 35,
    "phase3_drawdown": 15.0,
    "phase3_pe": 18.0,
    "risk_10y_break": 4.60,
    # ... add new ones freely
}
```

### 2. Add new indicators or phasesJust add new keys to THRESHOLDS and add new if blocks in the main logic.

I can give you the exact code snippet anytime — just tell me what you want to add.3. Change check frequencyEdit .github/workflows/alert.yml → change */5 * * * * to:*/15 * * * * → every 15 min
0 */1 * * * → every hour
0 9-16 * * 1-5 → only market hours (Mon–Fri 9am–4pm UTC)

### 3. Add Phase 2 macro data (Sahm, ISM, NFP)Just say the word and I’ll give you the free FRED API version.Quick Commands You Might Need

LaterManual test → Actions tab → “Run workflow”
View alert history → check your Telegram chat
Stop alerts temporarily → comment out the send_telegram calls in alert.py

Project created on: 2026-03-27
Your logic version: Phase 1–3 + 10Y 4.5% top (from original Excel table)

