import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retailer Rewards Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .kpi-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #DDE3EE;
        border-top: 3px solid var(--accent);
    }
    .kpi-label { font-size: 11px; font-weight: 700; color: #8A9BB5;
                 text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; }
    .kpi-value { font-size: 24px; font-weight: 700; color: #1C2B4A; }
    .kpi-sub   { font-size: 12px; color: #8A9BB5; margin-top: 4px; }
    .kpi-sub b { color: #1C2B4A; }
    .section-title {
        font-size: 12px; font-weight: 700; color: #5A6A85;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin: 1.5rem 0 0.75rem;
        padding-bottom: 6px;
        border-bottom: 1px solid #DDE3EE;
    }
    .ffr-header {
        background: #1C2B4A; color: white;
        padding: 10px 16px; border-radius: 8px 8px 0 0;
        font-weight: 600; font-size: 14px;
    }
    .ffr-sub { font-size: 12px; color: #8FA8C8; float: right; font-weight: 400; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path="Dashboard_Backend.xlsx"):
    df = pd.read_excel(path)

    # Column indexes (0-based) — Dashboard_Backend.xlsx schema:
    # [0] WD Code  [1] WD Name  [2] Retailer Code  [3] Retailer Name  [4] FFR
    # [5] SKU Base  [6] Distt. SKU CM  [7] Distt. SKU CM >6EA
    # [8] Avg SKU Count  [9] SKU Remaining Target
    # [10] TO Base  [11] T.O. Achieved  [12] Avg TO  [13] TO Remaining Target
    # [14] Range Selling Reward  [15] T.O. Reward  [16] WDSM Claim

    cols = df.columns
    out = pd.DataFrame({
        "WD Code":        df.iloc[:, 0].astype(str).str.strip(),
        "WD Name":        df.iloc[:, 1].astype(str).str.strip(),
        "Retailer Code":  df.iloc[:, 2].astype(str).str.strip(),
        "Retailer Name":  df.iloc[:, 3].astype(str).str.strip(),
        "FFR":            df.iloc[:, 4].astype(str).str.strip(),
        "TO Base":        pd.to_numeric(df.iloc[:, 10], errors="coerce").fillna(0) * 1000,
        "TO Achieved":    pd.to_numeric(df.iloc[:, 11], errors="coerce").fillna(0) * 1000,
        "TO Remaining":   pd.to_numeric(df.iloc[:, 13], errors="coerce").fillna(0) * 1000,
        "Range Reward":   pd.to_numeric(df.iloc[:, 14], errors="coerce").fillna(0),
        "TO Reward":      pd.to_numeric(df.iloc[:, 15], errors="coerce").fillna(0) * 1000,
        "WDSM Claim":     pd.to_numeric(df.iloc[:, 16], errors="coerce").fillna(0),
    })

    # Drop rows with missing WD Name or Retailer Code
    out = out[out["WD Name"].notna() & (out["WD Name"] != "nan") & (out["WD Name"] != "")]
    out = out[out["Retailer Code"].notna() & (out["Retailer Code"] != "nan") & (out["Retailer Code"] != "")]

    out["Total Payout"] = out["Range Reward"] + out["TO Reward"] + out["WDSM Claim"]

    def status(row):
        if row["Range Reward"] > 0 and row["TO Reward"] > 0: return "Both"
        if row["Range Reward"] > 0: return "Range only"
        if row["TO Reward"] > 0:    return "TO only"
        return "None"

    out["Status"] = out.apply(status, axis=1)
    return out


# ── Formatters ────────────────────────────────────────────────────────────────
def inr(n, decimals=2):
    if n == 0: return "—"
    return f"₹{n:,.{decimals}f}"

def inr0(n):
    return inr(n, 0)


# ── Load ──────────────────────────────────────────────────────────────────────
try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ `Dashboard_Backend.xlsx` not found. Place it in the same folder as this script.")
    st.stop()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Retailer Rewards Dashboard")
st.markdown("<p style='color:#8A9BB5;margin-top:-12px'>Range Selling · T.O. Reward · WDSM Claim</p>",
            unsafe_allow_html=True)
st.divider()


# ── WD Selector ───────────────────────────────────────────────────────────────
wd_names = sorted(df["WD Name"].unique())
selected_wd = st.selectbox("Select WD", wd_names, label_visibility="visible")

wdf = df[df["WD Name"] == selected_wd].copy()
st.caption(f"{len(wdf)} retailers under **{selected_wd}**")


# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)

earning       = (wdf["WDSM Claim"] > 0).sum()
total_range   = wdf["Range Reward"].sum()
total_to      = wdf["TO Reward"].sum()
total_wdsm    = wdf["WDSM Claim"].sum()
total_payout  = wdf["Total Payout"].sum()
both_count    = (wdf["Status"] == "Both").sum()

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, sub, accent):
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, "Total Retailers",      str(len(wdf)),          f"<b>{earning}</b> earning rewards",       "#3B7DD8")
kpi(k2, "Range Selling Reward", inr0(total_range),      f"<b>{(wdf['Range Reward']>0).sum()}</b> retailers", "#0E9E74")
kpi(k3, "T.O. Reward",          inr(total_to),          f"<b>{(wdf['TO Reward']>0).sum()}</b> retailers",    "#7B5EA7")
kpi(k4, "WDSM Claim",           inr0(total_wdsm),       f"<b>{earning}</b> claimants",             "#E07B1A")
kpi(k5, "Total Payout",         inr(total_payout),      f"<b>{both_count}</b> earned both",        "#D94F3D")


# ── Reward Breakdown ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Reward breakdown</div>', unsafe_allow_html=True)

status_counts = wdf["Status"].value_counts()
b1, b2, b3, b4 = st.columns(4)

for col, label, color in [
    (b1, "Both rewards",  "#0E9E74"),
    (b2, "Range only",    "#3B7DD8"),
    (b3, "TO only",       "#E07B1A"),
    (b4, "None",          "#C5D0E0"),
]:
    status_key = label.replace(" rewards", "").strip()
    # match label to Status column values
    count_map = {"Both rewards": "Both", "Range only": "Range only",
                 "TO only": "TO only", "None": "None"}
    count = int(status_counts.get(count_map[label], 0))
    pct   = round(count / len(wdf) * 100) if len(wdf) else 0
    col.markdown(f"""
    <div style="border-left:4px solid {color};padding:10px 14px;
                background:#fff;border-radius:0 8px 8px 0;border:1px solid #DDE3EE;border-left:4px solid {color}">
        <div style="font-size:11px;color:#8A9BB5;text-transform:uppercase;
                    letter-spacing:0.07em;font-weight:700">{label}</div>
        <div style="font-size:22px;font-weight:700;color:#1C2B4A">{count}
            <span style="font-size:13px;font-weight:400;color:#8A9BB5">({pct}%)</span>
        </div>
    </div>""", unsafe_allow_html=True)


# ── Salesman (FFR) Cards ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">Salesman summary</div>', unsafe_allow_html=True)

ffrs = sorted(wdf["FFR"].unique())
ffr_cols = st.columns(min(len(ffrs), 3))

for i, ffr in enumerate(ffrs):
    fdf = wdf[wdf["FFR"] == ffr]
    col = ffr_cols[i % len(ffr_cols)]

    f_range  = fdf["Range Reward"].sum()
    f_to     = fdf["TO Reward"].sum()
    f_wdsm   = fdf["WDSM Claim"].sum()
    f_total  = fdf["Total Payout"].sum()
    f_earn   = (fdf["WDSM Claim"] > 0).sum()

    # Build retailer sub-table for this FFR
    display_fdf = fdf[[
        "Retailer Code", "Retailer Name",
        "Range Reward", "TO Reward", "WDSM Claim", "Total Payout"
    ]].copy()

    display_fdf["Range Reward"]  = display_fdf["Range Reward"].apply(inr0)
    display_fdf["TO Reward"]     = display_fdf["TO Reward"].apply(inr)
    display_fdf["WDSM Claim"]    = display_fdf["WDSM Claim"].apply(inr0)
    display_fdf["Total Payout"]  = display_fdf["Total Payout"].apply(inr)

    display_fdf = display_fdf.rename(columns={
        "Retailer Code": "Code",
        "Retailer Name": "Retailer",
        "Range Reward":  "Range reward",
        "TO Reward":     "T.O. reward",
        "WDSM Claim":    "WDSM claim",
        "Total Payout":  "Total payout",
    })

    with col:
        st.markdown(f"""
        <div class="ffr-header">{ffr}
            <span class="ffr-sub">{len(fdf)} retailers · {f_earn} earning</span>
        </div>""", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Range reward", inr0(f_range))
        m2.metric("T.O. reward",  inr(f_to))
        m3.metric("WDSM claim",   inr0(f_wdsm))

        st.dataframe(
            display_fdf,
            use_container_width=True,
            hide_index=True,
            height=min(38 * len(fdf) + 38, 280)
        )
        st.markdown(
            f"<div style='text-align:right;font-size:12px;font-weight:700;"
            f"color:#1C2B4A;padding:4px 0 12px'>Total payout: {inr(f_total)}</div>",
            unsafe_allow_html=True
        )


# ── Master Retailer Table ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">Retailer detail</div>', unsafe_allow_html=True)

search = st.text_input("Search retailer, code or salesman", placeholder="Type to filter…")

display_df = wdf.copy()
if search:
    q = search.lower()
    display_df = display_df[
        display_df["Retailer Name"].str.lower().str.contains(q) |
        display_df["Retailer Code"].str.lower().str.contains(q) |
        display_df["FFR"].str.lower().str.contains(q)
    ]

# Format money columns for display
table_df = display_df[[
    "Retailer Code", "Retailer Name", "FFR",
    "TO Achieved", "TO Remaining",
    "Range Reward", "TO Reward", "WDSM Claim", "Total Payout", "Status"
]].copy()

table_df["TO Achieved"]   = table_df["TO Achieved"].apply(inr)
table_df["TO Remaining"]  = table_df["TO Remaining"].apply(lambda x: inr(x, 2))
table_df["Range Reward"]  = table_df["Range Reward"].apply(inr0)
table_df["TO Reward"]     = table_df["TO Reward"].apply(inr)
table_df["WDSM Claim"]    = table_df["WDSM Claim"].apply(inr0)
table_df["Total Payout"]  = table_df["Total Payout"].apply(inr)

table_df = table_df.rename(columns={
    "Retailer Code": "Code",
    "Retailer Name": "Retailer",
    "TO Achieved":   "T.O. achieved",
    "TO Remaining":  "T.O. remaining",
    "Range Reward":  "Range reward",
    "TO Reward":     "T.O. reward",
    "WDSM Claim":    "WDSM claim",
    "Total Payout":  "Total payout",
})

st.dataframe(table_df, use_container_width=True, hide_index=True, height=min(38 * len(table_df) + 38, 500))

grand_total = display_df["Total Payout"].sum()
st.caption(f"Showing **{len(display_df)}** of **{len(wdf)}** retailers · Grand total payout: **{inr(grand_total)}**")
