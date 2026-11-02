"""
Kaftet Restock Analytics: Executive Dashboard
==============================================
Streamlit + Plotly.

Jalankan:
    streamlit run kaftet_dashboard.py

Sumber data : output/kaftet_dashboard_data.csv (dibuat oleh prepare_dashboard_data.py)
Catatan     : ini data RESTOCK / PEMBELIAN, bukan data penjualan atau permintaan.
"""
from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ======================================================================================
# DESIGN TOKENS
# ======================================================================================
INK = "#0F2A43"       # judul, angka utama
PRIMARY = "#0E7C86"   # warna utama (teal)
PRIMARY_2 = "#35A7B2"  # teal terang
PRIMARY_P = "#E6F4F5"  # teal sangat muda
TEXT = "#334155"
MUTED = "#64748B"
LINE = "#E5EAF0"
BG = "#F4F6F9"
CARD = "#FFFFFF"
UP = "#C2410C"        # harga naik (biaya bertambah)
DOWN = "#15803D"      # harga turun
AMBER = "#B45309"
AMBER_P = "#FEF3C7"
PALETTE = [PRIMARY, INK, PRIMARY_2, "#7C9CBF", "#D9A441", "#8FB8B0", "#B6C2D0"]
PFONT = "Inter, 'Segoe UI', system-ui, -apple-system, Arial, sans-serif"
PCFG = {"displayModeBar": False}

DATA_PATH = Path(__file__).parent / "output" / "kaftet_dashboard_data.csv"

