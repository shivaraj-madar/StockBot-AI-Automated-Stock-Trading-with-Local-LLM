# 📈 StockBot AI — Automated Stock Trading with Local LLM

An AI agentic trading bot using **Local LLM (TinyLlama)** + **Vector Database (ChromaDB)** + **Real-Time Market Data**.

---

## Project Files (just 4!)

| File | What it does |
|------|-------------|
| `config.py` | All settings — stocks, risk rules, LLM model |
| `bot.py` | The brain — fetch, store, search, decide, trade |
| `dashboard.py` | The UI — press ▶ Run to open in browser |
| `requirements.txt` | Python packages needed |

---

## How It Works — 5 Steps

```
1. FETCH   →  Download real stock price (Yahoo Finance)
2. STORE   →  Save snapshot text into ChromaDB (vector DB)
3. SEARCH  →  Find similar past snapshots from ChromaDB
4. DECIDE  →  Ask local LLM (TinyLlama-1.1B): BUY / SELL / HOLD?
5. TRADE   →  Update paper portfolio
```

---

## Setup (one time)

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. First run auto-downloads TinyLlama (~2.2GB) — no login needed!

# 3. Press F5 in VS Code  (or run below)
streamlit run dashboard.py
```

Then open **http://localhost:8501** in your browser.

---

## What to tell instructor when submitting

| Item | Details |
|---|---|
| **Project Name** | StockBot AI |
| **Subtitle** | Automated Stock Trading with Local LLM |
| **Category** | Finance / AI Agentic System |
| **LLM Used** | TinyLlama-1.1B (runs 100% locally) |
| **Vector DB** | ChromaDB |
| **GitHub** | `https://github.com/YOUR_USERNAME/stockbot-ai` |
| **Run command** | `streamlit run dashboard.py` |

---

## What to show the instructor

1. Open `bot.py` — point to each of the 5 steps in the code
2. Open `config.py` — show how easy it is to change stocks / risk rules
3. Press ▶ Run → click **"Analyse Stocks Now"**
4. Show the **stock cards** with LLM decisions
5. Show the **ChromaDB section** — what text gets stored and retrieved
6. Show the **Trade History** table updating

---

> ⚠️ Paper money only. Not financial advice.
