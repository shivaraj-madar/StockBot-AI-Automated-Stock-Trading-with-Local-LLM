# ──────────────────────────────────────────────────────────────
#  bot.py  —  The entire trading brain
#
#  HOW IT WORKS (explain to instructor):
#
#  1. FETCH   — Download real stock price from Yahoo Finance
#  2. STORE   — Save price snapshot to ChromaDB (vector database)
#  3. SEARCH  — Find similar past snapshots from ChromaDB
#  4. DECIDE  — Ask local LLM (google/gemma-3-1b-it) what to do: BUY/SELL/HOLD
#  5. TRADE   — Update our paper portfolio
# ──────────────────────────────────────────────────────────────

import json
import yfinance as yf
import chromadb
from transformers import pipeline
from datetime import datetime
from config import (
    SYMBOLS, GEMMA_MODEL, STARTING_CASH,
    MAX_POSITION_PCT, STOP_LOSS_PCT, TAKE_PROFIT_PCT
)

# ── Load Gemma model once at startup ────────────────────────
# pipeline() downloads the model from HuggingFace on first run (~2GB)
print(f"Loading {GEMMA_MODEL} ... (first run downloads the model)")
_llm = pipeline(
    "text-generation",
    model=GEMMA_MODEL,
    max_new_tokens=150,
    do_sample=False,       # deterministic — same input → same output
)

# ── Setup ChromaDB (local vector database) ──────────────────
_chroma  = chromadb.Client()
_db      = _chroma.get_or_create_collection("price_history")

# ── Paper portfolio state ───────────────────────────────────
portfolio = {
    "cash":      STARTING_CASH,
    "holdings":  {},   # { "AAPL": {"shares": 5, "bought_at": 180.0} }
    "trades":    [],   # list of every trade made
}


# ═══════════════════════════════════════════════════════════
#  STEP 1 — Fetch real stock data
# ═══════════════════════════════════════════════════════════
def fetch_price(symbol: str) -> dict:
    """Download the latest price + basic stats for one stock."""
    ticker = yf.Ticker(symbol)
    hist   = ticker.history(period="5d", interval="1d")

    if hist.empty:
        return {}

    latest   = hist.iloc[-1]
    prev     = hist.iloc[-2] if len(hist) > 1 else latest
    change   = float(latest["Close"] - prev["Close"])
    chg_pct  = round(change / float(prev["Close"]) * 100, 2)

    return {
        "symbol":  symbol,
        "price":   round(float(latest["Close"]), 2),
        "high":    round(float(latest["High"]),  2),
        "low":     round(float(latest["Low"]),   2),
        "volume":  int(latest["Volume"]),
        "change":  round(change, 2),
        "chg_pct": chg_pct,
        "time":    datetime.now().strftime("%H:%M:%S"),
    }


# ═══════════════════════════════════════════════════════════
#  STEP 2 — Store snapshot in ChromaDB
# ═══════════════════════════════════════════════════════════
def store_snapshot(data: dict):
    """
    Turn the price data into a sentence, then save it in
    ChromaDB so we can search similar situations later.
    """
    text = (
        f"{data['symbol']} is at ${data['price']}, "
        f"changed {data['chg_pct']:+.1f}% today, "
        f"high ${data['high']}, low ${data['low']}."
    )
    doc_id = f"{data['symbol']}_{data['time']}"
    _db.add(documents=[text], ids=[doc_id],
            metadatas=[{"symbol": data["symbol"], "price": data["price"]}])
    return text


# ═══════════════════════════════════════════════════════════
#  STEP 3 — Search ChromaDB for similar past situations
# ═══════════════════════════════════════════════════════════
def find_similar(text: str, symbol: str) -> list[str]:
    """
    Ask ChromaDB: 'have we seen something like this before?'
    Returns the top 2 matching past snapshots.
    """
    count = _db.count()
    if count < 2:
        return []   # not enough history yet

    results = _db.query(
        query_texts=[text],
        n_results=min(2, count),
        where={"symbol": symbol},
    )
    return results["documents"][0] if results["documents"] else []


