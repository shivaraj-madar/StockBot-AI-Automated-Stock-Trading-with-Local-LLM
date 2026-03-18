# 📈 StockBot AI — Automated Stock Trading with Local LLM

> An AI Agentic Stock Trading Bot that uses a **Local LLM (TinyLlama-1.1B)** +
> **Vector Database (ChromaDB)** + **Real-Time Market Data (Yahoo Finance)**
> to automatically analyse stocks and make BUY / SELL / HOLD decisions.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)
![LLM](https://img.shields.io/badge/LLM-TinyLlama--1.1B-green)
![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)
![License](https://img.shields.io/badge/Mode-Paper%20Trading-yellow)

---

## 📌 Table of Contents

1. [About the Project](#about-the-project)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [How It Works](#how-it-works)
6. [Setup and Installation](#setup-and-installation)
7. [How to Run](#how-to-run)
8. [Dashboard Overview](#dashboard-overview)
9. [Configuration](#configuration)
10. [Project Details](#project-details)
11. [Disclaimer](#disclaimer)

---

## 📖 About the Project

**StockBot AI** is an AI-powered automated stock trading bot built as a
**Finance category AI Agentic project**. It combines three powerful technologies:

- 🧠 **Local LLM** — TinyLlama-1.1B runs completely on your laptop, no API key needed
- 🗄️ **Vector Database** — ChromaDB stores and searches historical market patterns
- 📡 **Real-Time Data** — Yahoo Finance provides live stock prices

The bot watches 4 stocks (AAPL, TSLA, NVDA, MSFT), analyses the market every time
you click the button, and decides whether to BUY, SELL, or HOLD each stock —
just like a real trading algorithm.

> ⚠️ This project uses **paper money only** ($10,000 virtual cash).
> No real money is involved. This is for educational purposes only.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 Local LLM | TinyLlama-1.1B runs 100% on your machine — no internet API needed |
| 🗄️ Vector Database | ChromaDB stores price snapshots and finds similar past patterns |
| 📡 Real-Time Prices | Fetches live stock data from Yahoo Finance |
| 📊 Live Dashboard | Streamlit dashboard with charts and portfolio tracking |
| 💰 Paper Trading | Starts with $10,000 virtual cash — completely safe to test |
| 🛡️ Risk Management | Auto stop-loss (5%) and take-profit (10%) built in |
| 📈 Candlestick Charts | 30-day price chart for each stock |
| 🔄 Auto Refresh | Optional 30-second auto-refresh mode |

---

## 🛠️ Tech Stack

| Technology | Purpose | Details |
|---|---|---|
| **Python** | Programming language | Version 3.11+ |
| **TinyLlama-1.1B** | Local LLM for trading decisions | Runs fully offline |
| **ChromaDB** | Vector database for pattern storage | Stores text embeddings |
| **HuggingFace Transformers** | Load and run the LLM locally | No API key needed |
| **yfinance** | Fetch real-time stock prices | Yahoo Finance data |
| **Streamlit** | Web dashboard UI | Runs in browser |
| **Plotly** | Interactive candlestick charts | 30-day price history |

---

## 📁 Project Structure

```
StockBot-AI/
│
├── config.py           ← All settings (stocks, risk rules, LLM model)
├── bot.py              ← The brain (fetch, store, search, decide, trade)
├── dashboard.py        ← The UI (press Run to open in browser)
├── requirements.txt    ← All Python packages needed
│
└── .vscode/
    └── launch.json     ← VS Code F5 run button configuration
```

Only **4 main files** — simple and easy to understand!

---

## ⚙️ How It Works

The bot follows **5 clear steps** every time it analyses stocks:

```
  ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
  │  STEP 1   │────▶│  STEP 2   │────▶│  STEP 3   │────▶│  STEP 4   │────▶│  STEP 5   │
  │  FETCH    │     │  STORE    │     │  SEARCH   │     │  DECIDE   │     │  TRADE    │
  └───────────┘     └───────────┘     └───────────┘     └───────────┘     └───────────┘
  Download live     Save snapshot     Find similar      Ask LLM:           Update paper
  stock price       to ChromaDB       past patterns     BUY/SELL/HOLD      portfolio
  from Yahoo        vector DB         from vector DB    (TinyLlama)
```

### Step 1 — FETCH
Downloads the latest stock price, high, low, volume and daily change
percentage from Yahoo Finance for every stock symbol in your watchlist.

### Step 2 — STORE
Converts the price data into a plain English sentence like:
> *"AAPL is at $189.23, changed +1.2% today, high $191.00, low $188.50."*

This sentence is saved into **ChromaDB** (vector database) with a
unique ID so it can be found and compared later.

### Step 3 — SEARCH
When a new market snapshot arrives, ChromaDB searches its stored history
to find the **top 2 most similar past situations** using vector similarity
search. This gives the LLM historical context to reason from.

### Step 4 — DECIDE
The bot sends a prompt to **TinyLlama-1.1B** (running locally on your laptop)
containing the current price data plus the similar past situations.
The LLM responds with structured JSON:

```json
{
  "action": "BUY",
  "confidence": 75,
  "reason": "Price rising with strong volume, similar past patterns showed gains."
}
```

### Step 5 — TRADE
Based on the LLM decision, the bot updates the paper portfolio:

| Decision | What happens |
|---|---|
| **BUY** | Spends 10% of available cash to buy shares |
| **SELL** | Sells all shares of that stock, records profit/loss |
| **HOLD** | Does nothing, waits for next cycle |
| **Auto Stop-Loss** | Automatically sells if price drops 5% from buy price |
| **Auto Take-Profit** | Automatically sells if price rises 10% from buy price |

---

## 🚀 Setup and Installation

### Prerequisites

Make sure these are installed on your laptop:

- ✅ Python 3.11+ → https://python.org/downloads
- ✅ VS Code → https://code.visualstudio.com
- ✅ Git → https://git-scm.com/download/win

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/shivaraj-madar/ai-trading-bot.git
cd ai-trading-bot
```

---

### Step 2 — Create a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac or Linux)
source venv/bin/activate
```

You will see `(venv)` appear in your terminal — this means it is active. ✅

---

### Step 3 — Install all packages

```bash
pip install -r requirements.txt
```

Packages installed:

| Package | Why |
|---|---|
| `yfinance` | Fetch real stock prices |
| `transformers` | Load TinyLlama LLM locally |
| `torch` | Run the LLM on CPU/GPU |
| `accelerate` | Speed up model loading |
| `chromadb` | Vector database |
| `streamlit` | Dashboard UI |
| `plotly` | Candlestick charts |

---

### Step 4 — First run (model download)

The **first time only**, TinyLlama downloads automatically. No login needed!

```
Loading TinyLlama/TinyLlama-1.1B-Chat-v1.0 ...
Downloading model: 100%|████████████| 2.2G/2.2G [05:30]
```

⏳ Wait about 5–10 minutes depending on your internet speed.
After downloading once, it is **cached on your laptop forever**.

---

## ▶️ How to Run

### Option A — VS Code (Recommended)

1. Open the project folder in VS Code
2. Press **F5** on your keyboard
3. Select **"▶ Run Trading Bot Dashboard"**
4. Browser opens automatically at `http://localhost:8501`

### Option B — Terminal

```bash
# Step 1 — Activate venv
venv\Scripts\activate

# Step 2 — Run dashboard
streamlit run dashboard.py
```

Open **http://localhost:8501** in your browser.

---

### Using the Dashboard

1. Click the big **"🔍 Analyse Stocks Now"** button
2. Wait 1–2 minutes while the bot works
3. Results appear automatically showing:
   - Stock cards with BUY / SELL / HOLD for each stock
   - Updated portfolio value and P&L
   - ChromaDB stored text and retrieved similar patterns
   - Trade history with every decision made

---

## 📊 Dashboard Overview

| Section | What it shows |
|---|---|
| **Top Banner** | Project name — StockBot AI |
| **5 Steps Bar** | Visual flow showing how the bot works |
| **Portfolio Bar** | Total value, P&L percentage, cash, open positions |
| **Stock Cards** | Live price + LLM decision (BUY/SELL/HOLD) + reason |
| **Candlestick Charts** | 30-day price history for each stock |
| **ChromaDB Section** | Exact text stored in vector DB and similar patterns retrieved |
| **Trade History** | Every trade with time, symbol, action, reason, and P&L |
| **Sidebar** | How it works explanation + auto-refresh toggle |

---

## 🔧 Configuration

All settings are in **`config.py`** — easy to change for your needs:

```python
# ── Stocks to watch ──────────────────────────────
SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT"]

# ── Local LLM model ──────────────────────────────
GEMMA_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# ── Starting paper money ─────────────────────────
STARTING_CASH = 10_000        # $10,000 virtual cash

# ── Risk management rules ────────────────────────
MAX_POSITION_PCT = 0.10       # max 10% of cash per trade
STOP_LOSS_PCT    = 0.05       # auto-sell if price drops 5%
TAKE_PROFIT_PCT  = 0.10       # auto-sell if price rises 10%
```

### Examples of changes you can make

**Add more stocks:**
```python
SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META"]
```

**Increase starting cash:**
```python
STARTING_CASH = 50_000        # $50,000
```

**Make the bot more aggressive (bigger trades):**
```python
MAX_POSITION_PCT = 0.20       # spend 20% per trade
```

**Tighter stop-loss:**
```python
STOP_LOSS_PCT = 0.02          # sell if drops 2%
```

---

## 👨‍💻 Project Details

| Item | Details |
|---|---|
| **Project Name** | StockBot AI |
| **Full Title** | Automated Stock Trading with Local LLM |
| **Category** | Finance / AI Agentic System |
| **Type** | Automated Trading Bot |
| **LLM Model** | TinyLlama-1.1B (Local — no API key required) |
| **Vector Database** | ChromaDB |
| **Data Source** | Yahoo Finance (Real-Time) |
| **Dashboard** | Streamlit |
| **Trading Mode** | Paper Trading (Virtual Money Only) |
| **Developer** | Shivaraj Madar |
| **GitHub** | https://github.com/shivaraj-madar/ai-trading-bot |

---

## ⚠️ Disclaimer

This project is built for **educational purposes only** as part of an
AI course / college project.

- Uses **paper money (virtual cash)** — no real money involved
- Not connected to any real brokerage or trading platform
- **NOT financial advice** of any kind
- Do not use this bot for real stock trading
- Past performance does not guarantee future results
- Always consult a licensed financial advisor before investing

---

## 📄 License

This project is open source and free to use for educational purposes.

---

*Built with ❤️ by Shivaraj Madar*
