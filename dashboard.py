# ──────────────────────────────────────────────────────────────
#  dashboard.py  —  Press ▶ Run in VS Code to start everything
#
#  Shows:
#   • Live stock prices
#   • LLM decision (BUY / SELL / HOLD) with reason
#   • Paper portfolio value
#   • Trade history table
# ──────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import time
from bot import run_cycle, get_portfolio_value, portfolio
from config import SYMBOLS, STARTING_CASH

# ── Page setup ──────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Bot",
    page_icon="📈",
    layout="wide",
)

# ── Clean CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: #0f1117;
    color: #e2e8f0;
}

.stApp { background: #0f1117; }

/* title banner */
.banner {
    background: linear-gradient(135deg, #0d1f3c 0%, #0f1117 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.banner-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px; font-weight: 600;
    color: #38bdf8;
    margin: 0;
}
.banner-sub { font-size: 12px; color: #64748b; margin-top: 4px; }
.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; font-weight: 600;
    padding: 4px 12px; border-radius: 20px;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    color: #38bdf8;
}

/* stock cards */
.stock-card {
    background: #161b27;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    position: relative;
}
.stock-card.BUY  { border-left: 4px solid #22c55e; }
.stock-card.SELL { border-left: 4px solid #ef4444; }
.stock-card.HOLD { border-left: 4px solid #64748b; }

.stock-symbol { font-family: 'IBM Plex Mono', monospace; font-size: 16px; font-weight: 600; color: #38bdf8; }
.stock-price  { font-family: 'IBM Plex Mono', monospace; font-size: 22px; font-weight: 600; color: #f1f5f9; }
.stock-chg.up   { color: #22c55e; font-size: 13px; }
.stock-chg.down { color: #ef4444; font-size: 13px; }

.action-pill {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; font-weight: 600;
    padding: 3px 12px; border-radius: 20px;
    margin-bottom: 6px;
}
.action-BUY  { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.4); }
.action-SELL { background: rgba(239,68,68,0.15);   color: #ef4444; border: 1px solid rgba(239,68,68,0.4); }
.action-HOLD { background: rgba(100,116,139,0.15); color: #94a3b8; border: 1px solid rgba(100,116,139,0.4); }

.reason-text { font-size: 12px; color: #64748b; margin-top: 4px; font-style: italic; }
.confidence  { font-size: 11px; color: #475569; margin-top: 2px; font-family: 'IBM Plex Mono', monospace; }

/* portfolio bar */
.port-bar {
    background: #161b27;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 16px 24px;
    display: flex; align-items: center; gap: 40px;
    margin-bottom: 20px;
}
.port-val { font-family: 'IBM Plex Mono', monospace; font-size: 26px; font-weight: 600; }
.port-label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; }
.port-pnl.pos { color: #22c55e; }
.port-pnl.neg { color: #ef4444; }

/* step diagram */
.steps { display: flex; gap: 6px; margin-bottom: 20px; flex-wrap: wrap; }
.step-box {
    background: #161b27;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    display: flex; align-items: center; gap: 6px;
}
.step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; font-weight: 600;
    color: #38bdf8;
}
.step-arrow { color: #1e2d45; font-size: 16px; }

/* trade table */
.trade-row {
    display: grid;
    grid-template-columns: 70px 60px 80px 1fr 70px;
    gap: 8px;
    padding: 8px 12px;
    border-bottom: 1px solid #1a2035;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    align-items: center;
}
.trade-row.header { color: #475569; font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; }
.pnl-pos { color: #22c55e; }
.pnl-neg { color: #ef4444; }
.pnl-neu { color: #64748b; }

.section-head {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; font-weight: 600;
    color: #38bdf8; text-transform: uppercase;
    letter-spacing: 0.1em; margin: 20px 0 10px;
    border-bottom: 1px solid #1e2d45; padding-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Banner ───────────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <div>
    <div class="banner-title">📈 AI Trading Bot</div>
    <div class="banner-sub">Local LLM + Vector DB · Paper Trading · Finance Project</div>
  </div>
  <div class="badge">📄 PAPER MONEY ONLY</div>
</div>
""", unsafe_allow_html=True)

# ── How it works — 5 steps ──────────────────────────────────
st.markdown("""
<div class="steps">
  <div class="step-box"><span class="step-num">1</span> Fetch real price</div>
  <div class="step-arrow">→</div>
  <div class="step-box"><span class="step-num">2</span> Save to ChromaDB</div>
  <div class="step-arrow">→</div>
  <div class="step-box"><span class="step-num">3</span> Find similar past</div>
  <div class="step-arrow">→</div>
  <div class="step-box"><span class="step-num">4</span> Ask LLM (TinyLlama-1.1B)</div>
  <div class="step-arrow">→</div>
  <div class="step-box"><span class="step-num">5</span> Execute trade</div>
</div>
""", unsafe_allow_html=True)

# ── Portfolio value bar ──────────────────────────────────────
def render_portfolio(latest_prices: dict):
    total  = get_portfolio_value(latest_prices)
    pnl    = round(total - STARTING_CASH, 2)
    pnl_pct = round(pnl / STARTING_CASH * 100, 2)
    cls    = "pos" if pnl >= 0 else "neg"
    sign   = "+" if pnl >= 0 else ""
    cash   = round(portfolio["cash"], 2)
    n_hold = len(portfolio["holdings"])

    st.markdown(f"""
    <div class="port-bar">
      <div>
        <div class="port-label">Portfolio Value</div>
        <div class="port-val port-pnl {cls}">${total:,.2f}</div>
      </div>
      <div>
        <div class="port-label">Total P&amp;L</div>
        <div class="port-val port-pnl {cls}">{sign}${pnl:,.2f} ({sign}{pnl_pct}%)</div>
      </div>
      <div>
        <div class="port-label">Cash Available</div>
        <div class="port-val" style="color:#f1f5f9">${cash:,.2f}</div>
      </div>
      <div>
        <div class="port-label">Open Positions</div>
        <div class="port-val" style="color:#f1f5f9">{n_hold}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Stock card ───────────────────────────────────────────────
def render_stock_card(result: dict):
    d   = result["data"]
    dec = result["decision"]
    chg_class = "up" if d["chg_pct"] >= 0 else "down"
    sign      = "▲" if d["chg_pct"] >= 0 else "▼"
    action    = dec.get("action", "HOLD")
    conf      = dec.get("confidence", 0)
    reason    = dec.get("reason", "")

    in_portfolio = d["symbol"] in portfolio["holdings"]
    port_info = ""
    if in_portfolio:
        pos = portfolio["holdings"][d["symbol"]]
        pnl = round((d["price"] - pos["bought_at"]) * pos["shares"], 2)
        pnl_cls = "pnl-pos" if pnl >= 0 else "pnl-neg"
        port_info = f'<div class="{pnl_cls}" style="font-size:11px;font-family:\'IBM Plex Mono\',monospace;margin-top:6px;">Holding {pos["shares"]} shares · P&L ${pnl:+.2f}</div>'

    return f"""
    <div class="stock-card {action}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div class="stock-symbol">{d['symbol']}</div>
          <div class="stock-price">${d['price']}</div>
          <div class="stock-chg {chg_class}">{sign} {abs(d['chg_pct'])}% today</div>
        </div>
        <div style="text-align:right;">
          <div class="action-pill action-{action}">{action}</div>
          <div class="confidence">Confidence: {conf}%</div>
        </div>
      </div>
      <div class="reason-text">"{reason}"</div>
      {port_info}
    </div>
    """

# ── Candlestick chart ────────────────────────────────────────
def render_chart(symbol: str):
    df = yf.Ticker(symbol).history(period="30d", interval="1d")
    if df.empty:
        return

    fig = go.Figure(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
    ))
    fig.update_layout(
        height=200, margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="#161b27", plot_bgcolor="#161b27",
        font=dict(color="#64748b", size=10),
        xaxis=dict(gridcolor="#1e2d45", showgrid=True),
        yaxis=dict(gridcolor="#1e2d45", showgrid=True),
        xaxis_rangeslider_visible=False,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key=symbol)

# ── Trade history table ──────────────────────────────────────
def render_trade_history():
    trades = portfolio["trades"]
    if not trades:
        st.markdown('<div style="color:#475569;font-size:13px;">No trades yet — click Analyse to start.</div>', unsafe_allow_html=True)
        return

    rows_html = """
    <div class="trade-row header">
      <div>Time</div><div>Symbol</div><div>Action</div><div>Reason</div><div>P&L</div>
    </div>
    """
    for t in reversed(trades[-15:]):
        pnl     = t.get("pnl", 0)
        pnl_cls = "pnl-pos" if pnl > 0 else "pnl-neg" if pnl < 0 else "pnl-neu"
        pnl_str = f"+${pnl:.2f}" if pnl > 0 else f"${pnl:.2f}" if pnl < 0 else "—"
        action  = t.get("action", "HOLD")
        color   = "#22c55e" if action == "BUY" else "#ef4444" if "SELL" in action else "#64748b"
        rows_html += f"""
        <div class="trade-row">
          <div style="color:#475569">{t['time']}</div>
          <div style="color:#38bdf8">{t['symbol']}</div>
          <div style="color:{color}">{action}</div>
          <div style="color:#64748b;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">{t.get('reason','')}</div>
          <div class="{pnl_cls}">{pnl_str}</div>
        </div>
        """
    st.markdown(rows_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ════════════════════════════════════════════════════════════

# Sidebar controls
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    auto = st.toggle("Auto-refresh (30s)", value=False)
    st.markdown("---")
    st.markdown("### 📚 How it works")
    st.markdown("""
**Step 1 — Fetch**
Real price data from Yahoo Finance

**Step 2 — Store**
Save snapshot text into ChromaDB (vector database)

**Step 3 — Search**
Find similar past market conditions

**Step 4 — Decide**
Local LLM (`TinyLlama-1.1B`) reads current + past data, outputs BUY / SELL / HOLD

**Step 5 — Trade**
Update paper portfolio with the decision
""")
    st.markdown("---")
    st.caption("⚠️ Paper money only. Not financial advice.")

# Analyse button
clicked = st.button("🔍 Analyse Stocks Now", type="primary", use_container_width=True)

if "results" not in st.session_state:
    st.session_state.results = []

if clicked or (auto and st.session_state.get("auto_ran")):
    with st.spinner("Fetching prices and asking LLM..."):
        st.session_state.results = run_cycle()
        st.session_state.auto_ran = True

results = st.session_state.results

# Portfolio bar
latest_prices = {r["data"]["symbol"]: r["data"]["price"] for r in results}
render_portfolio(latest_prices)

# Stock cards + charts
if results:
    st.markdown('<div class="section-head">Market Analysis</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, result in enumerate(results):
        with cols[i % 2]:
            st.markdown(render_stock_card(result), unsafe_allow_html=True)
            render_chart(result["data"]["symbol"])

    # Vector DB info box
    st.markdown('<div class="section-head">Vector Database (ChromaDB)</div>', unsafe_allow_html=True)
    vcol1, vcol2 = st.columns(2)
    with vcol1:
        sample = results[0]
        st.markdown(f"""
        <div style="background:#161b27;border:1px solid #1e2d45;border-radius:10px;padding:14px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#38bdf8;margin-bottom:8px;">STORED TEXT (what gets embedded)</div>
          <div style="font-size:13px;color:#94a3b8;line-height:1.6;">
            "{sample['data']['symbol']} is at ${sample['data']['price']},
             changed {sample['data']['chg_pct']:+.1f}% today,
             high ${sample['data']['high']}, low ${sample['data']['low']}."
          </div>
        </div>
        """, unsafe_allow_html=True)
    with vcol2:
        sample_sim = results[0]["similar"]
        sim_text = "<br>".join(sample_sim) if sample_sim else "No similar history yet — run more cycles to build up the DB."
        st.markdown(f"""
        <div style="background:#161b27;border:1px solid #1e2d45;border-radius:10px;padding:14px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#38bdf8;margin-bottom:8px;">RETRIEVED SIMILAR PAST SNAPSHOTS</div>
          <div style="font-size:13px;color:#94a3b8;line-height:1.6;">{sim_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Trade history
    st.markdown('<div class="section-head">Trade History</div>', unsafe_allow_html=True)
    render_trade_history()

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#475569;">
      <div style="font-size:40px;margin-bottom:12px;">📈</div>
      <div style="font-size:16px;margin-bottom:6px;color:#94a3b8;">Click <strong style="color:#38bdf8">Analyse Stocks Now</strong> to start</div>
      <div style="font-size:13px;">The bot will fetch real prices, store them in ChromaDB, and ask the local LLM what to do.</div>
    </div>
    """, unsafe_allow_html=True)

# Auto-refresh
if auto:
    time.sleep(30)
    st.rerun()