# ======================================================================================
# PAGE CONFIG
# ======================================================================================
st.set_page_config(
    page_title="Kaftet Restock Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

# ======================================================================================
# GLOBAL CSS  (disuntik lewat st.html — TIDAK diparse sebagai Markdown,
# sehingga baris kosong / indentasi tidak merusak blok <style>)
# ======================================================================================
_CSS_VARS = f"""
:root {{
  --ink:{INK}; --primary:{PRIMARY}; --primary-2:{PRIMARY_2}; --primary-p:{PRIMARY_P};
  --text:{TEXT}; --muted:{MUTED}; --line:{LINE}; --bg:{BG}; --card:{CARD};
  --up:{UP}; --down:{DOWN}; --amber:{AMBER}; --amber-p:{AMBER_P};
}}
"""

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp { font-family: Inter,'Segoe UI',system-ui,-apple-system,Arial,sans-serif; }
.stApp *:not([data-testid="stIconMaterial"]):not(.material-icons):not(.material-symbols-rounded) { font-family: Inter,'Segoe UI',system-ui,-apple-system,Arial,sans-serif; }
.stApp { background: var(--bg); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display:none !important; }
header[data-testid="stHeader"] { background: transparent; height: 2.6rem; }
[data-testid="stMainBlockContainer"], .block-container { padding: 1.2rem 2.2rem 2.5rem; max-width: 1520px; }
h1,h2,h3,h4 { color: var(--ink); letter-spacing: -.01em; }

/* ---------- sidebar (gelap) ---------- */
[data-testid="stSidebar"] { background: #0B1F33; border-right: none; transition: width .22s ease, min-width .22s ease, max-width .22s ease; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding: .9rem .9rem 1rem; }
.st-key-sb_full [data-testid="stVerticalBlock"] { gap: .75rem; }
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { display:none; }
.brand { display:flex; align-items:center; gap:11px; padding: 2px 0; }
.brand .logo, .rail-logo { width:38px; height:38px; border-radius:11px; background: linear-gradient(135deg,#17A2B0,#0E7C86); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.1rem; flex:0 0 auto; box-shadow: 0 4px 12px rgba(14,124,134,.35); }
.brand b { display:block; color:#fff; font-size:.92rem; line-height:1.15; }
.brand span { color:#8FA6BC; font-size:.74rem; }
.sb-title { font-size:.66rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#7F96AD; margin: 18px 0 4px; display:flex; align-items:center; gap:8px; }
.sb-title::after { content:""; flex:1; height:1px; background: rgba(255,255,255,.08); }
.sb-note { font-size:.74rem; line-height:1.55; color:#9FB3C8; background: rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:11px 13px; margin-top: 12px; }
.sb-note b { color:#fff; }
.rail-logo { margin: 4px auto 6px; }
.rail-sep { height:1px; width:36px; background: rgba(255,255,255,.1); margin: 6px auto; }
.rail-badge { margin: 2px auto 0; background:#0E7C86; color:#fff; border-radius:999px; font-size:.64rem; font-weight:700; padding:2px 8px; letter-spacing:.04em; white-space:nowrap; }

/* teks & label */
[data-testid="stSidebar"] label p, [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size:.8rem; font-weight:600; color:#D3DEE9; }
[data-testid="stSidebar"] [data-testid="stTooltipIcon"] svg { color:#8FA6BC; fill:#8FA6BC; }
/* select / multiselect */
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: rgba(255,255,255,.07) !important; border:1px solid rgba(255,255,255,.12) !important; border-radius:10px !important; color:#E6EEF6; }
[data-testid="stSidebar"] [data-baseweb="select"] input { color:#E6EEF6 !important; -webkit-text-fill-color:#E6EEF6; }
[data-testid="stSidebar"] [data-baseweb="select"] input::placeholder { color:#8FA6BC !important; -webkit-text-fill-color:#8FA6BC; }
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill:#9FB3C8; color:#9FB3C8; }
[data-testid="stSidebar"] span[data-baseweb="tag"] { background:#0E7C86 !important; color:#fff !important; border-radius:6px; font-weight:600; }
[data-testid="stSidebar"] span[data-baseweb="tag"] span, [data-testid="stSidebar"] span[data-baseweb="tag"] svg { color:#fff !important; fill:#fff !important; }
/* pills */
[data-testid="stSidebar"] button[data-variant="pills"] { border-radius:999px; background:transparent; color:#C9D6E3; border:1px solid rgba(255,255,255,.22); font-size:.78rem; font-weight:600; }
[data-testid="stSidebar"] button[data-variant="pills"] p { color:inherit; }
[data-testid="stSidebar"] button[data-variant="pills"][data-selected="true"] { background:#0E7C86; border-color:#0E7C86; color:#fff; }
[data-testid="stSidebar"] button[data-variant="pills"]:hover { border-color:#35A7B2; color:#fff; }
[data-testid="stSidebar"] [data-testid="stPills"] button { border-radius:999px; font-size:.78rem; font-weight:600; background: transparent; color:#C9D6E3; border:1px solid rgba(255,255,255,.22); }
[data-testid="stSidebar"] [data-testid="stPills"] button p { color:inherit; }
[data-testid="stSidebar"] [data-testid="stPills"] button:hover { border-color:#35A7B2; color:#fff; }
[data-testid="stSidebar"] [data-testid="stPills"] button[kind="pillsActive"], [data-testid="stSidebar"] [data-testid="stBaseButton-pillsActive"] { background:#0E7C86; color:#fff; border-color:#0E7C86; }
/* tombol di panel lebar */
.st-key-sb_full [data-testid="stBaseButton-secondary"] { background: rgba(255,255,255,.07); color:#E6EEF6; border:1px solid rgba(255,255,255,.14); border-radius:10px; }
.st-key-sb_full [data-testid="stBaseButton-secondary"] p { color:#E6EEF6; }
.st-key-sb_full [data-testid="stBaseButton-secondary"]:hover { background: rgba(255,255,255,.14); border-color:#35A7B2; }
.st-key-sb_collapse button { width:32px; height:32px; min-height:32px; padding:0; border-radius:9px; }
.st-key-sb_full { position:relative; }
.st-key-sb_collapse { position:absolute; top:3px; right:0; z-index:3; width:auto !important; }
.brand { padding-right:46px; white-space:nowrap; }
/* rel ikon */
.st-key-sb_rail [data-testid="stVerticalBlock"] { align-items:center; gap:.35rem; }
.st-key-sb_rail [data-testid="stElementContainer"] { width:100% !important; display:flex; justify-content:center; }
.st-key-sb_rail [data-testid="stButton"], .st-key-sb_rail [data-testid="stDownloadButton"] { width:100% !important; display:flex; justify-content:center; margin:0 !important; }
.st-key-sb_rail button, .st-key-sb_rail [data-testid="stDownloadButton"] button { width:46px; height:46px; min-height:46px; padding:0; flex:0 0 46px; border-radius:12px; background: transparent; border:none; color:#B7C7D8; }
.st-key-sb_rail button p { display:none; }
.st-key-sb_rail button:hover { background: rgba(255,255,255,.1); color:#fff; }
.st-key-rail_open button { background:#0E7C86 !important; color:#fff !important; }
.st-key-sb_rail [data-testid="stIconMaterial"] { font-size:22px; }

/* ---------- top bar ---------- */
.topbar { display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:14px; padding: 4px 2px 16px; }
.topbar .eyebrow { font-size:.72rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color: var(--primary); }
.topbar h1 { margin: 2px 0 2px; font-size:1.85rem; font-weight:700; line-height:1.1; padding:0; color: var(--ink); }
.topbar p { margin:0; color: var(--muted); font-size:.9rem; }
.chips { display:flex; flex-wrap:wrap; gap:8px; }
.chip { display:inline-flex; align-items:center; gap:6px; background: var(--card); border:1px solid var(--line); color: var(--text); border-radius:999px; padding:5px 12px; font-size:.76rem; font-weight:600; }
.chip.warn { background: var(--amber-p); border-color:#F6DFA0; color: var(--amber); }
.chip .dot { width:7px; height:7px; border-radius:50%; background: var(--primary); display:inline-block; }

/* ---------- KPI ---------- */
.kpi-grid { display:grid; grid-template-columns: 1.4fr repeat(5, 1fr); gap:12px; }
.kpi { background: var(--card); border:1px solid var(--line); border-radius:12px; padding:15px 17px 14px; box-shadow: 0 1px 2px rgba(15,42,67,.04); }
.kpi .l { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:.67rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; color: var(--muted); }
.kpi .v { font-size:clamp(1.2rem,1.25vw + .55rem,1.5rem); font-weight:700; color: var(--ink); margin:7px 0 3px; line-height:1.1; font-variant-numeric: tabular-nums; white-space:nowrap; }
.kpi .s { font-size:.74rem; color: var(--muted); line-height:1.35; }
.kpi.hero { background: linear-gradient(135deg, var(--ink), #16507A); border-color: var(--ink); }
.kpi.hero .l { color:#A9C4DA; } .kpi.hero .v { color:#fff; } .kpi.hero .s { color:#C5D8E8; }

/* ---------- cards ---------- */
[class*="st-key-card"] { background: var(--card); border:1px solid var(--line); border-radius:12px; padding: 16px 18px 12px; box-shadow: 0 1px 2px rgba(15,42,67,.04); }
.ch { margin-bottom: 4px; }
.ch .t { font-size:.95rem; font-weight:600; color: var(--ink); }
.ch .d { font-size:.76rem; color: var(--muted); margin-top:1px; }
.sec { display:flex; align-items:center; gap:10px; margin: 6px 0 2px; }
.sec b { font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color: var(--primary); white-space:nowrap; }
.sec i { flex:1; height:1px; background: var(--line); display:block; }

/* ---------- tabs ---------- */
[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
button[data-baseweb="tab"] { height: 42px; padding: 0 16px; background: transparent; border-radius: 8px 8px 0 0; }
button[data-baseweb="tab"] p { font-size:.88rem; font-weight:600; color: var(--muted); }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--primary); }
[data-baseweb="tab-highlight"] { background-color: var(--primary) !important; height: 3px; }

/* ---------- tables ---------- */
.tbl-wrap { overflow-x:auto; border:1px solid var(--line); border-radius:10px; margin-top:6px; }
table.tbl { width:100%; border-collapse: collapse; font-size:.82rem; }
.tbl th { background:#F8FAFC; color: var(--muted); font-size:.68rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase; padding:10px 12px; border-bottom:1px solid var(--line); white-space:nowrap; }
.tbl td { padding:10px 12px; border-bottom:1px solid #EEF2F6; color: var(--text); font-variant-numeric: tabular-nums; }
.tbl tr:last-child td { border-bottom:none; }
.tbl tbody tr:hover td { background:#FAFCFD; }
.tbl .l { text-align:left; } .tbl .r { text-align:right; } .tbl .c { text-align:center; }
.pill { display:inline-block; padding:2px 9px; border-radius:999px; font-size:.7rem; font-weight:700; }
.pill.warn { background: var(--amber-p); color: var(--amber); }
.pill.ok { background:#DCFCE7; color:#166534; }
.up { color: var(--up); font-weight:600; } .down { color: var(--down); font-weight:600; } .flat { color: var(--muted); }

/* ---------- insight lists ---------- */
ul.ins { margin:4px 0 0 !important; padding:0 !important; list-style:none !important; }
ul.ins li { list-style:none !important; position:relative; padding: 9px 0 9px 22px; border-bottom:1px solid #EEF2F6; font-size:.86rem; line-height:1.5; color: var(--text); }
.ins li:last-child { border-bottom:none; }
.ins li::before { content:""; position:absolute; left:2px; top:16px; width:8px; height:8px; border-radius:50%; background: var(--primary); }
.ins.rec li::before { background:#D9A441; }
.ins b { color: var(--ink); }
.callout { background: var(--amber-p); border:1px solid #F6DFA0; border-radius:10px; padding:11px 14px; font-size:.82rem; color:#7A4A07; line-height:1.55; }
.callout b { color:#5E3805; }
.foot { display:flex; flex-wrap:wrap; gap:6px 18px; font-size:.74rem; color: var(--muted); padding: 18px 2px 0; border-top:1px solid var(--line); margin-top: 22px; }
.foot b { color: var(--ink); }
.empty { color: var(--muted); font-size:.85rem; padding: 28px 8px; text-align:center; }

/* ---------- widget polish ---------- */
[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button { font-size:.78rem; font-weight:600; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:10px; overflow:hidden; }
[data-testid="stVerticalBlock"] { gap: .9rem; }
[class*="st-key-card"] [data-testid="stVerticalBlock"] { gap: .4rem; }

/* ---------- responsive ---------- */
@media (max-width: 1399px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 640px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"], .block-container { padding: 1rem 1rem 2rem; }
  .topbar h1 { font-size:1.45rem; }
  .kpi .v { font-size:1.3rem; }
}
"""
st.html(f"<style>{_CSS_VARS}{_CSS}</style>")


# ======================================================================================
# HELPERS
# ======================================================================================
def _id(x: float, decimals: int = 0) -> str:
    """Format angka gaya Indonesia: 1.234.567,89"""
    s = f"{x:,.{decimals}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def rupiah(x, decimals: int = 0) -> str:
    return "n/a" if pd.isna(x) else f"Rp{_id(x, decimals)}"


def rp_short(x) -> str:
    if pd.isna(x):
        return "n/a"
    a = abs(x)
    if a >= 1_000_000:
        return f"Rp{_id(x / 1_000_000, 2)} jt"
    if a >= 1_000:
        return f"Rp{_id(x / 1_000, 0)} rb"
    return f"Rp{_id(x)}"


def trunc(s: str, n: int = 32) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def esc(x) -> str:
    return html.escape(str(x))


def pct_html(v) -> str:
    if pd.isna(v):
        return '<span class="flat">Awal</span>'
    if abs(v) < 0.05:
        return '<span class="flat">0,0%</span>'
    cls, arrow = ("up", "▲") if v > 0 else ("down", "▼")
    return f'<span class="{cls}">{arrow} {_id(abs(v), 1)}%</span>'


def table_html(df: pd.DataFrame, align: dict | None = None, raw: tuple = ()) -> str:
    """Tabel HTML rapi (angka rata-kanan). Kolom di `raw` boleh berisi HTML."""
    align = align or {}
    head = "".join(f'<th class="{align.get(c, "l")}">{esc(c)}</th>' for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        tds = "".join(
            f'<td class="{align.get(c, "l")}">{r[c] if c in raw else esc(r[c])}</td>' for c in df.columns
        )
        rows.append(f"<tr>{tds}</tr>")
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def card_head(title: str, desc: str = "") -> None:
    d = f'<div class="d">{desc}</div>' if desc else ""
    st.html(f'<div class="ch"><div class="t">{title}</div>{d}</div>')


def section(title: str) -> None:
    st.html(f'<div class="sec"><b>{title}</b><i></i></div>')


def kpi(label: str, value: str, sub: str, hero: bool = False) -> str:
    return (
        f'<div class="kpi{" hero" if hero else ""}"><div class="l">{label}</div>'
        f'<div class="v">{value}</div><div class="s">{sub}</div></div>'
    )


def base_fig(fig: go.Figure, height: int = 340, legend: bool = False, **layout) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=4, t=6, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=PFONT, color=TEXT, size=12),
        separators=",.",
        showlegend=legend,
        hoverlabel=dict(bgcolor=INK, bordercolor=INK, font=dict(color="#fff", size=12, family=PFONT)),
        legend=dict(orientation="h", yanchor="top", y=-0.12, x=0, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        **layout,
    )
    return fig


def hbar(d: pd.DataFrame, value: str, label: str, color: str, fmt, hover_name: str, height: int = 400) -> go.Figure:
    """Bar horizontal peringkat: label di ujung batang, sumbu-x disembunyikan."""
    d = d.sort_values(value, ascending=True)
    names = d[label].tolist()
    vals = d[value].tolist()
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=names,
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=[fmt(v) for v in vals],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=11, color=TEXT),
            customdata=[[n, fmt(v)] for n, v in zip(names, vals)],
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>{hover_name}: %{{customdata[1]}}<extra></extra>",
        )
    )
    base_fig(fig, height=height, bargap=0.32)
    fig.update_xaxes(visible=False, range=[0, max(vals) * 1.28])
    fig.update_yaxes(
        tickvals=names, ticktext=[trunc(n, 30) for n in names], showgrid=False,
        automargin=True, ticks="", tickfont=dict(size=11.5, color=TEXT), linecolor=LINE,
    )
    return fig


# ======================================================================================
# DATA
# ======================================================================================
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["receipt_date"])


if not DATA_PATH.exists():
    st.error("Data belum tersedia. Jalankan dulu:  `python prepare_dashboard_data.py`")
    st.stop()

df_all = load_data(str(DATA_PATH))
df_all["price_anomaly_flag"] = df_all["price_anomaly_flag"].fillna(False).astype(bool)

trip_order = (
    df_all.dropna(subset=["receipt_date"]).sort_values("receipt_date")["trip_label"].unique().tolist()
)
_years = {t.rsplit(" ", 1)[-1] for t in trip_order}
trip_fmt = (lambda s: s.rsplit(" ", 1)[0]) if len(_years) == 1 else (lambda s: s)

# ======================================================================================
# SIDEBAR — FILTER
# ======================================================================================
def reset_filters() -> None:
    st.session_state["f_trips"] = trip_order
    st.session_state["f_brands"] = []
    st.session_state["f_products"] = []
    st.session_state["f_anom"] = False


def toggle_sidebar() -> None:
    st.session_state["sb_open"] = not st.session_state["sb_open"]


if "f_trips" not in st.session_state:
    reset_filters()
if "sb_open" not in st.session_state:
    st.session_state["sb_open"] = True

# -- lebar sidebar mengikuti state (desktop saja; di ponsel dipakai sidebar bawaan Streamlit) --
_open = st.session_state["sb_open"]
_w = "312px" if _open else "80px"
st.html(
    "<style>"
    ".st-key-sb_rail{display:none}"
    "@media (min-width:641px){"
    '[data-testid="stSidebarCollapseButton"],[data-testid="stSidebarCollapsedControl"],'
    '[data-testid="stExpandSidebarButton"],[data-testid="stSidebarResizeHandle"]{display:none !important}'
    f'section[data-testid="stSidebar"]{{width:{_w} !important;min-width:{_w} !important;max-width:{_w} !important;'
    "transform:none !important;margin-left:0 !important;visibility:visible !important}"
    'section[data-testid="stSidebar"] > div{width:100% !important}'
    f'.st-key-sb_full{{display:{"block" if _open else "none"}}}'
    f'.st-key-sb_rail{{display:{"none" if _open else "flex"};flex-direction:column;align-items:center}}'
    + ("" if _open else '[data-testid="stSidebarContent"],[data-testid="stSidebarUserContent"]{padding-left:0 !important;padding-right:0 !important;width:100% !important}'
                      '[data-testid="stSidebarUserContent"]{padding-top:.8rem !important}'
                      '.st-key-sb_rail{width:100% !important}')
    + "}</style>"
)

sb_full = st.sidebar.container(key="sb_full")
sb_rail = st.sidebar.container(key="sb_rail")

with sb_full:
    st.button("\u00a0", key="sb_collapse", icon=":material/keyboard_double_arrow_left:",
              on_click=toggle_sidebar, help="Ciutkan sidebar")
    st.html(
        '<div class="brand"><div class="logo">K</div>'
        "<div><b>Kaftet Analytics</b><span>Restock Intelligence</span></div></div>"
    )

    st.html('<div class="sb-title">Periode</div>')
    st.pills(
        "Trip belanja",
        trip_order,
        selection_mode="multi",
        format_func=trip_fmt,
        key="f_trips",
        help=(f"Tanggal belanja tahun {next(iter(_years))}. " if len(_years) == 1 else "")
        + "Kosongkan untuk menampilkan semua trip.",
    )

    st.html('<div class="sb-title">Produk</div>')
    brands_avail = sorted(df_all["brand"].dropna().unique().tolist())
    st.multiselect("Brand", brands_avail, key="f_brands", placeholder="Semua brand")

    pool = df_all if not st.session_state["f_brands"] else df_all[df_all["brand"].isin(st.session_state["f_brands"])]
    products_avail = sorted(pool["item_name"].dropna().unique().tolist())
    st.session_state["f_products"] = [p for p in st.session_state.get("f_products", []) if p in products_avail]
    st.multiselect(
        "Produk", products_avail, key="f_products", placeholder="Semua produk",
        help="Daftar menyempit sesuai brand yang dipilih.",
    )

    st.html('<div class="sb-title">Opsi Analisis</div>')
    st.toggle(
        "Kecualikan 2 baris anomali harga",
        key="f_anom",
        help="ISOPLUS COCO 350ML & PUCUK HARUM TEH MELATI. Data asli tidak diubah, hanya untuk analisis sensitivitas.",
    )

    st.html('<div style="height:6px"></div>')
    st.button("↺  Reset semua filter", on_click=reset_filters, width="stretch", key="full_reset")

# -- terapkan filter -------------------------------------------------------------------
df = df_all.copy()
if st.session_state["f_trips"]:
    df = df[df["trip_label"].isin(st.session_state["f_trips"])]
if st.session_state["f_brands"]:
    df = df[df["brand"].isin(st.session_state["f_brands"])]
if st.session_state["f_products"]:
    df = df[df["item_name"].isin(st.session_state["f_products"])]
if st.session_state["f_anom"]:
    df = df[~df["price_anomaly_flag"]]

_csv = df.to_csv(index=False).encode("utf-8") if not df.empty else b""
n_active = (
    int(0 < len(st.session_state["f_trips"]) < len(trip_order))
    + int(bool(st.session_state["f_brands"]))
    + int(bool(st.session_state["f_products"]))
    + int(bool(st.session_state["f_anom"]))
)

with sb_full:
    if not df.empty:
        st.download_button(
            "⬇  Unduh CSV terfilter", _csv, file_name="kaftet_restock_terfilter.csv",
            mime="text/csv", width="stretch", key="full_dl",
        )
    st.html(
        '<div class="sb-note"><b>Catatan metodologi</b><br>'
        "Nilai dinormalkan ke skala Rupiah penuh. <b>Qty</b> mencampur satuan kemasan (pcs vs karton), "
        "jadi bersifat indikatif.</div>"
    )

with sb_rail:
    st.html('<div class="rail-logo">K</div>')
    st.button("\u00a0", key="rail_open", icon=":material/keyboard_double_arrow_right:",
              on_click=toggle_sidebar, help="Buka sidebar")
    st.html('<div class="rail-sep"></div>')
    st.button("\u00a0", key="rail_periode", icon=":material/calendar_month:",
              on_click=toggle_sidebar, help="Filter periode")
    st.button("\u00a0", key="rail_produk", icon=":material/inventory_2:",
              on_click=toggle_sidebar, help="Filter produk")
    st.button("\u00a0", key="rail_opsi", icon=":material/tune:",
              on_click=toggle_sidebar, help="Opsi analisis")
    if n_active:
        st.html(f'<div class="rail-badge">{n_active} filter</div>')
    st.html('<div class="rail-sep"></div>')
    st.button("\u00a0", key="rail_reset", icon=":material/restart_alt:",
              on_click=reset_filters, help="Reset semua filter")
    if not df.empty:
        st.download_button("\u00a0", _csv, file_name="kaftet_restock_terfilter.csv", mime="text/csv",
                           key="rail_dl", icon=":material/download:", help="Unduh data terfilter (CSV)")

if df.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Longgarkan filter di sidebar atau tekan **Reset semua filter**.")
    st.stop()

# ======================================================================================
# METRIK TURUNAN (mengikuti filter)
# ======================================================================================
spend_total = df["total_after_rp"].sum()
n_records = len(df)
n_products = df["item_name"].nunique()
n_trips = df["receipt_date"].nunique()
n_units = df["qty"].sum()
avg_per_trip = spend_total / n_trips if n_trips else 0

active_trips = [t for t in trip_order if t in set(df["trip_label"])]
period_label = f"{active_trips[0]} s/d {active_trips[-1]}" if len(active_trips) >= 2 else active_trips[0]

by_trip = (
    df.groupby("trip_label")
    .agg(belanja=("total_after_rp", "sum"), unit=("qty", "sum"),
         catatan=("item_name", "size"), produk=("item_name", "nunique"))
    .reindex(active_trips)
)
by_trip["delta"] = by_trip["belanja"].pct_change() * 100

prod = (
    df.groupby("item_name")
    .agg(brand=("brand", "first"), belanja=("total_after_rp", "sum"), unit=("qty", "sum"),
         catatan=("item_name", "size"), trip=("receipt_date", "nunique"))
)

# ======================================================================================
# HEADER
# ======================================================================================
chips = [
    f'<span class="chip"><span class="dot"></span>{period_label}</span>',
    f'<span class="chip">{n_trips} trip belanja</span>',
]
if st.session_state["f_brands"]:
    chips.append(f'<span class="chip">Brand: {len(st.session_state["f_brands"])} dipilih</span>')
if st.session_state["f_products"]:
    chips.append(f'<span class="chip">Produk: {len(st.session_state["f_products"])} dipilih</span>')
if st.session_state["f_anom"]:
    chips.append('<span class="chip">Anomali dikecualikan</span>')
chips.append('<span class="chip warn">⚠ Data restock, bukan penjualan</span>')

st.html(
    '<div class="topbar"><div>'
    '<div class="eyebrow">Kaftet · Kafe TETI · Business Intelligence</div>'
    "<h1>Restock Analytics</h1>"
    "<p>Memahami pola belanja dan perubahan harga · Indogrosir Yogyakarta</p>"
    f'</div><div class="chips">{"".join(chips)}</div></div>'
)

# ======================================================================================
# KPI
# ======================================================================================
cards = [
    kpi("Total Pengeluaran", rupiah(spend_total), "Σ total setelah diskon", hero=True),
    kpi("Rata-rata/Trip", rp_short(avg_per_trip), "pengeluaran per hari belanja"),
    kpi("Trip Belanja", f"{n_trips}", "hari belanja tercatat"),
    kpi("Produk Unik", f"{n_products}", "nama terstandardisasi"),
    kpi("Jumlah Catatan", f"{n_records}", "baris item pada struk"),
    kpi("Total Unit", _id(n_units), "qty · kemasan campuran"),
]
st.html('<div class="kpi-grid">' + "".join(cards) + "</div>")
st.html('<div style="height:2px"></div>')

# ======================================================================================
# TABS
# ======================================================================================
tab_ov, tab_prod, tab_price, tab_dq = st.tabs(
    ["Ringkasan Eksekutif", "Kinerja Produk", "Intelijen Harga", "Kualitas Data & Insight"]
)

# --------------------------------------------------------------------------------------
# TAB 1 — RINGKASAN
# --------------------------------------------------------------------------------------
with tab_ov:
    c1, c2 = st.columns([1.5, 1], gap="medium")

    with c1.container(key="card_trip"):
        card_head("Pengeluaran Restock per Trip", "Total setelah diskon (Rp) · garis putus-putus = rata-rata per trip")
        bt = by_trip.reset_index()
        fig = go.Figure(
            go.Bar(
                x=bt["trip_label"], y=bt["belanja"],
                marker=dict(color=PRIMARY, line=dict(width=0)),
                text=[rp_short(v) for v in bt["belanja"]], textposition="outside", cliponaxis=False,
                textfont=dict(size=12, color=INK),
                customdata=[[rupiah(b), _id(u), c, p] for b, u, c, p in zip(bt["belanja"], bt["unit"], bt["catatan"], bt["produk"])],
                hovertemplate=("<b>%{x}</b><br>Belanja: %{customdata[0]}<br>Catatan: %{customdata[2]}"
                               "<br>Produk unik: %{customdata[3]}<br>Unit: %{customdata[1]}<extra></extra>"),
            )
        )
        base_fig(fig, height=330, bargap=0.45)
        if len(bt) > 1:
            fig.add_hline(y=avg_per_trip, line=dict(color=MUTED, width=1.2, dash="dash"))
        fig.update_xaxes(showgrid=False, linecolor=LINE, ticks="", type="category", categoryorder="array",
                         categoryarray=active_trips, tickfont=dict(size=12))
        fig.update_yaxes(visible=False, range=[0, bt["belanja"].max() * 1.2])
        st.plotly_chart(fig, width="stretch", config=PCFG)

    with c2.container(key="card_brand"):
        card_head("Distribusi Belanja per Brand", "Enam brand teratas + lainnya")
        bs = df.groupby("brand")["total_after_rp"].sum().sort_values(ascending=False)
        top = bs.head(6)
        if bs.iloc[6:].sum() > 0:
            top = pd.concat([top, pd.Series({"Lainnya": bs.iloc[6:].sum()})])
        slice_colors = PALETTE[:6] + ["#CBD5E1"] if "Lainnya" in top.index else PALETTE[: len(top)]
        fig = go.Figure(
            go.Pie(
                labels=[f"{b}  ·  {v / top.sum() * 100:.0f}%" for b, v in zip(top.index, top.values)],
                values=top.values, hole=0.62, sort=False, direction="clockwise",
                domain=dict(x=[0, 0.56]),
                marker=dict(colors=slice_colors[: len(top)], line=dict(color="white", width=2)),
                textinfo="none",
                customdata=[rupiah(v) for v in top.values],
                hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
            )
        )
        base_fig(fig, height=330, legend=True)
        fig.update_layout(
            legend=dict(orientation="v", x=0.62, y=0.5, yanchor="middle", font=dict(size=11.5, color=TEXT)),
            annotations=[dict(text=f"<b>{rp_short(spend_total)}</b>",
                              x=0.28, y=0.5, showarrow=False, font=dict(size=12, color=INK, family=PFONT))],
        )
        st.plotly_chart(fig, width="stretch", config=PCFG)

    with st.container(key="card_trip_tbl"):
        card_head("Ringkasan per Trip", "Perubahan dibandingkan trip sebelumnya dalam periode terpilih")
        t = by_trip.reset_index()
        tbl = pd.DataFrame({
            "Trip": t["trip_label"],
            "Catatan": t["catatan"].astype(int).astype(str),
            "Total Unit": [_id(v) for v in t["unit"]],
            "Pengeluaran": [rupiah(v) for v in t["belanja"]],
            "% Share": [f"{_id(v / spend_total * 100, 1)}%" for v in t["belanja"]],
            "Δ vs Trip Sebelumnya": [pct_html(v) for v in t["delta"]],
        })
        al = {c: "r" for c in tbl.columns if c != "Trip"}
        st.html(table_html(tbl, al, raw=("Δ vs Trip Sebelumnya",)))

# --------------------------------------------------------------------------------------
# TAB 2 — PRODUK
# --------------------------------------------------------------------------------------
with tab_prod:
    st.html(
        '<div class="callout"><b>Perhatikan:</b> frekuensi, kuantitas, dan belanja adalah tiga metrik berbeda dan '
        "tidak dapat dipertukarkan. Semuanya mengukur <b>pembelian</b>, bukan penjualan.</div>"
    )
    p1, p2 = st.columns([1.5, 1], gap="medium")

    with p1.container(key="card_rank"):
        card_head("10 Produk Teratas", "Pilih metrik untuk mengganti peringkat")
        metric = st.segmented_control(
            "Metrik", ["Belanja", "Frekuensi Restock", "Kuantitas"], default="Belanja",
            key="rank_metric", label_visibility="collapsed",
        ) or "Belanja"
        cfg = {
            "Belanja": ("belanja", PRIMARY, rupiah, "Belanja"),
            "Frekuensi Restock": ("catatan", INK, lambda v: f"{int(v)}×", "Jumlah catatan (bukan jumlah terjual)"),
            "Kuantitas": ("unit", "#2B8A6E", lambda v: _id(v), "Total unit (kemasan campuran)"),
        }
        col, colr, fmt, hname = cfg[metric]
        d = prod.sort_values([col, "belanja"], ascending=False).head(10).reset_index()
        st.plotly_chart(hbar(d, col, "item_name", colr, fmt, hname, height=400), width="stretch", config=PCFG)

    with p2.container(key="card_recur"):
        card_head("Keberulangan Produk antar Trip", "Berapa banyak produk dibeli di 1, 2, … trip")
        rec = prod["trip"].value_counts().sort_index()
        share = rec / rec.sum() * 100
        fig = go.Figure(
            go.Bar(
                x=[f"{i} trip" for i in rec.index], y=rec.values,
                marker=dict(color=PRIMARY_2, line=dict(width=0)),
                text=[str(v) for v in rec.values], textposition="outside", cliponaxis=False,
                textfont=dict(size=12, color=INK),
                customdata=[f"{_id(s, 1)}%" for s in share.values],
                hovertemplate="Dibeli di %{x}<br>%{y} produk (%{customdata})<extra></extra>",
            )
        )
        base_fig(fig, height=452, bargap=0.4)
        fig.update_xaxes(showgrid=False, linecolor=LINE, ticks="", tickfont=dict(size=12))
        fig.update_yaxes(visible=False, range=[0, rec.max() * 1.18])
        st.plotly_chart(fig, width="stretch", config=PCFG)

    with st.container(key="card_prod_tbl"):
        card_head("Detail Produk", "Seluruh produk pada filter aktif. Klik judul kolom untuk mengurutkan, ikon kaca pembesar untuk mencari")
        pt = prod.reset_index().rename(columns={
            "item_name": "Produk", "brand": "Brand", "trip": "Trip", "catatan": "Catatan",
            "unit": "Unit", "belanja": "Belanja (Rp)"})
        pt = pt[["Produk", "Brand", "Trip", "Catatan", "Unit", "Belanja (Rp)"]].sort_values("Belanja (Rp)", ascending=False)
        pt["Unit"] = pt["Unit"].round().astype(int)
        sty = pt.style.format({"Belanja (Rp)": rupiah, "Unit": "{:d}"})
        st.dataframe(sty, hide_index=True, width="stretch", height=370)

# --------------------------------------------------------------------------------------
# TAB 3 — HARGA
# --------------------------------------------------------------------------------------
price_src = df[~df["price_anomaly_flag"]]
phist = price_src.groupby(["item_name", "trip_label", "receipt_date"])["unit_price_rp"].mean().reset_index()
pstats = phist.groupby("item_name")["unit_price_rp"].agg(n_trip="count", harga_min="min", harga_max="max", harga_avg="mean")
pstats = pstats[pstats["n_trip"] >= 2].copy()
pstats["rentang"] = pstats["harga_max"] - pstats["harga_min"]

fl = (
    phist.sort_values("receipt_date").groupby("item_name")["unit_price_rp"]
    .agg(harga_awal="first", harga_akhir="last")
    .reindex(pstats.index)
)
fl["pct"] = (fl["harga_akhir"] / fl["harga_awal"] - 1) * 100

with tab_price:
    st.html(
        '<div class="callout">Harga satuan sudah dinormalkan ke Rupiah. Baris anomali harga ditandai dan '
        "<b>dikecualikan</b> dari analisis pada tab ini. Hanya produk yang dibeli di ≥2 trip yang dapat dibandingkan.</div>"
    )
    h1, h2 = st.columns([1.4, 1], gap="medium")

    with h1.container(key="card_trend"):
        card_head("Tren Harga Satuan antar Trip", "Pilih hingga 6 produk untuk dibandingkan")
        opts = sorted(pstats.index.tolist())
        default_watch = [p for p in ["SPRITE PET 390 ML", "ISOPLUS BTL 350ML", "MILKU SUSU STRO 200", "COCA COLA PET 390 ML"] if p in opts]
        if st.session_state["f_products"]:
            default_watch = [p for p in st.session_state["f_products"] if p in opts][:6]
        watch = st.multiselect("Produk dipantau", opts, default=default_watch, max_selections=6,
                               placeholder="Pilih produk…", label_visibility="collapsed")
        if watch:
            fig = go.Figure()
            for i, name in enumerate(watch):
                s = phist[phist["item_name"] == name].sort_values("receipt_date")
                fig.add_trace(go.Scatter(
                    x=s["trip_label"], y=s["unit_price_rp"], mode="lines+markers", name=trunc(name, 26),
                    line=dict(color=PALETTE[i % len(PALETTE)], width=2.6), marker=dict(size=8),
                    customdata=[rupiah(v) for v in s["unit_price_rp"]],
                    hovertemplate=f"<b>{esc(name)}</b><br>%{{x}}<br>Harga: %{{customdata}}<extra></extra>",
                ))
            base_fig(fig, height=340, legend=True)
            fig.update_xaxes(categoryorder="array", categoryarray=active_trips, type="category",
                             showgrid=False, linecolor=LINE, ticks="")
            fig.update_yaxes(gridcolor=LINE, zeroline=False, tickprefix="Rp", tickformat=",.0f", tickfont=dict(size=11, color=MUTED))
            st.plotly_chart(fig, width="stretch", config=PCFG)
        else:
            st.html('<div class="empty">Pilih produk yang dibeli di ≥2 trip untuk melihat tren harga.</div>')

    with h2.container(key="card_movers"):
        card_head("Perubahan Harga Terbesar", "Trip pertama → terakhir (%) · hanya produk yang berubah")
        ch = fl[fl["pct"].abs() >= 0.05]
        movers = pd.concat([ch.sort_values("pct", ascending=False).head(5), ch.sort_values("pct").head(5)])
        movers = movers[~movers.index.duplicated()].sort_values("pct")
        if len(movers):
            names = movers.index.tolist()
            vals = movers["pct"].tolist()
            fig = go.Figure(go.Bar(
                x=vals, y=names, orientation="h",
                marker=dict(color=[UP if v > 0 else DOWN for v in vals], line=dict(width=0)),
                text=[f"{'+' if v > 0 else '−'}{_id(abs(v), 1)}%" for v in vals],
                textposition="outside", cliponaxis=False, textfont=dict(size=11, color=TEXT),
                customdata=[[n, rupiah(a), rupiah(b)] for n, a, b in zip(names, movers["harga_awal"], movers["harga_akhir"])],
                hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} → %{customdata[2]}<extra></extra>",
            ))
            base_fig(fig, height=400, bargap=0.35)
            lim = max(abs(min(vals)), abs(max(vals))) * 1.35
            fig.update_xaxes(visible=False, range=[-lim, lim * 1.3])
            fig.update_yaxes(tickvals=names, ticktext=[trunc(n, 24) for n in names], showgrid=False, automargin=True,
                             ticks="", tickfont=dict(size=11, color=TEXT), linecolor=MUTED)
            st.plotly_chart(fig, width="stretch", config=PCFG)
            st.html(f'<div style="font-size:.74rem;color:{MUTED}"><span class="up">■</span> harga naik &nbsp; <span class="down">■</span> harga turun</div>')
        else:
            st.html('<div class="empty">Tidak ada perubahan harga pada filter ini.</div>')

    with st.container(key="card_price_tbl"):
        card_head("Harga Min / Maks / Rata-rata per Produk", "12 produk dengan rentang harga terbesar · produk dengan ≥2 trip")
        show = pstats[pstats["rentang"] > 0].sort_values("rentang", ascending=False).head(12)
        if len(show):
            tt = pd.DataFrame({
                "Produk": show.index,
                "Trip": show["n_trip"].astype(int).astype(str).values,
                "Harga Min": [rupiah(v) for v in show["harga_min"]],
                "Harga Maks": [rupiah(v) for v in show["harga_max"]],
                "Rata-rata": [rupiah(v) for v in show["harga_avg"]],
                "Rentang": [rupiah(v) for v in show["rentang"]],
                "Rentang %": [pct_html(r / mn * 100) for r, mn in zip(show["rentang"], show["harga_min"])],
            })
            al = {c: "r" for c in tt.columns if c != "Produk"}
            st.html(table_html(tt, al, raw=("Rentang %",)))
        else:
            st.html('<div class="empty">Tidak ada produk dengan variasi harga pada filter ini.</div>')

# --------------------------------------------------------------------------------------
# TAB 4 — KUALITAS DATA & INSIGHT
# --------------------------------------------------------------------------------------
with tab_dq:
    q1, q2 = st.columns([1, 1.25], gap="medium")

    with q1.container(key="card_missing"):
        card_head("Kolom Opsional yang Sering Kosong", "% nilai kosong · seluruh dataset (tidak terpengaruh filter)")
        miss = (
            df_all[["discount", "profit", "sisa", "rusak", "receipt_time_raw", "transaction_no"]]
            .isna().mean().mul(100).round(1).sort_values(ascending=True)
        )
        names = miss.index.tolist()
        fig = go.Figure(go.Bar(
            x=miss.values, y=names, orientation="h",
            marker=dict(color=[AMBER if v >= 50 else PRIMARY_2 for v in miss.values], line=dict(width=0)),
            text=[f"{_id(v, 1)}%" for v in miss.values], textposition="outside", cliponaxis=False,
            textfont=dict(size=11, color=TEXT),
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% kosong<extra></extra>",
        ))
        base_fig(fig, height=322, bargap=0.38)
        fig.update_xaxes(visible=False, range=[0, 112])
        fig.update_yaxes(showgrid=False, ticks="", automargin=True, tickfont=dict(size=11.5, color=TEXT), linecolor=LINE)
        st.plotly_chart(fig, width="stretch", config=PCFG)
        st.html(f'<div style="font-size:.74rem;color:{MUTED}"><span style="color:{AMBER}">■</span> ≥50% kosong: membatasi analisis margin / transaksi</div>')

    n_anom = int(df_all["price_anomaly_flag"].sum())
    n_thousands = int(df_all["price_scale_flag"].astype(str).str.startswith("thousands").sum())
    with q2.container(key="card_qc"):
        card_head("Daftar Periksa Kualitas Data", "Anomali dipertahankan, data asli tidak diubah")
        qc = pd.DataFrame({
            "Pemeriksaan": [
                "Format tanggal campuran (dd-mm-yyyy vs dd-mm-yy)",
                "Skala moneter campuran (ribuan / desimal)",
                "Selisih harga vs total (ISOPLUS COCO, PUCUK HARUM)",
                "Satuan qty campuran (pcs vs karton)",
                "Nomor transaksi kosong (sheet 18-Sep)",
            ],
            "Status": ['<span class="pill warn">Ditandai</span>'] * 5,
            "Dampak": [
                "Diparse dayfirst; kolom asli disimpan",
                f"{n_thousands} baris dinormalkan ke Rp",
                f"{n_anom} baris dipertahankan untuk ditinjau",
                "‘Total unit’ bersifat indikatif",
                "Analisis per-transaksi terbatas",
            ],
        })
        st.html(table_html(qc, raw=("Status",)))

    with st.container(key="card_anom"):
        card_head("Baris yang Ditandai untuk Ditinjau Manual", "Data asli tidak diubah. Konfirmasi ke struk fisik sebelum dipakai untuk penganggaran")
        an = df_all[df_all["price_anomaly_flag"]]
        if len(an):
            at = pd.DataFrame({
                "Sheet": an["source_sheet"].values,
                "Tanggal": an["receipt_date_raw"].values,
                "Produk": an["item_name"].values,
                "Qty": [_id(v) for v in an["qty"]],
                "Harga Satuan": [rupiah(v) for v in an["unit_price_rp"]],
                "Total Asli": [_id(v, 0) if float(v).is_integer() else _id(v, 1) for v in an["total_after_discount"]],
                "Total (Rp)": [rupiah(v) for v in an["total_after_rp"]],
            })
            al = {c: "r" for c in ["Qty", "Harga Satuan", "Total Asli", "Total (Rp)"]}
            st.html(table_html(at, al))
        else:
            st.html('<div class="empty">Tidak ada baris anomali.</div>')

    # ---------------- insight dinamis (dihitung dari data terfilter) ----------------
    section("Insight Bisnis")
    spend_by_prod = prod["belanja"].sort_values(ascending=False)
    top10_share = spend_by_prod.head(10).sum() / spend_total * 100 if spend_total else 0
    n_top10 = min(10, len(spend_by_prod))
    always = prod[prod["trip"] == n_trips].index.tolist() if n_trips >= 3 else []
    single = int((prod["trip"] == 1).sum())
    peak_trip = by_trip["belanja"].idxmax()
    peak_share = by_trip["belanja"].max() / spend_total * 100 if spend_total else 0
    stable = int((pstats["rentang"] == 0).sum())

    findings = [
        f"<b>Belanja terkonsentrasi:</b> {n_top10} produk teratas menyumbang <b>{_id(top10_share, 0)}%</b> dari total pengeluaran "
        f"({n_products} produk unik).",
        f"<b>Mayoritas ad-hoc:</b> {single} dari {n_products} produk ({_id(single / n_products * 100, 0)}%) hanya dibeli di satu trip.",
    ]
    if always:
        findings.append(
            f"<b>Produk staple:</b> {len(always)} produk hadir di seluruh {n_trips} trip: "
            + ", ".join(trunc(a, 26) for a in always[:3]) + "."
        )
    if n_trips >= 2:
        findings.append(f"<b>Trip terbesar:</b> {peak_trip} ({rp_short(by_trip['belanja'].max())}, {_id(peak_share, 0)}% dari total).")
    if len(pstats):
        findings.append(
            f"<b>Harga relatif stabil:</b> {stable} dari {len(pstats)} produk berulang tidak berubah harga; "
            "sisanya bergeser kecil. Baris anomali adalah masalah pencatatan, bukan perubahan harga nyata."
        )

    recs = [
        "Tetapkan <b>daftar beli tetap</b> untuk produk staple dengan target kuantitas per trip.",
        "Konfirmasi <b>2 baris anomali</b> ke struk fisik sebelum dipakai untuk penganggaran.",
        "Seragamkan <b>format tanggal &amp; skala harga</b> pada input struk agar data konsisten.",
        "Catat <b>penjualan</b> secara terpisah bila ingin menganalisis permintaan dan margin.",
    ]
    i1, i2 = st.columns(2, gap="medium")
    with i1.container(key="card_findings"):
        card_head("Temuan Ringkas", "Dihitung otomatis dari data pada filter aktif")
        st.html('<ul class="ins">' + "".join(f"<li>{f}</li>" for f in findings) + "</ul>")
    with i2.container(key="card_recs"):
        card_head("Rekomendasi Praktis")
        st.html('<ul class="ins rec">' + "".join(f"<li>{r}</li>" for r in recs) + "</ul>")

    st.html(
        '<div class="callout"><b>Batasan:</b> ini data <b>restock/pembelian</b>, bukan penjualan. Dengan hanya 5 trip '
        "yang jaraknya tidak teratur, dashboard ini <b>tidak</b> meramalkan permintaan atau penjualan, dan produk yang "
        "tidak muncul di suatu trip tidak berarti permintaannya nol.</div>"
    )

# ======================================================================================
# FOOTER
# ======================================================================================
st.html(
    '<div class="foot"><b>Kaftet Restock Analytics</b>'
    "<span>Sumber: Struk_Indogrosir_restock_18_April_2026.xlsx · 5 struk, 2026</span>"
    "<span>Nilai dinormalkan ke Rupiah penuh</span>"
    "<span>Streamlit + Plotly</span></div>"
)
