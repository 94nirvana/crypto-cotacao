"""
Crypto Quote REST API — Flask

Provides real-time crypto quotes (price + 24h volume) for a fixed basket of
coins.  Quotes are refreshed every 2 seconds via a background thread that
hits the Binance public API.

Endpoints
---------
GET /api/quotes          — JSON list ordered by 24h traded volume (desc)
GET /api/quotes/<symbol>  — JSON quote for a single coin
GET /                     — Minimalist HTML dashboard
"""

import os
import threading
import time
from collections import OrderedDict

import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
QUOTE_COINS = {
    "BTC":  "BTCUSDT",
    "USDT": "USDTUSDT",   # USDT/BUSD — treat as USD-stable
    "USDC": "USDCUSDT",
    "ETH":  "ETHUSDT",
    "XRP":  "XRPUSDT",
    "SOL":  "SOLUSDT",
    "BNB":  "BNBUSDT",
    "USDG": "USDGUSDT",
    "DOGE": "DOGEUSDT",
    "UNI":  "UNIUSDT",
    "TRX":  "TRXUSDT",
    "ADA":  "ADAUSDT",
    "XLM":  "XLMUSDT",
    "LINK": "LINKUSDT",
}

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"
REFRESH_INTERVAL = 2  # seconds

# ---------------------------------------------------------------------------
# Cache (thread-safe)
# ---------------------------------------------------------------------------
_cache_lock = threading.Lock()
_cache: list[dict] = []
_last_fetch_ok = False
_last_error = ""
_last_fetch_ts = 0.0


def _fetch_quotes() -> None:
    """Fetch 24h-ticker data for every configured coin from Binance."""
    global _cache, _last_fetch_ok, _last_error, _last_fetch_ts

    pairs = ",".join(QUOTE_COINS.values())
    try:
        resp = requests.get(
            BINANCE_URL, params={"symbol": pairs}, timeout=5
        )
        resp.raise_for_status()
        data = resp.json()  # always a list when multiple symbols
    except Exception as exc:  # noqa: BLE001
        try:
            # Fallback: fetch one-by-one
            data = []
            for sym in QUOTE_COINS.values():
                r = requests.get(
                    BINANCE_URL, params={"symbol": sym}, timeout=5
                )
                if r.ok:
                    data.append(r.json())
        except Exception as exc2:  # noqa: BLE001
            _last_fetch_ok = False
            _last_error = str(exc2)
            return

    quotes = []
    for item in data:
        symbol = item.get("symbol", "")
        coin = None
        for k, v in QUOTE_COINS.items():
            if v == symbol:
                coin = k
                break
        if coin is None:
            continue

        quotes.append(
            {
                "symbol": coin,
                "price": float(item["lastPrice"]),
                "change24h": float(item["priceChangePercent"]),
                "volume24h": float(item["volume"]),
                "quote_volume24h": float(item["quoteVolume"]),
            }
        )

    # Sort by 24h volume (desc) — i.e. most-traded first
    quotes.sort(key=lambda q: q["volume24h"], reverse=True)

    with _cache_lock:
        _cache = quotes
        _last_fetch_ok = True
        _last_error = ""
        _last_fetch_ts = time.time()


def _background_loop() -> None:
    while True:
        _fetch_quotes()
        time.sleep(REFRESH_INTERVAL)


# Seed the cache immediately so /api/quotes never returns empty
_fetch_quotes()
threading.Thread(target=_background_loop, daemon=True).start()


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@app.route("/api/quotes")
def api_quotes():
    with _cache_lock:
        data = list(_cache)
        ok = _last_fetch_ok
        err = _last_error
        ts = _last_fetch_ts
    return jsonify(
        {
            "ok": ok,
            "error": err if not ok else "",
            "timestamp": ts,
            "quotes": data,
        }
    )


@app.route("/api/quotes/<symbol>")
def api_quote_single(symbol: str):
    symbol = symbol.upper()
    with _cache_lock:
        data = list(_cache)
    for q in data:
        if q["symbol"] == symbol:
            return jsonify({"ok": True, "quote": q})
    return jsonify({"ok": False, "error": f"Unknown symbol: {symbol}"}), 404


