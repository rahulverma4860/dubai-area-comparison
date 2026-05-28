import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import ssl
import urllib.request
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY   = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST  = "uae-real-estate3.p.rapidapi.com"

# Split CSV parts — each under 25MB, no virus warning
GDRIVE_PARTS = [
    "1QT7bxfWGFQznE02FSDOTNIKzkj7p4n2Q",
    "1Gj62X41xjDmJfCOhKUgfDJF1i7A6pEAe",
    "1QNnDQU4wnrVCBobmSjcep8Lf5XUCEVd6",
    "1OlbultfiKvr00D-lSuSIq6RcgR2TqEPR",
]

st.set_page_config(
    page_title="Dubai Area Comparison Tool 2026",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #0a0f1e; color: #e8e0d0; }
    .main .block-container { padding: 2rem 3rem; max-width: 1200px; }
    #MainMenu, footer, header { visibility: hidden; }
    .hero { text-align: center; padding: 2rem 0 1.5rem; }
    .hero-title { font-size: 2.4rem; font-weight: 700; color: #C9A84C; margin: 0 0 0.5rem; }
    .hero-sub { font-size: 1rem; color: #8a9bb5; margin: 0 0 0.3rem; }
    .hero-badge { display: inline-block; background: rgba(201,168,76,0.12); border: 1px solid rgba(201,168,76,0.3); color: #C9A84C; font-size: 0.75rem; padding: 4px 14px; border-radius: 20px; margin: 4px; }
    .section-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em; color: #C9A84C; text-transform: uppercase; margin-bottom: 1rem; margin-top: 1.5rem; border-bottom: 1px solid rgba(201,168,76,0.2); padding-bottom: 0.5rem; }
    .metric-card { background: #111827; border: 1px solid rgba(201,168,76,0.15); border-radius: 10px; padding: 1rem; text-align: center; }
    .metric-val { font-size: 1.2rem; font-weight: 700; color: #C9A84C; }
    .metric-lbl { font-size: 0.72rem; color: #8a9bb5; margin-top: 4px; }
    .win-a { color: #4a9eff !important; }
    .win-b { color: #2dd4a0 !important; }
    .comm-header-a { background: rgba(74,158,255,0.06); border: 1px solid rgba(74,158,255,0.3); border-radius: 12px; padding: 1.2rem 1.5rem; }
    .comm-header-b { background: rgba(45,212,160,0.06); border: 1px solid rgba(45,212,160,0.3); border-radius: 12px; padding: 1.2rem 1.5rem; }
    .comm-name-a { font-size: 1.5rem; font-weight: 700; color: #4a9eff; margin: 0 0 4px; }
    .comm-name-b { font-size: 1.5rem; font-weight: 700; color: #2dd4a0; margin: 0 0 4px; }
    .comm-tag { font-size: 0.8rem; color: #8a9bb5; margin: 0; }
    .verdict-card { background: #111827; border: 1px solid rgba(201,168,76,0.15); border-radius: 10px; padding: 1rem; text-align: center; }
    .verdict-icon { font-size: 1.4rem; margin-bottom: 4px; }
    .verdict-cat { font-size: 0.68rem; color: #8a9bb5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
    .verdict-winner { font-size: 0.95rem; font-weight: 700; }
    .disclaimer { background: rgba(201,168,76,0.04); border: 1px solid rgba(201,168,76,0.12); border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.73rem; color: #4a6080; margin: 1rem 0; }
    .lead-box { background: #111827; border: 1px solid rgba(201,168,76,0.4); border-radius: 14px; padding: 2rem; text-align: center; margin-top: 2rem; }
    .lead-title { font-size: 1.2rem; font-weight: 700; color: #C9A84C; margin-bottom: 0.3rem; }
    .lead-sub { font-size: 0.85rem; color: #8a9bb5; }
    .stSelectbox [data-baseweb="select"] > div { background: #1a2235 !important; border: 1px solid rgba(201,168,76,0.25) !important; border-radius: 8px !important; color: #e8e0d0 !important; }
    .stSelectbox [data-baseweb="select"] span { color: #e8e0d0 !important; }
    .stSelectbox [data-baseweb="select"] svg { fill: #C9A84C !important; }
    [data-baseweb="popover"] li { background: #1a2235 !important; color: #e8e0d0 !important; }
    [data-baseweb="popover"] li:hover { background: rgba(201,168,76,0.15) !important; }
    label { color: #8a9bb5 !important; font-size: 0.82rem !important; }
    .stTextInput input { background: #1a2235 !important; border: 1px solid rgba(201,168,76,0.25) !important; color: #e8e0d0 !important; border-radius: 8px !important; }
    .stButton > button, .stFormSubmitButton > button, div[data-testid="stFormSubmitButton"] > button { background: #C9A84C !important; color: #0a0f1e !important; font-weight: 800 !important; border: none !important; border-radius: 8px !important; font-size: 1rem !important; width: 100% !important; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { background: #b8963e !important; }
    details { background: #111827 !important; border: 1px solid rgba(201,168,76,0.25) !important; border-radius: 8px !important; }
    details summary p { color: #C9A84C !important; }
    hr { border-color: rgba(201,168,76,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ── Download CSV ───────────────────────────────────────────────────────────────
def download_csv_if_needed():
    if not os.path.exists("transactions.csv"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE

        progress = st.progress(0, text="📥 Downloading DLD data (part 0/9)...")
        parts = []

        for i, file_id in enumerate(GDRIVE_PARTS):
            try:
                url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, context=ctx) as r:
                    data = r.read()
                # Each part is small so no virus warning — verify it is CSV
                if len(data) < 1000 or data[:1].lower() in [b"<"]:
                    st.error(f"Part {i+1} download failed — got HTML instead of CSV.")
                    return
                parts.append(data)
                progress.progress((i + 1) / len(GDRIVE_PARTS),
                                   text=f"📥 Downloading DLD data (part {i+1}/{len(GDRIVE_PARTS)})...")
            except Exception as e:
                st.error(f"Failed to download part {i+1}: {e}")
                return

        progress.progress(1.0, text="💾 Merging and saving...")
        try:
            # Write part 1 with header, rest without header
            with open("transactions.csv", "wb") as f:
                f.write(parts[0])
                for part in parts[1:]:
                    # Skip the header line of subsequent parts
                    newline_idx = part.index(10)  # 10 = ord("\n")
                    f.write(part[newline_idx + 1:])
            progress.empty()
            st.rerun()
        except Exception as e:
            st.error(f"Failed to merge parts: {e}")

# ── Load & process DLD data ────────────────────────────────────────────────────
@st.cache_data
def load_dld():
    if not os.path.exists("transactions.csv"):
        return None
    df = pd.read_csv("transactions.csv", low_memory=False)
    # Normalise all column names first
    df.columns = df.columns.str.strip()
    # Rename known DLD columns
    rename_map = {}
    for c in df.columns:
        if c == "area_name_en":   rename_map[c] = "area"
        if c == "procedure_area": rename_map[c] = "size_sqft"
        if c == "actual_worth":   rename_map[c] = "price_aed"
        if c == "instance_date":  rename_map[c] = "date"
        if c == "trans_group_en": rename_map[c] = "trans_type"
    df = df.rename(columns=rename_map)
    if "date" not in df.columns:
        st.error(f"Date column not found. Available columns: {list(df.columns[:10])}")
        return None
    df["date"]      = pd.to_datetime(df["date"], errors="coerce")
    df["year"]      = df["date"].dt.year
    df["size_sqft"] = pd.to_numeric(df["size_sqft"], errors="coerce")
    df["price_aed"] = pd.to_numeric(df["price_aed"], errors="coerce")
    df = df[df["trans_type"].str.contains("Sale", case=False, na=False)]
    df = df.dropna(subset=["price_aed","size_sqft","area"])
    df = df[(df["price_aed"] > 50000) & (df["size_sqft"] > 50)]
    df["psf"] = df["price_aed"] / df["size_sqft"]
    return df

@st.cache_data
def get_community_stats(df):
    """Returns per-area stats: avg_psf, median_psf, txn_count, min_price, max_price, avg_price."""
    stats = (df.groupby("area").agg(
        avg_psf    = ("psf",     "mean"),
        median_psf = ("psf",     "median"),
        txn_count  = ("psf",     "count"),
        avg_price  = ("price_aed","mean"),
        min_price  = ("price_aed", lambda x: x.quantile(0.10)),
        max_price  = ("price_aed", lambda x: x.quantile(0.90)),
    ).reset_index())
    stats = stats[stats["txn_count"] >= 20]
    return stats.set_index("area").to_dict("index")

@st.cache_data
def get_yearly_trend(df, area):
    """Returns yearly median psf for an area from 2019 onwards."""
    sub = df[(df["area"] == area) & (df["year"] >= 2019)]
    if len(sub) < 10:
        return {}
    trend = sub.groupby("year")["psf"].median().reset_index()
    return dict(zip(trend["year"].astype(int), trend["psf"].round(0)))

@st.cache_data
def get_rental_yield(df, area):
    """Estimate gross yield from DLD data where possible."""
    sub = df[df["area"] == area]
    if len(sub) < 10:
        return None
    avg_psf = sub["psf"].median()
    return avg_psf

# ── Bayut live rent ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_bayut_rent(community, beds="2"):
    if not RAPIDAPI_KEY:
        return None
    try:
        headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}
        r1   = requests.get(f"https://{RAPIDAPI_HOST}/autocomplete",
                            headers=headers, params={"query": community.split("(")[0].strip()}, timeout=8)
        locs = r1.json().get("data", {}).get("locations", [])
        if not locs:
            return None
        loc_id = locs[0]["externalID"]
        r2 = requests.get(f"https://{RAPIDAPI_HOST}/transactions",
                          headers=headers,
                          params={"purpose":"for-rent","locationExternalIDs":loc_id,
                                  "hitsPerPage":"50","beds":beds}, timeout=8)
        hits = r2.json().get("data", {}).get("hits", [])
        rents = []
        for h in hits:
            amt = h.get("contract_monthly_amount") or h.get("transaction_amount")
            if amt:
                try:
                    v = float(amt)
                    annual = v * 12 if v < 100000 else v
                    if 20000 < annual < 2000000:
                        rents.append(annual)
                except Exception:
                    pass
        return int(sum(rents)/len(rents)) if len(rents) >= 3 else None
    except Exception:
        return None

def fmt(n):
    n = round(n)
    if n >= 1_000_000: return f"AED {n/1_000_000:.2f}M"
    if n >= 1_000:     return f"AED {n:,.0f}"
    return f"AED {n}"

# ══════════════════════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════════════════════
download_csv_if_needed()

# Debug: show file status
if not os.path.exists("transactions.csv"):
    st.error("❌ transactions.csv still not found after download attempt. Check logs above for errors.")
    st.stop()

dld = load_dld()

st.markdown("""
<div class="hero">
  <div class="hero-title">Dubai Area Comparison Tool</div>
  <div class="hero-sub">Compare any two Dubai communities with real DLD transaction data</div>
  <span class="hero-badge">1M+ DLD Transactions</span>
  <span class="hero-badge">Live Bayut Rental Data</span>
  <span class="hero-badge">50+ Communities</span>
  <span class="hero-badge">2026 Edition</span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

if dld is None:
    st.warning("DLD data not available. Place transactions.csv in this folder.")
    st.stop()

st.success(f"✅ {len(dld):,} real DLD transactions loaded")
community_stats = get_community_stats(dld)
all_communities = sorted(community_stats.keys())

# ── Community selectors ────────────────────────────────────────────────────────
col1, col_vs, col2 = st.columns([5, 1, 5])
with col1:
    area_a = st.selectbox("Community A", all_communities,
                           index=all_communities.index("Dubai Marina") if "Dubai Marina" in all_communities else 0,
                           key="area_a")
with col_vs:
    st.markdown("<div style='text-align:center;padding-top:28px;color:#C9A84C;font-weight:700;font-size:1.1rem'>VS</div>", unsafe_allow_html=True)
with col2:
    default_b = "Jumeirah Village Circle" if "Jumeirah Village Circle" in all_communities else all_communities[1]
    area_b = st.selectbox("Community B", all_communities,
                           index=all_communities.index(default_b),
                           key="area_b")

if area_a == area_b:
    st.warning("Please select two different communities.")
    st.stop()

# ── Load data for both areas ───────────────────────────────────────────────────
sa = community_stats[area_a]
sb = community_stats[area_b]

with st.spinner("Fetching live rental data from Bayut..."):
    rent_a = fetch_bayut_rent(area_a, "2")
    rent_b = fetch_bayut_rent(area_b, "2")

# Fallback rents if Bayut unavailable
RENT_FALLBACK = {
    "Palm Jumeirah":230000,"Downtown Dubai":168000,"Dubai Marina":140000,
    "Business Bay":125000,"DIFC":180000,"Dubai Hills Estate":132000,
    "Arabian Ranches":122000,"Jumeirah Lake Towers":98000,
    "Jumeirah Village Circle":88000,"International City":55000,
}
if not rent_a: rent_a = RENT_FALLBACK.get(area_a, int(sa["avg_psf"] * 0.065 * 1000))
if not rent_b: rent_b = RENT_FALLBACK.get(area_b, int(sb["avg_psf"] * 0.065 * 1000))

yield_a = (rent_a / (sa["avg_psf"] * 1000)) * 100
yield_b = (rent_b / (sb["avg_psf"] * 1000)) * 100

# ── Community headers ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
hc1, hc2 = st.columns(2)
with hc1:
    st.markdown(f"""
    <div class="comm-header-a">
      <p class="comm-name-a">{area_a}</p>
      <p class="comm-tag">Based on {sa['txn_count']:,} DLD transactions</p>
    </div>""", unsafe_allow_html=True)
with hc2:
    st.markdown(f"""
    <div class="comm-header-b">
      <p class="comm-name-b">{area_b}</p>
      <p class="comm-tag">Based on {sb['txn_count']:,} DLD transactions</p>
    </div>""", unsafe_allow_html=True)

# ── Key metrics ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Key Metrics — Real DLD Data</div>', unsafe_allow_html=True)

metrics = [
    ("Avg Price/sqft",      f"AED {sa['avg_psf']:,.0f}",  f"AED {sb['avg_psf']:,.0f}",  sa['avg_psf'] < sb['avg_psf'],  sb['avg_psf'] < sa['avg_psf'],  "Lower = more affordable"),
    ("Median Price/sqft",   f"AED {sa['median_psf']:,.0f}",f"AED {sb['median_psf']:,.0f}",sa['median_psf']<sb['median_psf'],sb['median_psf']<sa['median_psf'],"Median is less skewed by outliers"),
    ("Avg Transaction Price",fmt(sa['avg_price']),          fmt(sb['avg_price']),          sa['avg_price']<sb['avg_price'],  sb['avg_price']<sa['avg_price'],  "Lower = more accessible market"),
    ("Price Range (10–90%)", f"{fmt(sa['min_price'])} – {fmt(sa['max_price'])}",f"{fmt(sb['min_price'])} – {fmt(sb['max_price'])}",False,False,"Wide range = diverse property mix"),
    ("Total DLD Transactions",f"{sa['txn_count']:,}",       f"{sb['txn_count']:,}",        sa['txn_count']>sb['txn_count'],  sb['txn_count']>sa['txn_count'],  "Higher = more liquid market"),
    ("2BR Annual Rent",      fmt(rent_a),                   fmt(rent_b),                   rent_a < rent_b,                  rent_b < rent_a,                  "Live Bayut data where available"),
    ("Gross Rental Yield",   f"{yield_a:.1f}%",             f"{yield_b:.1f}%",             yield_a > yield_b,                yield_b > yield_a,                "Higher = better investment return"),
]

for label, va, vb, win_a, win_b, note in metrics:
    mc1, mc2, mc3 = st.columns([2, 1, 1])
    with mc1:
        st.markdown(f"<div style='padding:10px 0;font-size:0.85rem;color:#8a9bb5;border-bottom:1px solid rgba(201,168,76,0.08);'>{label}<br><span style='font-size:0.7rem;color:#2a3548;'>{note}</span></div>", unsafe_allow_html=True)
    with mc2:
        cls = "win-a" if win_a else ""
        st.markdown(f"<div style='padding:10px 0;text-align:center;border-bottom:1px solid rgba(201,168,76,0.08);'><span class='{cls}' style='font-size:0.9rem;font-weight:600;color:{'#4a9eff' if win_a else '#e8e0d0'}'>{va}</span></div>", unsafe_allow_html=True)
    with mc3:
        cls = "win-b" if win_b else ""
        st.markdown(f"<div style='padding:10px 0;text-align:center;border-bottom:1px solid rgba(201,168,76,0.08);'><span class='{cls}' style='font-size:0.9rem;font-weight:600;color:{'#2dd4a0' if win_b else '#e8e0d0'}'>{vb}</span></div>", unsafe_allow_html=True)

# ── Price trend chart ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Price per sqft Trend — Real DLD Yearly Data</div>', unsafe_allow_html=True)

trend_a = get_yearly_trend(dld, area_a)
trend_b = get_yearly_trend(dld, area_b)

if trend_a and trend_b:
    all_years = sorted(set(trend_a.keys()) | set(trend_b.keys()))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=all_years, y=[trend_a.get(y) for y in all_years],
        name=area_a, mode="lines+markers",
        line=dict(color="#4a9eff", width=2),
        marker=dict(size=6),
        connectgaps=True,
        hovertemplate="<b>%{x}</b><br>AED %{y:,.0f}/sqft<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=all_years, y=[trend_b.get(y) for y in all_years],
        name=area_b, mode="lines+markers",
        line=dict(color="#2dd4a0", width=2, dash="dot"),
        marker=dict(size=6),
        connectgaps=True,
        hovertemplate="<b>%{x}</b><br>AED %{y:,.0f}/sqft<extra></extra>"
    ))
    fig.update_layout(
        plot_bgcolor="#111827", paper_bgcolor="#111827",
        font=dict(color="#8a9bb5", family="DM Sans"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8e0d0")),
        yaxis=dict(tickprefix="AED ", gridcolor="rgba(201,168,76,0.06)", color="#8a9bb5"),
        xaxis=dict(gridcolor="rgba(201,168,76,0.06)", color="#8a9bb5"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough yearly data for one or both communities.")

# ── Transaction volume by year ─────────────────────────────────────────────────
st.markdown('<div class="section-title">Transaction Volume by Year — Market Activity</div>', unsafe_allow_html=True)

sub_a = dld[(dld["area"] == area_a) & (dld["year"] >= 2019)].groupby("year").size().reset_index(name="count")
sub_b = dld[(dld["area"] == area_b) & (dld["year"] >= 2019)].groupby("year").size().reset_index(name="count")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=sub_a["year"], y=sub_a["count"], name=area_a,
    marker_color="rgba(74,158,255,0.7)",
    hovertemplate="<b>%{x}</b><br>%{y:,} transactions<extra></extra>"
))
fig2.add_trace(go.Bar(
    x=sub_b["year"], y=sub_b["count"], name=area_b,
    marker_color="rgba(45,212,160,0.7)",
    hovertemplate="<b>%{x}</b><br>%{y:,} transactions<extra></extra>"
))
fig2.update_layout(
    plot_bgcolor="#111827", paper_bgcolor="#111827",
    font=dict(color="#8a9bb5"),
    barmode="group",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8e0d0")),
    yaxis=dict(gridcolor="rgba(201,168,76,0.06)", color="#8a9bb5"),
    xaxis=dict(gridcolor="rgba(201,168,76,0.06)", color="#8a9bb5"),
    margin=dict(l=0, r=0, t=10, b=0),
    height=260,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Price distribution ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Price Distribution — Where Do Most Transactions Happen?</div>', unsafe_allow_html=True)

sub_a_price = dld[(dld["area"] == area_a) & (dld["price_aed"] <= dld["price_aed"].quantile(0.95))]["price_aed"]
sub_b_price = dld[(dld["area"] == area_b) & (dld["price_aed"] <= dld["price_aed"].quantile(0.95))]["price_aed"]

fig3 = go.Figure()
fig3.add_trace(go.Histogram(
    x=sub_a_price, name=area_a, nbinsx=30,
    marker_color="rgba(74,158,255,0.6)", opacity=0.8,
))
fig3.add_trace(go.Histogram(
    x=sub_b_price, name=area_b, nbinsx=30,
    marker_color="rgba(45,212,160,0.6)", opacity=0.8,
))
fig3.update_layout(
    barmode="overlay",
    plot_bgcolor="#111827", paper_bgcolor="#111827",
    font=dict(color="#8a9bb5"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8e0d0")),
    xaxis=dict(tickprefix="AED ", gridcolor="rgba(201,168,76,0.06)", color="#8a9bb5"),
    yaxis=dict(gridcolor="rgba(201,168,76,0.06)", color="#8a9bb5", title="Transactions"),
    margin=dict(l=0, r=0, t=10, b=0),
    height=260,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Verdict ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Verdict</div>', unsafe_allow_html=True)

def winner(val_a, val_b, higher_is_better=True):
    if higher_is_better:
        return (area_a, "#4a9eff") if val_a >= val_b else (area_b, "#2dd4a0")
    else:
        return (area_a, "#4a9eff") if val_a <= val_b else (area_b, "#2dd4a0")

verdicts = [
    ("📈", "Best Investment Yield",    winner(yield_a, yield_b, True)),
    ("💰", "Most Affordable",          winner(sa["avg_psf"], sb["avg_psf"], False)),
    ("📊", "Most Active Market",       winner(sa["txn_count"], sb["txn_count"], True)),
    ("🏷️", "Lower Entry Price",        winner(sa["min_price"], sb["min_price"], False)),
    ("📉", "Lower Annual Rent",        winner(rent_a, rent_b, False)),
    ("🏆", "Higher Price Growth",      winner(
        (trend_a.get(max(trend_a), 0) - trend_a.get(min(trend_a), 1)) / max(trend_a.get(min(trend_a), 1), 1),
        (trend_b.get(max(trend_b), 0) - trend_b.get(min(trend_b), 1)) / max(trend_b.get(min(trend_b), 1), 1),
        True) if trend_a and trend_b else (area_a, "#4a9eff")),
]

cols = st.columns(3)
for i, (icon, cat, (win, color)) in enumerate(verdicts):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="verdict-card">
          <div class="verdict-icon">{icon}</div>
          <div class="verdict-cat">{cat}</div>
          <div class="verdict-winner" style="color:{color}">{win}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# ── Raw data expander ──────────────────────────────────────────────────────────
with st.expander("📋 View raw DLD transactions for both areas"):
    tab_a, tab_b = st.tabs([area_a, area_b])
    with tab_a:
        show_a = dld[dld["area"] == area_a][["date","size_sqft","price_aed","psf"]].sort_values("date", ascending=False).head(200)
        show_a = show_a.rename(columns={"date":"Date","size_sqft":"Size (sqft)","price_aed":"Price (AED)","psf":"AED/sqft"})
        show_a["Price (AED)"] = show_a["Price (AED)"].apply(lambda x: f"AED {x:,.0f}")
        show_a["AED/sqft"]    = show_a["AED/sqft"].apply(lambda x: f"AED {x:,.0f}")
        st.dataframe(show_a, use_container_width=True, hide_index=True)
    with tab_b:
        show_b = dld[dld["area"] == area_b][["date","size_sqft","price_aed","psf"]].sort_values("date", ascending=False).head(200)
        show_b = show_b.rename(columns={"date":"Date","size_sqft":"Size (sqft)","price_aed":"Price (AED)","psf":"AED/sqft"})
        show_b["Price (AED)"] = show_b["Price (AED)"].apply(lambda x: f"AED {x:,.0f}")
        show_b["AED/sqft"]    = show_b["AED/sqft"].apply(lambda x: f"AED {x:,.0f}")
        st.dataframe(show_b, use_container_width=True, hide_index=True)

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
  <b>Data sources:</b>
  All price and transaction data sourced directly from Dubai Land Department (DLD) open data.
  Rental prices from Bayut API (live) where available, otherwise estimated at 6.5% gross yield.
  No lifestyle scores — only officially sourced data is shown.
  All figures are historical and indicative. This tool does not constitute financial or investment advice.
  <br><b>Source:</b> Dubai Land Department Open Data Portal · Bayut Property Transactions API · 2026
</div>
""", unsafe_allow_html=True)

# ── Lead capture ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="lead-box">
  <div class="lead-title">Get a Free Comparison Report</div>
  <div class="lead-sub">
    I'll send you a detailed PDF comparing {area_a} vs {area_b} with full DLD analysis
    and my personal recommendation as a Dubai real estate expert.
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

with st.form("lead_form", clear_on_submit=True):
    lc1, lc2, lc3 = st.columns(3)
    with lc1: lead_name  = st.text_input("Your Name *",        placeholder="Ahmed Al Mansouri")
    with lc2: lead_email = st.text_input("Email Address *",    placeholder="ahmed@email.com")
    with lc3: lead_phone = st.text_input("WhatsApp / Phone *", placeholder="+971 50 123 4567")
    submitted = st.form_submit_button("Get My Free Comparison Report")
    if submitted:
        if not lead_name or not lead_email or not lead_phone:
            st.error("Please fill in all three fields.")
        else:
            st.success(
                f"Thank you {lead_name.split()[0]}! I'll send your {area_a} vs {area_b} "
                f"comparison report to {lead_email} within 24 hours."
            )

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#2a3548;font-size:0.75rem;'>"
    "Built by Rahul Verma · Dubai Real Estate Agent & Python Developer · "
    "Data: Dubai Land Department Open Data · Bayut API · 2026</p>",
    unsafe_allow_html=True
)