# ═══════════════════════════════════════════════════════════
#  STEP 4 — Ask local LLM to decide BUY / SELL / HOLD
# ═══════════════════════════════════════════════════════════
def llm_decide(data: dict, similar: list[str]) -> dict:
    """
    Build a short prompt and ask llama3.2 for a trading decision.
    The LLM must reply with JSON so we can parse it easily.
    """
    history_text = "\n".join(similar) if similar else "No past data yet."

    prompt = f"""You are a simple trading assistant.

CURRENT DATA:
- Stock: {data['symbol']}
- Price: ${data['price']}
- Today's change: {data['chg_pct']:+.1f}%
- Day high: ${data['high']}  |  Day low: ${data['low']}

SIMILAR PAST SITUATIONS:
{history_text}

Based on this, reply ONLY with valid JSON like this:
{{
  "action": "BUY" or "SELL" or "HOLD",
  "confidence": a number from 0 to 100,
  "reason": "one short sentence"
}}"""

    response = _llm(prompt)[0]["generated_text"]

    # Gemma echoes the prompt — grab only the new text after it
    raw = response[len(prompt):].strip()

    # Strip markdown fences if LLM adds them
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except Exception:
        return {"action": "HOLD", "confidence": 0, "reason": "Could not parse LLM response."}


# ═══════════════════════════════════════════════════════════
#  STEP 5 — Execute the trade (paper money only)
# ═══════════════════════════════════════════════════════════
def execute_trade(decision: dict, data: dict) -> dict:
    """
    Act on the LLM decision.
    Updates the portfolio cash and holdings.
    Returns a trade record.
    """
    symbol = data["symbol"]
    price  = data["price"]
    action = decision.get("action", "HOLD")
    record = {"time": data["time"], "symbol": symbol,
              "price": price, "action": action,
              "reason": decision.get("reason", ""),
              "shares": 0, "pnl": 0.0}

    # ── BUY ─────────────────────────────────────────────────
    if action == "BUY" and symbol not in portfolio["holdings"]:
        budget = portfolio["cash"] * MAX_POSITION_PCT
        shares = round(budget / price, 4)
        cost   = shares * price

        if cost > portfolio["cash"]:
            record["action"] = "HOLD"
            record["reason"] = "Not enough cash"
        else:
            portfolio["cash"] -= cost
            portfolio["holdings"][symbol] = {"shares": shares, "bought_at": price}
            record["shares"] = shares

    # ── SELL ────────────────────────────────────────────────
    elif action == "SELL" and symbol in portfolio["holdings"]:
        pos    = portfolio["holdings"].pop(symbol)
        shares = pos["shares"]
        pnl    = round((price - pos["bought_at"]) * shares, 2)
        portfolio["cash"] += shares * price
        record["shares"]   = shares
        record["pnl"]      = pnl

    # ── Check stop-loss / take-profit for existing holdings ──
    _check_exits(data)

    portfolio["trades"].append(record)
    return record


def _check_exits(data: dict):
    """Auto sell if stop-loss or take-profit is hit."""
    symbol = data["symbol"]
    price  = data["price"]
    if symbol not in portfolio["holdings"]:
        return

    pos       = portfolio["holdings"][symbol]
    bought_at = pos["bought_at"]
    change    = (price - bought_at) / bought_at

    reason = None
    if change <= -STOP_LOSS_PCT:
        reason = f"Stop-loss hit ({change*100:+.1f}%)"
    elif change >= TAKE_PROFIT_PCT:
        reason = f"Take-profit hit ({change*100:+.1f}%)"

    if reason:
        shares = pos["shares"]
        pnl    = round((price - bought_at) * shares, 2)
        portfolio["cash"] += shares * price
        del portfolio["holdings"][symbol]
        portfolio["trades"].append({
            "time": data["time"], "symbol": symbol,
            "price": price, "action": "AUTO-SELL",
            "reason": reason, "shares": shares, "pnl": pnl,
        })


# ═══════════════════════════════════════════════════════════
#  MAIN — Run one full cycle for all symbols
# ═══════════════════════════════════════════════════════════
def run_cycle() -> list[dict]:
    """
    Run steps 1-5 for every symbol.
    Returns a list of results (one per stock) for the dashboard.
    """
    results = []

    for symbol in SYMBOLS:
        # 1. Fetch
        data = fetch_price(symbol)
        if not data:
            continue

        # 2. Store in ChromaDB
        snapshot_text = store_snapshot(data)

        # 3. Find similar past situations
        similar = find_similar(snapshot_text, symbol)

        # 4. Ask LLM
        decision = llm_decide(data, similar)

        # 5. Execute
        trade = execute_trade(decision, data)

        results.append({
            "data":     data,
            "decision": decision,
            "trade":    trade,
            "similar":  similar,
        })

    return results


def get_portfolio_value(latest_prices: dict) -> float:
    """Total portfolio value = cash + value of all holdings."""
    value = portfolio["cash"]
    for symbol, pos in portfolio["holdings"].items():
        px = latest_prices.get(symbol, pos["bought_at"])
        value += pos["shares"] * px
    return round(value, 2)