# ---------------------------------------------------------------------------
# HTML Dashboard
# ---------------------------------------------------------------------------
HTML_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crypto Quotes</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
      background:#0d0f12; color:#d4d6db; padding:2rem; max-width:900px; margin:0 auto;
    }
    h1 { font-size:1.4rem; margin-bottom:0.2rem; }
    .subtitle { font-size:0.8rem; color:#6a6f7a; margin-bottom:1.5rem; }
    .grid {
      display:grid; grid-template-columns:1fr; gap:0.4rem;
    }
    .card {
      background:#1a1c22; border:1px solid #2a2d37; border-radius:10px;
      padding:1rem 1.2rem; display:flex; justify-content:space-between;
      align-items:center; transition:opacity 0.2s;
    }
    .left { display:flex; align-items:center; gap:0.8rem; }
    .badge {
      font-size:0.7rem; font-weight:600; padding:0.2rem 0.6rem;
      border-radius:6px; background:#23262f; color:#8b91a3;
    }
    .name { font-weight:600; font-size:0.95rem; }
    .price { font-size:0.9rem; color:#8b91a3; }
    .right { text-align:right; }
    .price-val { font-size:1rem; font-weight:600; }
    .change { font-size:0.8rem; margin-top:0.15rem; }
    .pos { color:#27ae60; }
    .neg { color:#e74c3c; }
    .vol { font-size:0.75rem; color:#5a5f6d; margin-top:0.15rem; }
    .meta { font-size:0.75rem; color:#5a5f6d; margin-bottom:1rem; }
    .loading { opacity:0.5; }
  </style>
</head>
<body>
  <h1>Crypto Quotes</h1>
  <p class="subtitle">Ordenado por volume 24h (da maior para a menor)</p>
  <p class="meta" id="meta">Carregando...</p>
  <div class="grid" id="grid"></div>

  <script>
  const REFRESH_MS = 2000;

  function fmt(num, fix) {
    if (num === null || num === undefined) return '—';
    if (Math.abs(num) >= 1e9) return (num/1e9).toFixed(fix) + 'B';
    if (Math.abs(num) >= 1e6) return (num/1e6).toFixed(fix) + 'M';
    if (Math.abs(num) >= 1e3) return (num/1e3).toFixed(fix) + 'K';
    return num.toFixed(fix);
  }

  function render(quotes) {
    const g = document.getElementById('grid');
    g.innerHTML = '';
    quotes.forEach(q => {
      const chgCls = q.change24h >= 0 ? 'pos' : 'neg';
      const chgSign = q.change24h >= 0 ? '+' : '';
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML =
        '<div class="left">'
        + '<span class="badge">' + q.symbol + '</span>'
        + '<div><div class="name">' + q.symbol + '</div><div class="price">24h volume: ' + fmt(q.volume24h, 2) + '</div></div>'
        + '</div>'
        + '<div class="right">'
        + '<div class="price-val">$' + q.price.toLocaleString('en-US', {minimumFractionDigits: q.price < 1 ? 4 : 2, maximumFractionDigits: q.price < 1 ? 4 : 2}) + '</div>'
        + '<div class="change ' + chgCls + '">' + chgSign + q.change24h.toFixed(2) + '%</div>'
        + '</div>';
      g.appendChild(card);
    });
  }

  async function fetchQuotes() {
    try {
      const r = await fetch('/api/quotes');
      const d = await r.json();
      if (d.ok) {
        render(d.quotes);
        const t = new Date((d.timestamp || 0) * 1000 || Date.now());
        document.getElementById('meta').textContent =
          'Última atualização: ' + d.quotes.length + ' cotações · ' + t.toLocaleTimeString('pt-BR');
      }
    } catch(e) {
      document.getElementById('meta').textContent = 'Erro ao buscar cotações';
    }
  }

  fetchQuotes();
  setInterval(fetchQuotes, REFRESH_MS);
  </script>
</body>
</html>
"""

@app.route("/")
def dashboard():
    return render_template_string(HTML_PAGE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
