import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Retailer Rewards Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .kpi-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #DDE3EE;
        border-top: 3px solid var(--accent);
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 11px; font-weight: 700; color: #8A9BB5;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px;
    }
    .kpi-value { font-size: 28px; font-weight: 700; color: #1C2B4A; }
    .kpi-sub   { font-size: 12px; color: #8A9BB5; margin-top: 4px; }
    .section-title {
        font-size: 12px; font-weight: 700; color: #5A6A85;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin: 1.5rem 0 0.6rem;
        padding-bottom: 6px;
        border-bottom: 1px solid #DDE3EE;
    }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path="Dashboard_Backend.xlsx"):
    df = pd.read_excel(path, engine="openpyxl")

    # Column indexes (0-based):
    # [0] WD Code        [1] WD Name         [2] Retailer Code   [3] Retailer Name
    # [4] FFR            [5] SKU Base         [6] Distt. SKU CM   [7] Distt. SKU CM >6EA
    # [8] Avg SKU Count  [9] SKU Remaining    [10] TO Base        [11] T.O. Achieved
    # [12] Avg TO        [13] TO Remaining    [14] Range Reward   [15] T.O. Reward (x1000)
    # [16] WDSM Claim

    out = pd.DataFrame({
        "WD Name":              df.iloc[:, 1].astype(str).str.strip(),
        "Retailer Code":        df.iloc[:, 2].astype(str).str.strip(),
        "Retailer Name":        df.iloc[:, 3].astype(str).str.strip(),
        "FFR":                  df.iloc[:, 4].astype(str).str.strip(),
        "SKU Base":             pd.to_numeric(df.iloc[:, 5],  errors="coerce").fillna(0),
        "Distt. SKU CM":        pd.to_numeric(df.iloc[:, 6],  errors="coerce").fillna(0),
        "Distt. SKU CM >6EA":   pd.to_numeric(df.iloc[:, 7],  errors="coerce").fillna(0),
        "Avg SKU Count":        pd.to_numeric(df.iloc[:, 8],  errors="coerce").fillna(0),
        "SKU Remaining Target": pd.to_numeric(df.iloc[:, 9],  errors="coerce").fillna(0),
        "TO Base":              pd.to_numeric(df.iloc[:, 10], errors="coerce").fillna(0) * 1000,
        "TO Achieved":          pd.to_numeric(df.iloc[:, 11], errors="coerce").fillna(0) * 1000,
        "Range Reward":         pd.to_numeric(df.iloc[:, 14], errors="coerce").fillna(0),
        "TO Reward":            pd.to_numeric(df.iloc[:, 15], errors="coerce").fillna(0) * 1000,
        "WDSM Claim":           pd.to_numeric(df.iloc[:, 16], errors="coerce").fillna(0),
    })

    out = out[~out["WD Name"].isin(["", "nan", "NaN"])].reset_index(drop=True)
    out = out[~out["Retailer Code"].isin(["", "nan", "NaN"])].reset_index(drop=True)
    return out


# ── Load with full error visibility ──────────────────────────────────────────
df = None
try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ `Dashboard_Backend.xlsx` not found. Make sure it is committed to your GitHub repo.")
    st.stop()
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

if df is None or df.empty:
    st.error("❌ Data loaded but is empty. Check that Dashboard_Backend.xlsx has data rows.")
    st.stop()

if "WD Name" not in df.columns:
    st.error(f"❌ 'WD Name' column missing. Columns found: {list(df.columns)}")
    st.stop()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## Retailer Rewards Dashboard")
st.markdown(
    "<p style='color:#8A9BB5;margin-top:-12px'>SKU Performance · T.O. · Range Selling · WDSM</p>",
    unsafe_allow_html=True
)
st.divider()


# ── WD Selector ───────────────────────────────────────────────────────────────
wd_names = sorted(df["WD Name"].unique().tolist())
selected_wd = st.selectbox("Select WD", wd_names)
wdf = df[df["WD Name"] == selected_wd].copy().reset_index(drop=True)
st.caption(f"{len(wdf)} retailers under **{selected_wd}**")


# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)

total_retailers = len(wdf)
got_range       = int((wdf["Range Reward"] > 0).sum())
got_to          = int((wdf["TO Reward"] > 0).sum())
got_both        = int(((wdf["Range Reward"] > 0) & (wdf["TO Reward"] > 0)).sum())
got_none        = int(((wdf["Range Reward"] == 0) & (wdf["TO Reward"] == 0)).sum())

def kpi_card(col, label, value, sub, accent):
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
kpi_card(k1, "Total Retailers",      str(total_retailers), "under selected WD",       "#3B7DD8")
kpi_card(k2, "Range Selling Reward", str(got_range),       "retailers qualified",      "#0E9E74")
kpi_card(k3, "T.O. Reward",          str(got_to),          "retailers qualified",      "#7B5EA7")
kpi_card(k4, "Both Rewards",         str(got_both),        "got range + T.O. both",   "#E07B1A")
kpi_card(k5, "No Reward",            str(got_none),        "retailers not qualified",  "#C5D0E0")


# ── Formatters ────────────────────────────────────────────────────────────────
def fmt_inr(n):
    return f"₹{n:,.2f}" if n != 0 else "—"

def fmt_num(n):
    return f"{int(n):,}" if n != 0 else "—"


# ── Table 1: SKU + TO Performance ────────────────────────────────────────────
st.markdown('<div class="section-title">Table 1 — SKU & T.O. Performance</div>', unsafe_allow_html=True)

t1 = wdf[["Retailer Code", "Retailer Name",
           "SKU Base", "Distt. SKU CM", "Distt. SKU CM >6EA",
           "Avg SKU Count", "SKU Remaining Target",
           "TO Base", "TO Achieved"]].copy()

t1["SKU Base"]             = t1["SKU Base"].apply(fmt_num)
t1["Distt. SKU CM"]        = t1["Distt. SKU CM"].apply(fmt_num)
t1["Distt. SKU CM >6EA"]   = t1["Distt. SKU CM >6EA"].apply(fmt_num)
t1["Avg SKU Count"]        = t1["Avg SKU Count"].apply(fmt_num)
t1["SKU Remaining Target"] = t1["SKU Remaining Target"].apply(fmt_num)
t1["TO Base"]              = t1["TO Base"].apply(fmt_inr)
t1["TO Achieved"]          = t1["TO Achieved"].apply(fmt_inr)

t1 = t1.rename(columns={
    "Retailer Code":        "Code",
    "Retailer Name":        "Retailer",
    "SKU Remaining Target": "SKU Remaining",
})

st.dataframe(t1, use_container_width=True, hide_index=True,
             height=min(38 * len(t1) + 46, 520))


# ── Table 2: Retailer Rewards ─────────────────────────────────────────────────
st.markdown('<div class="section-title">Table 2 — Retailer Rewards</div>', unsafe_allow_html=True)

t2 = wdf[["Retailer Code", "Retailer Name",
           "TO Reward", "Range Reward", "WDSM Claim"]].copy()

t2["TO Reward"]    = t2["TO Reward"].apply(fmt_inr)
t2["Range Reward"] = t2["Range Reward"].apply(fmt_inr)
t2["WDSM Claim"]   = t2["WDSM Claim"].apply(fmt_inr)

t2 = t2.rename(columns={
    "Retailer Code": "Code",
    "Retailer Name": "Retailer",
    "TO Reward":     "T.O. Reward",
    "Range Reward":  "Range Selling Reward",
    "WDSM Claim":    "WDSM Claim",
})

st.dataframe(t2, use_container_width=True, hide_index=True,
             height=min(38 * len(t2) + 46, 520))