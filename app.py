import datetime
import io
import json
import urllib.request
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

EASTERN_TZ = ZoneInfo("America/New_York")


def get_eastern_time_str():
    return datetime.datetime.now(EASTERN_TZ).strftime("%H:%M:%S")


def get_eastern_now():
    return datetime.datetime.now(EASTERN_TZ)


def format_date_clean(val):
    if pd.isna(val) or str(val).strip() == "":
        return "N/A"
    dt = pd.to_datetime(val, errors="coerce")
    if pd.isna(dt):
        return str(val).split(" ")[0]
    return dt.strftime("%Y-%m-%d")


# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING (FIXED PRINT ENGINE)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lady Vols Basketball | Performance Console",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp { background-color: #F8FAFC; color: #0F172A; }
        section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
        
        .console-header {
            background: linear-gradient(90deg, #FF8200 0%, #D96B00 100%);
            padding: 12px 20px;
            border-radius: 8px;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 1.4rem;
            letter-spacing: 0.5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .athlete-card {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        .athlete-avatar {
            width: 75px;
            height: 75px;
            border-radius: 50%;
            border: 3px solid #FF8200;
            object-fit: cover;
            background-color: #F1F5F9;
        }

        .vball-section-title {
            background-color: #38BDF8; color: #0F172A; font-weight: 700; font-size: 1.05rem;
            padding: 8px 16px; border-radius: 6px; text-align: center;
            margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;
        }

        .vball-table {
            width: 100%; border-collapse: collapse; background-color: #FFFFFF;
            border-radius: 8px; overflow: hidden; border: 1px solid #E2E8F0;
            font-size: 0.88rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03); margin-bottom: 12px;
            margin-left: auto; margin-right: auto;
        }
        .vball-table th {
            background-color: #F1F5F9; color: #475569; font-weight: 700; text-align: center !important;
            padding: 8px 12px; border-bottom: 2px solid #E2E8F0; text-transform: uppercase; font-size: 0.72rem;
        }
        .vball-table td { 
            padding: 8px 12px; border-bottom: 1px solid #F1F5F9; color: #0F172A; text-align: center !important; 
        }
        .vball-table tr:last-child td { border-bottom: none; }
        .grade-badge { font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; }

        .compliance-subcard {
            background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
            padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); height: 100%;
        }
        .compliance-metric-card {
            background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;
            padding: 8px 6px; text-align: center;
        }
        .compliance-metric-label { font-size: 0.68rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 2px; }
        .compliance-metric-value { font-size: 1.05rem; font-weight: 800; color: #0F172A; }
        .compliance-metric-sub { font-size: 0.68rem; color: #94A3B8; margin-top: 2px; }

        .rec-grid-card {
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }

        [data-testid="stDataFrame"] div[role="columnheader"] {
            justify-content: center !important;
            text-align: center !important;
        }
        [data-testid="stDataFrame"] div[role="columnheader"] span {
            text-align: center !important;
            width: 100% !important;
        }
        [data-testid="stDataFrame"] div[role="gridcell"] {
            justify-content: center !important;
            text-align: center !important;
        }

        @media print {
            @page {
                size: portrait;
                margin: 0.35in;
            }

            section[data-testid="stSidebar"],
            header[data-testid="stHeader"],
            footer,
            .stButton,
            .no-print,
            .console-header,
            div[data-baseweb="tab-list"],
            div[data-baseweb="tab-border"],
            div[data-testid="stSelectbox"],
            div[data-testid="stDateInput"] {
                display: none !important;
            }

            html, body, .stApp, .main,
            div[data-testid="stAppViewContainer"],
            div[data-testid="stAppViewBlockContainer"],
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stVerticalBlock"],
            div[data-testid="stTabs"],
            div[data-baseweb="tab-panel"] {
                overflow: visible !important;
                height: auto !important;
                min-height: 100% !important;
                background-color: #FFFFFF !important;
                display: block !important;
            }

            .main .block-container {
                max-width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            .practice-score-card {
                padding: 10px 14px !important;
                margin-bottom: 12px !important;
                border: 1px solid #CBD5E1 !important;
                box-shadow: none !important;
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }

            .practice-score-card .vball-table th,
            .practice-score-card .vball-table td {
                padding: 3px 6px !important;
                font-size: 0.72rem !important;
            }

            .practice-score-card .vball-section-title {
                font-size: 0.78rem !important;
                padding: 3px 8px !important;
                margin-bottom: 6px !important;
            }

            .practice-score-card:nth-of-type(2n) {
                page-break-after: always !important;
                break-after: page !important;
            }
        }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. PASSWORD PROTECTION (ROLE-BASED LOGIN)
# -----------------------------------------------------------------------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = None

    if not st.session_state["authenticated"]:
        st.markdown(
            '<div class="console-header">LADY VOLS PERFORMANCE CONSOLE - LOGIN</div>',
            unsafe_allow_html=True,
        )
        
        st.markdown(
            """
            <style>
                div[data-testid="stVerticalBlock"]:has(button[key="login_submit_btn"]) button,
                div[data-testid="stButton"]:has(button[key="login_submit_btn"]) button {
                    background-color: #38BDF8 !important;
                    color: #0F172A !important;
                    border: 1px solid #0284C7 !important;
                    font-weight: 700 !important;
                }
                div[data-testid="stVerticalBlock"]:has(button[key="login_submit_btn"]) button:hover,
                div[data-testid="stButton"]:has(button[key="login_submit_btn"]) button:hover {
                    background-color: #0EA5E9 !important;
                    color: #0F172A !important;
                    border-color: #0369A1 !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        pwd = st.text_input("Enter Dashboard Password:", type="password")
        if st.button("Login", key="login_submit_btn", use_container_width=True):
            admin_pwd = st.secrets.get("dashboard_password", "ladyvols")
            rec_pwd = st.secrets.get("recovery_password", "ladyvolsrecovery")

            if pwd == admin_pwd:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = "admin"
                st.rerun()
            elif pwd == rec_pwd:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = "recovery_only"
                st.rerun()
            else:
                st.error("Incorrect password.")
        return False
    return True


if not check_password():
    st.stop()


# -----------------------------------------------------------------------------
# 3. DATA LOADING VIA SECRETS & DYNAMIC LIVE FETCH
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_sheet_data():
    def fetch_csv(secret_key):
        if "sheets" not in st.secrets or secret_key not in st.secrets["sheets"]:
            return pd.DataFrame()
        url = st.secrets["sheets"][secret_key]
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8")
            return pd.read_csv(
                io.StringIO(content), on_bad_lines="skip", engine="python"
            )

    try:
        vol_df = fetch_csv("volume_url")
        int_df = fetch_csv("intensity_url")
        comp_df = fetch_csv("compliance_url")
        weekly_df = fetch_csv("weekly_url")
        cmj_df = fetch_csv("cmj_url")
        roster_df = fetch_csv("roster_url")

        nordic_df = fetch_csv("nordic_url")
        belt_squat_df = fetch_csv("belt_squat_url")
        ankle_df = fetch_csv("ankle_url")
        knee_df = fetch_csv("knee_url")
        hip_df = fetch_csv("hip_url")

        for df in [
            vol_df,
            int_df,
            comp_df,
            weekly_df,
            cmj_df,
            nordic_df,
            belt_squat_df,
            ankle_df,
            knee_df,
            hip_df,
        ]:
            if df.empty:
                continue
            date_col = [c for c in df.columns if "date" in c.lower()]
            if date_col:
                df["Date"] = pd.to_datetime(df[date_col[0]], errors="coerce")
                df["Date_Str"] = df["Date"].dt.strftime("%Y-%m-%d")

        return (
            vol_df,
            int_df,
            comp_df,
            weekly_df,
            cmj_df,
            roster_df,
            nordic_df,
            belt_squat_df,
            ankle_df,
            knee_df,
            hip_df,
        )
    except Exception as e:
        st.error(f"Error loading data from Google Sheets secrets: {e}")
        st.stop()


(
    vol_raw,
    int_raw,
    comp_raw,
    weekly_raw,
    cmj_raw,
    roster_raw,
    nordic_raw,
    belt_squat_raw,
    ankle_raw,
    knee_raw,
    hip_raw,
) = load_sheet_data()


def fetch_live_recovery_sheet():
    macro_url = (
        st.secrets.get("MACRO_URL")
        or st.secrets.get("Live Track")
        or st.secrets.get("sheets", {}).get("live_track_url")
    )

    if macro_url:
        try:
            res = requests.get(f"{macro_url}?sheet=Logs&t={datetime.datetime.now().timestamp()}", headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    df_json = pd.DataFrame(data)
                    for col in ["Week_Starting", "Athlete", "Station", "Day", "Duration_Minutes"]:
                        if col in df_json.columns:
                            df_json[col] = df_json[col].astype(str).str.strip()
                    return df_json
        except Exception as e:
            print(f"Apps Script GET fallback: {e}")

    return pd.DataFrame(
        columns=[
            "Week_Starting",
            "Athlete",
            "Station",
            "Day",
            "Timestamp",
            "Duration_Minutes",
        ]
    )


def fetch_live_tracking_sheet():
    macro_url = (
        st.secrets.get("MACRO_URL")
        or st.secrets.get("Live Track")
        or st.secrets.get("sheets", {}).get("live_track_url")
    )

    if macro_url:
        try:
            fetch_url = f"{macro_url}?sheet=Tracking_Logs&t={datetime.datetime.now().timestamp()}"
            res = requests.get(fetch_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            if res.status_code == 200 and res.text.strip():
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    df.columns = [str(c).strip() for c in df.columns]
                    return df
        except Exception as e:
            print(f"Error fetching live tracking sheet: {e}")

    return pd.DataFrame()


if "tracking_data" not in st.session_state or not st.session_state.get("tracking_data_initialized", False):
    st.session_state.tracking_data = {}
    live_track_df = fetch_live_tracking_sheet()
    
    if not live_track_df.empty:
        cols_lower = {str(c).lower().strip(): c for c in live_track_df.columns}
        wk_col = cols_lower.get("week_starting", "Week_Starting")
        dt_col = cols_lower.get("date", "Date")
        ath_col = cols_lower.get("athlete", "Athlete")
        met_col = cols_lower.get("metric", "Metric")
        cnt_col = cols_lower.get("count", "Count")

        for _, row in live_track_df.iterrows():
            raw_wk = str(row.get(wk_col, "")).strip()
            raw_dt = str(row.get(dt_col, "")).strip()
            ath = str(row.get(ath_col, "")).strip()
            met = str(row.get(met_col, "")).strip()
            cnt = pd.to_numeric(row.get(cnt_col, 0), errors="coerce")
            
            wk_clean = format_date_clean(raw_wk)
            dt_clean = format_date_clean(raw_dt)
            
            if wk_clean != "N/A" and dt_clean != "N/A" and ath and met and pd.notna(cnt):
                key = f"{wk_clean}|{dt_clean}|{ath}|{met}"
                st.session_state.tracking_data[key] = int(cnt)
                
    st.session_state.tracking_data_initialized = True


# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def filter_by_season(df, season_name):
    if df.empty:
        return df
    season_col = next((c for c in df.columns if c.lower() in ["season", "phase"]), None)
    if season_col:
        target_norm = season_name.lower().replace("-", "").replace(" ", "").replace("_", "")
        series_norm = df[season_col].astype(str).str.lower().str.replace("-", "").str.replace(" ", "").str.replace("_", "")
        filtered = df[series_norm == target_norm]
        return filtered if not filtered.empty else pd.DataFrame(columns=df.columns)
    return df


def get_vball_color(score):
    if score is None or pd.isna(score):
        return "#E2E8F0", "#475569"
    if score < 50:
        return "#BBF7D0", "#166534"
    elif score < 75:
        return "#FEF08A", "#854D0E"
    else:
        return "#FFD6D6", "#991B1B"


def render_vball_table(df):
    if df.empty:
        return (
            "<p style='color:#64748B; font-style:italic;'>No data available for this season.</p>"
        )
    df_clean = df.copy()
    if "Date" in df_clean.columns:
        df_clean["Date"] = df_clean["Date"].apply(format_date_clean)

    html = '<table class="vball-table"><thead><tr>'
    for col in df_clean.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df_clean.iterrows():
        html += "<tr>"
        for col in df_clean.columns:
            val = row[col]
            if col == "Grade":
                bg_c, fg_c = get_vball_color(val)
                html += f'<td><span class="grade-badge" style="background-color:{bg_c}; color:{fg_c};">{val}</span></td>'
            elif isinstance(val, float):
                html += f"<td>{val:.2f}</td>"
            else:
                html += f"<td>{val}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html


def create_clean_bar_chart(x_vals, y_vals, title_text, bar_color="#38BDF8"):
    fig = px.bar(x=x_vals, y=y_vals, title=title_text)
    fig.update_traces(marker_color=bar_color)
    fig.update_layout(
        title_font=dict(size=14, color="#0F172A"),
        height=240,
        margin=dict(l=0, r=0, t=35, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig


def compute_practice_tables(player_name, session_date_str, v_source, i_source):
    v_player = v_source[
        (v_source["Player"] == player_name)
        & (v_source["Date_Str"] == str(session_date_str))
    ]
    i_player = i_source[
        (i_source["Player"] == player_name)
        & (i_source["Date_Str"] == str(session_date_str))
    ]

    v_all = (
        v_source[v_source["Player"] == player_name].sort_values("Date")
        if not v_source.empty
        else pd.DataFrame()
    )
    i_all = (
        i_source[i_source["Player"] == player_name].sort_values("Date")
        if not i_source.empty
        else pd.DataFrame()
    )

    if not v_all.empty and "Date" in v_all.columns and v_all["Date"].notna().any():
        start_date_v = v_all["Date"].min()
        v_base = v_all[v_all["Date"] <= start_date_v + pd.Timedelta(days=14)]
    else:
        v_base = v_all

    if not i_all.empty and "Date" in i_all.columns and i_all["Date"].notna().any():
        start_date_i = i_all["Date"].min()
        i_base = i_all[i_all["Date"] <= start_date_i + pd.Timedelta(days=14)]
    else:
        i_base = i_all

    vol_metrics = [
        "Distance (mi)",
        "Accels",
        "Decels",
        "FCTs",
        "Physio Load",
        "Mechanical Load",
        "Jump Load (J)",
    ]
    int_metrics = [
        "Physio Intensity",
        "High Acceleration",
        "High Speed Distance (mi)",
        "Speed (max.) (mph)",
        "Sprints",
        "Exertions",
        "High Metabolic Power Distance (m)",
    ]

    vol_rows, int_rows = [], []

    for m in vol_metrics:
        curr = (
            v_player[m].values[0]
            if not v_player.empty and m in v_player
            else 0.0
        )
        mx = v_base[m].max() if not v_base.empty and m in v_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        vol_rows.append(
            {"Metric": m, "Current": curr, "Max": mx, "Grade": grade}
        )

    for m in int_metrics:
        curr = (
            i_player[m].values[0]
            if not i_player.empty and m in i_player
            else 0.0
        )
        mx = i_base[m].max() if not i_base.empty and m in i_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        int_rows.append(
            {"Metric": m, "Current": curr, "Max": mx, "Grade": grade}
        )

    vol_df_out = pd.DataFrame(vol_rows)
    int_df_out = pd.DataFrame(int_rows)

    vol_score = int(vol_df_out["Grade"].mean()) if not vol_df_out.empty else 0
    int_score = int(int_df_out["Grade"].mean()) if not int_df_out.empty else 0
    comb_score = int(round((vol_score + int_score) / 2))

    minutes = (
        v_player["Minutes"].values[0]
        if not v_player.empty and "Minutes" in v_player
        else "--"
    )
    week_num = (
        v_player["Week"].values[0]
        if not v_player.empty and "Week" in v_player
        else "--"
    )
    day_num = (
        v_player["Day"].values[0]
        if not v_player.empty and "Day" in v_player
        else "--"
    )

    return (
        vol_df_out,
        int_df_out,
        vol_score,
        int_score,
        comb_score,
        minutes,
        week_num,
        day_num,
    )


def create_team_bar_athlete_line_chart(
    weeks,
    team_avg_vals,
    athlete_vals,
    title_text,
    athlete_name,
    bar_color="#38BDF8",
):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=weeks, y=team_avg_vals, name="Team Average", marker_color=bar_color
        )
    )
    fig.add_trace(
        go.Scatter(
            x=weeks,
            y=athlete_vals,
            name=f"{athlete_name} Output",
            mode="markers",
            marker=dict(
                symbol="line-ew", size=24, line=dict(width=3, color="black")
            ),
        )
    )
    fig.update_layout(
        title=title_text,
        title_font=dict(size=14, color="#0F172A"),
        height=250,
        margin=dict(l=0, r=0, t=35, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    return fig


def render_metric_subcard_html(p_comp, col_name, display_title, unit):
    if p_comp.empty or col_name not in p_comp.columns:
        return ""

    valid_df = p_comp.dropna(subset=[col_name])
    if valid_df.empty:
        return ""

    all_time_max = valid_df[col_name].max()
    max_row = valid_df[valid_df[col_name] == all_time_max].iloc[-1]
    max_date = format_date_clean(max_row["Date_Str"])

    recent_row = valid_df.iloc[-1]
    recent_val = recent_row[col_name]
    recent_date = format_date_clean(recent_row["Date_Str"])

    pct_max = (
        f"{(recent_val / all_time_max * 100):.1f}%"
        if all_time_max > 0
        else "-- %"
    )
    days_since = (pd.to_datetime("today") - pd.to_datetime(max_date)).days

    badge_bg = "#BBF7D0" if days_since <= 7 else "#FFD6D6"
    badge_fg = "#166534" if days_since <= 7 else "#991B1B"

    val_str = (
        f"{recent_val:.1f}{(' ' + unit) if unit else ''}"
        if isinstance(recent_val, (int, float))
        else str(recent_val)
    )
    max_str = (
        f"{all_time_max:.1f}{(' ' + unit) if unit else ''}"
        if isinstance(all_time_max, (int, float))
        else str(all_time_max)
    )

    return f"""
    <div class="compliance-subcard">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <h5 style="margin:0; font-size:0.95rem; color:#0F172A; font-weight:700;">{display_title}</h5>
            <div style="background-color:{badge_bg}; color:{badge_fg}; font-weight:700; padding:2px 8px; border-radius:10px; font-size:0.7rem;">
                {days_since} Days
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px;">
            <div class="compliance-metric-card">
                <div class="compliance-metric-label">Recent</div>
                <div class="compliance-metric-value">{val_str}</div>
                <div class="compliance-metric-sub">{recent_date}</div>
            </div>
            <div class="compliance-metric-card">
                <div class="compliance-metric-label">Season Max</div>
                <div class="compliance-metric-value">{max_str}</div>
                <div class="compliance-metric-sub">{max_date}</div>
            </div>
            <div class="compliance-metric-card">
                <div class="compliance-metric-label">% Peak Output</div>
                <div class="compliance-metric-value" style="color:#FF8200;">{pct_max}</div>
                <div class="compliance-metric-sub">Recent vs. Peak</div>
            </div>
            <div class="compliance-metric-card">
                <div class="compliance-metric-label">Recency Status</div>
                <div class="compliance-metric-value">{days_since} Days</div>
                <div class="compliance-metric-sub">Elapsed Threshold</div>
            </div>
        </div>
    </div>
    """


# -----------------------------------------------------------------------------
# 5. SIDEBAR NAVIGATION (DYNAMIC ROLES)
# -----------------------------------------------------------------------------
st.sidebar.markdown("### LADY VOLS BASKETBALL")

if st.session_state.get("user_role") == "recovery_only":
    available_views = ["Recovery"]
else:
    available_views = [
        "Individual Profile",
        "Practice Score",
        "Compliance",
        "Weekly Data",
        "Testing",
        "Recovery",
        "Tracking",
    ]

main_tab = st.sidebar.radio(
    "Console View:",
    options=available_views,
    index=0,
)

st.sidebar.divider()
st.sidebar.markdown("### DATA MANAGEMENT")

if st.sidebar.button("Refresh Google Sheets Data", use_container_width=True):
    st.cache_data.clear()
    if "recovery_local_state" in st.session_state:
        del st.session_state["recovery_local_state"]
    if "tracking_data" in st.session_state:
        del st.session_state["tracking_data"]
    if "tracking_data_initialized" in st.session_state:
        del st.session_state["tracking_data_initialized"]
    st.sidebar.success("Data reloaded!")
    st.rerun()

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.rerun()


# -----------------------------------------------------------------------------
# 6. TOP HEADER & DIRECT DOM PRINT TRIGGER
# -----------------------------------------------------------------------------
col_header_title, col_header_btn = st.columns([5, 1.2])

with col_header_title:
    st.markdown(
        """
        <div class="console-header" style="margin-bottom: 0;">
            <span>LADY VOLS BASKETBALL ANALYTICS</span>
            <span style="font-size: 0.9rem; font-weight: 600; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 4px;">PERFORMANCE CONSOLE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_header_btn:
    st.button("Print Page", key="global_print_btn", use_container_width=True)

components.html(
    """
    <script>
    const parentDoc = window.parent.document;
    function attachPrintListener() {
        const btns = parentDoc.querySelectorAll('button');
        btns.forEach(b => {
            if (b.innerText.includes('Print Page') && !b.getAttribute('data-print-bound')) {
                b.setAttribute('data-print-bound', 'true');
                b.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    window.parent.print();
                });
            }
        });
    }
    attachPrintListener();
    setInterval(attachPrintListener, 1000);
    </script>
    """,
    height=0,
    width=0,
)

st.markdown("<br>", unsafe_allow_html=True)

season_tab_summer, season_tab_post_summer = st.tabs(["Summer", "Pre-Season"])


# -----------------------------------------------------------------------------
# 7. DASHBOARD RENDER ENGINE PER SEASON
# -----------------------------------------------------------------------------
def render_dashboard_content(season_label, season_key):
    st.markdown(f"<div style='font-weight:700; color:#64748B; margin-bottom:12px; font-size:0.9rem;'>CURRENT ACTIVE SEASON: <span style='color:#FF8200;'>{season_label.upper()}</span></div>", unsafe_allow_html=True)
    
    vol_data = filter_by_season(vol_raw, season_label)
    int_data = filter_by_season(int_raw, season_label)
    comp_data = filter_by_season(comp_raw, season_label)
    weekly_data = filter_by_season(weekly_raw, season_label)
    cmj_data = filter_by_season(cmj_raw, season_label)
    nordic_data = filter_by_season(nordic_raw, season_label)
    belt_squat_data = filter_by_season(belt_squat_raw, season_label)
    ankle_data = filter_by_season(ankle_raw, season_label)
    knee_data = filter_by_season(knee_raw, season_label)
    hip_data = filter_by_season(hip_raw, season_label)

    roster_players = (
        roster_raw["Name"].tolist()
        if not roster_raw.empty
        else (vol_data["Player"].unique().tolist() if not vol_data.empty else [])
    )

    compliance_metrics = [
        ("Speed (MPH)", "Max Speed", "mph"),
        ("Distance (mi)", "Distance", "mi"),
        ("High Metabolic Power Distance (m)", "High Metabolic Power", "m"),
        ("Accels", "Accels", ""),
        ("Decels", "Decels", ""),
        ("Sprints", "Sprints", "cnt"),
        ("MCTs", "MCTs", "cnt"),
        ("FCTs", "FCTs", "cnt"),
    ]

    # TAB 1: INDIVIDUAL PROFILE
    if main_tab == "Individual Profile":
        c_sel, _ = st.columns([1, 2])
        with c_sel:
            selected_player = st.selectbox(
                "Select Athlete Profile:", roster_players, key=f"sel_player_{season_key}"
            )

        p_row = (
            roster_raw[roster_raw["Name"] == selected_player]
            if not roster_raw.empty
            else pd.DataFrame()
        )
        p_pos = (
            p_row["Position"].values[0]
            if not p_row.empty
            else "Guard / Forward | #00"
        )
        p_img = (
            p_row["Picture"].values[0]
            if not p_row.empty
            else "https://via.placeholder.com/80"
        )

        st.markdown(
            f"""
                <div class="athlete-card">
                    <img src="{p_img}" class="athlete-avatar">
                    <div class="athlete-info">
                        <h2 style="margin:0; font-size:1.4rem; font-weight:700; color:#0F172A;">{selected_player}</h2>
                        <p style="margin:2px 0 0 0; color:#64748B; font-size:0.88rem;">{p_pos}</p>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="vball-section-title">1. Workload Exposure & Compliance Grid</div>',
            unsafe_allow_html=True,
        )

        p_comp = (
            comp_data[comp_data["Player"] == selected_player].sort_values("Date")
            if not comp_data.empty
            else pd.DataFrame()
        )

        for row_idx in range(0, len(compliance_metrics), 2):
            col1, col2 = st.columns(2)
            cols = [col1, col2]
            for j in range(2):
                metric_idx = row_idx + j
                if metric_idx < len(compliance_metrics):
                    col_name, display_title, unit = compliance_metrics[metric_idx]
                    subcard_html = render_metric_subcard_html(p_comp, col_name, display_title, unit)
                    with cols[j]:
                        st.markdown(subcard_html, unsafe_allow_html=True)

        st.divider()

        st.markdown(
            '<div class="vball-section-title">2. Practice Performance & Score Trends</div>',
            unsafe_allow_html=True,
        )
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("#### Practice Score History")
            v_p = (
                vol_data[vol_data["Player"] == selected_player].sort_values("Date")
                if not vol_data.empty
                else pd.DataFrame()
            )

            if not v_p.empty:
                score_history = []
                for d_str in v_p["Date_Str"].unique():
                    _, _, v_sc, i_sc, c_sc, _, _, _ = compute_practice_tables(
                        selected_player, d_str, vol_data, int_data
                    )
                    score_history.append(
                        {
                            "Date": format_date_clean(d_str),
                            "Volume Score": v_sc,
                            "Intensity Score": i_sc,
                            "Combined Score": c_sc,
                        }
                    )

                df_score_trend = pd.DataFrame(score_history)

                fig1 = px.line(
                    df_score_trend,
                    x="Date",
                    y=["Volume Score", "Intensity Score", "Combined Score"],
                    markers=True,
                    color_discrete_sequence=["#FF8200", "#38BDF8", "#58595B"],
                )
                fig1.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=230,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        title=None,
                    ),
                )
                st.plotly_chart(fig1, use_container_width=True, key=f"chart_trend_{season_key}")
            else:
                st.info(f"No practice scores recorded for {selected_player} in {season_label}.")

        latest_date_str = (
            vol_data[vol_data["Player"] == selected_player]["Date_Str"].max()
            if not vol_data.empty
            else None
        )

        if pd.notna(latest_date_str):
            vol_df, int_df, vol_score, int_score, comb_score, mins, wk, dy = (
                compute_practice_tables(selected_player, latest_date_str, vol_data, int_data)
            )

            wk_str = str(wk).replace("Week ", "")
            dy_str = str(dy).replace("Day ", "")
            clean_date = format_date_clean(latest_date_str)

            with col_g2:
                st.markdown(f"#### Latest Practice Metrics ({clean_date})")
                st.markdown(
                    f"""
                        <div style="margin-bottom: 12px; display: flex; gap: 10px;">
                            <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Minutes: {mins}</span>
                            <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Week {wk_str}</span>
                            <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Day {dy_str}</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_v_sc, col_i_sc, col_c_sc = st.columns(3)
                v_bg, v_fg = get_vball_color(vol_score)
                i_bg, i_fg = get_vball_color(int_score)
                c_bg, c_fg = get_vball_color(comb_score)

                with col_v_sc:
                    st.markdown(
                        f"""
                            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center;">
                                <div style="font-weight: 700; color: #64748B; font-size: 0.85rem;">VOLUME SCORE</div>
                                <div style="font-size: 1.8rem; font-weight: 800; padding: 4px 0; border-radius: 6px; background-color: {v_bg}; color: {v_fg}; margin-top: 4px;">{vol_score}</div>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_i_sc:
                    st.markdown(
                        f"""
                            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center;">
                                <div style="font-weight: 700; color: #64748B; font-size: 0.85rem;">INTENSITY SCORE</div>
                                <div style="font-size: 1.8rem; font-weight: 800; padding: 4px 0; border-radius: 6px; background-color: {i_bg}; color: {i_fg}; margin-top: 4px;">{int_score}</div>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_c_sc:
                    st.markdown(
                        f"""
                            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center;">
                                <div style="font-weight: 700; color: #58595B; font-size: 0.85rem;">COMBINED SCORE</div>
                                <div style="font-size: 1.8rem; font-weight: 800; padding: 4px 0; border-radius: 6px; background-color: {c_bg}; color: {c_fg}; margin-top: 4px;">{comb_score}</div>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )

            col_v_tbl, col_i_tbl = st.columns(2)
            with col_v_tbl:
                st.markdown('<div style="font-weight:700; font-size:0.9rem; margin: 10px 0 5px 0;">Volume Breakdown</div>', unsafe_allow_html=True)
                st.markdown(render_vball_table(vol_df), unsafe_allow_html=True)
            with col_i_tbl:
                st.markdown('<div style="font-weight:700; font-size:0.9rem; margin: 10px 0 5px 0;">Intensity Breakdown</div>', unsafe_allow_html=True)
                st.markdown(render_vball_table(int_df), unsafe_allow_html=True)

        st.divider()

        # SECTION 3: CMJ
        st.markdown(
            '<div class="vball-section-title">3. Jump Performance & RSI Tracking</div>',
            unsafe_allow_html=True,
        )

        p_cmj_ind = (
            cmj_data[cmj_data["Name"] == selected_player].sort_values("Date").copy()
            if not cmj_data.empty
            else pd.DataFrame()
        )
        jump_cols_ind = [c for c in p_cmj_ind.columns if "jump" in c.lower() or "height" in c.lower()]
        j_col_ind = jump_cols_ind[0] if jump_cols_ind else None
        rsi_cols_ind = [c for c in p_cmj_ind.columns if "rsi" in c.lower()]
        rsi_col_ind = rsi_cols_ind[0] if rsi_cols_ind else None

        if not p_cmj_ind.empty and j_col_ind:
            p_cmj_ind["Jump_Height_Clean"] = pd.to_numeric(
                p_cmj_ind[j_col_ind].astype(str).str.replace(r"[^0-9.]", "", regex=True),
                errors="coerce",
            )

            fig_jump_trend = go.Figure()
            fig_jump_trend.add_trace(
                go.Scatter(
                    x=p_cmj_ind["Date"],
                    y=p_cmj_ind["Jump_Height_Clean"],
                    name="Jump Height",
                    mode="lines+markers",
                    connectgaps=True,
                    yaxis="y",
                    line=dict(color="#FF8200", width=4),
                    marker=dict(size=8, color="#FF8200"),
                )
            )

            if rsi_col_ind:
                p_cmj_ind["RSI_Clean"] = pd.to_numeric(
                    p_cmj_ind[rsi_col_ind].astype(str).str.replace(r"[^0-9.]", "", regex=True),
                    errors="coerce",
                )
                fig_jump_trend.add_trace(
                    go.Scatter(
                        x=p_cmj_ind["Date"],
                        y=p_cmj_ind["RSI_Clean"],
                        name="RSI Modified",
                        mode="lines+markers",
                        connectgaps=True,
                        yaxis="y2",
                        line=dict(color="#38BDF8", width=3, dash="dot"),
                        marker=dict(size=8, color="#38BDF8"),
                    )
                )

            fig_jump_trend.update_layout(
                height=300,
                margin=dict(l=40, r=40, t=40, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.08,
                    xanchor="left",
                    x=0.01,
                    font=dict(size=13, color="#0F172A"),
                ),
                xaxis=dict(
                    title=None,
                    type="date",
                    tickformat="%b %d\n%Y",
                    showgrid=False,
                    showline=True,
                    linewidth=1.5,
                    linecolor="#0F172A",
                    tickfont=dict(color="#64748B", size=12),
                ),
                yaxis=dict(
                    showgrid=False,
                    showline=True,
                    linewidth=1.5,
                    linecolor="#0F172A",
                    tickfont=dict(color="#64748B", size=12),
                    side="left",
                ),
                yaxis2=dict(
                    showgrid=False,
                    showline=True,
                    linewidth=1.5,
                    linecolor="#0F172A",
                    tickfont=dict(color="#64748B", size=12),
                    overlaying="y",
                    side="right",
                    anchor="x",
                ),
            )
            st.plotly_chart(fig_jump_trend, use_container_width=True, key=f"jump_chart_{season_key}")

            with st.expander(f"View Raw CMJ Data Log for {selected_player} ({season_label})"):
                display_cols_ind = [
                    c for c in p_cmj_ind.columns if c not in ["Name", "Date_Str", "Jump_Height_Clean", "RSI_Clean"]
                ]
                st.markdown(render_vball_table(p_cmj_ind[display_cols_ind]), unsafe_allow_html=True)
        else:
            st.info(f"No CMJ jump data recorded for {selected_player} during {season_label}.")

        st.divider()

        # SECTION 4: WEEKLY DATA
        st.markdown(
            '<div class="vball-section-title">4. Weekly Output vs. Team Averages</div>',
            unsafe_allow_html=True,
        )

        p_weekly = (
            weekly_data[weekly_data["Player"] == selected_player]
            if not weekly_data.empty
            else pd.DataFrame()
        )
        t_weekly_avg = (
            (
                weekly_data.groupby("Week")
                .agg({
                    "Distance (mi)": "mean",
                    "High Speed Distance (mi)": "mean",
                    "Accels": "mean",
                    "Decels": "mean",
                })
                .reset_index()
            )
            if not weekly_data.empty
            else pd.DataFrame(
                columns=["Week", "Distance (mi)", "High Speed Distance (mi)", "Accels", "Decels"]
            )
        )

        all_weeks = t_weekly_avg["Week"].tolist() if not t_weekly_avg.empty else []

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_ind_td = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("Distance (mi)", []),
                p_weekly.get("Distance (mi)", []),
                f"Total Distance (mi) — {selected_player}",
                selected_player,
                "#FF8200",
            )
            st.plotly_chart(fig_ind_td, use_container_width=True, key=f"td_chart_{season_key}")

            fig_ind_aal = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("Accels", []),
                p_weekly.get("Accels", []),
                f"AAL — {selected_player}",
                selected_player,
                "#38BDF8",
            )
            st.plotly_chart(fig_ind_aal, use_container_width=True, key=f"aal_chart_{season_key}")

        with col_p2:
            fig_ind_hsd = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("High Speed Distance (mi)", []),
                p_weekly.get("High Speed Distance (mi)", []),
                f"High Speed Distance (mi) — {selected_player}",
                selected_player,
                "#FF8200",
            )
            st.plotly_chart(fig_ind_hsd, use_container_width=True, key=f"hsd_chart_{season_key}")

            fig_ind_dl = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("Decels", []),
                p_weekly.get("Decels", []),
                f"Decels — {selected_player}",
                selected_player,
                "#38BDF8",
            )
            st.plotly_chart(fig_ind_dl, use_container_width=True, key=f"dl_chart_{season_key}")

        st.divider()

        # SECTION 5: ATHLETE RECOVERY LOG
        st.markdown(
            '<div class="vball-section-title">5. Athlete Recovery Log & Duration Summary</div>',
            unsafe_allow_html=True,
        )

        local_now_rec_p = get_eastern_now()
        today_rec_p = local_now_rec_p.date()
        current_mon_rec_p = today_rec_p - datetime.timedelta(days=today_rec_p.weekday())

        c_rec_prof_wk, _ = st.columns([1, 2])
        with c_rec_prof_wk:
            sel_rec_prof_mon = st.date_input(
                "Select Recovery Week Starting (Monday):",
                value=current_mon_rec_p,
                key=f"ind_prof_rec_week_picker_{season_key}",
            )
            if sel_rec_prof_mon.weekday() != 0:
                sel_rec_prof_mon = sel_rec_prof_mon - datetime.timedelta(days=sel_rec_prof_mon.weekday())
            sel_rec_prof_mon_str = sel_rec_prof_mon.strftime("%Y-%m-%d")

        p_rec_rows = []
        if "recovery_local_state" in st.session_state and isinstance(st.session_state.recovery_local_state, dict):
            for r_key, dur_str in st.session_state.recovery_local_state.items():
                parts = r_key.split("|")
                if len(parts) == 4:
                    r_wk, r_ath, r_stn, r_day = parts[0], parts[1], parts[2], parts[3]
                    if r_ath.strip() == selected_player.strip() and r_wk.strip() == sel_rec_prof_mon_str:
                        dur_clean = pd.to_numeric(dur_str, errors="coerce")
                        dur_val = int(dur_clean) if pd.notna(dur_clean) else 0
                        p_rec_rows.append({
                            "Week_Starting": r_wk,
                            "Athlete": r_ath,
                            "Station": r_stn,
                            "Day": r_day,
                            "Duration_Minutes": dur_val,
                        })

        p_rec_df = pd.DataFrame(p_rec_rows) if p_rec_rows else pd.DataFrame(columns=["Week_Starting", "Athlete", "Station", "Day", "Duration_Minutes"])

        p_rec_count = len(p_rec_df)
        p_rec_duration = int(p_rec_df["Duration_Minutes"].sum()) if not p_rec_df.empty else 0
        p_top_stn = p_rec_df["Station"].value_counts().idxmax() if not p_rec_df.empty else "N/A"

        hrs_p = p_rec_duration // 60
        mins_p = p_rec_duration % 60
        p_time_str = f"{hrs_p}h {mins_p}m" if hrs_p > 0 else f"{mins_p}m"

        r_col1, r_col2, r_col3 = st.columns(3)
        with r_col1:
            st.metric("Total Stations Used", p_rec_count)
        with r_col2:
            st.metric("Total Recovery Duration", p_time_str, help=f"{p_rec_duration} minutes total")
        with r_col3:
            st.metric("Top Station", p_top_stn)

        days_order = [
            ("Monday", "Mon"),
            ("Tuesday", "Tue"),
            ("Wednesday", "Wed"),
            ("Thursday", "Thu"),
            ("Friday", "Fri"),
            ("Saturday", "Sat"),
            ("Sunday", "Sun"),
        ]

        if not p_rec_df.empty:
            day_stations_map = {}
            for _, row in p_rec_df.iterrows():
                raw_day = str(row.get("Day", ""))
                stn = str(row.get("Station", ""))
                dur = row.get("Duration_Minutes", 0)
                stn_display = f"{stn} ({dur}m)" if dur > 0 else stn
                day_key = next(
                    (full for full, _ in days_order if full in raw_day),
                    raw_day,
                )
                if day_key not in day_stations_map:
                    day_stations_map[day_key] = []
                day_stations_map[day_key].append(stn_display)

            days_grid_html = ""
            for full_day, short_day in days_order:
                stations_list = day_stations_map.get(full_day, [])

                if stations_list:
                    stations_html = "".join([
                        f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:3px solid #FF8200; border-radius:4px; padding:4px 8px; margin-top:4px; font-weight:700; color:#0F172A; font-size:0.78rem; text-align:center;">{stn}</div>'
                        for stn in stations_list
                    ])
                    card_style = "background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:10px; flex:1; min-width:0;"
                    header_color = "#FF8200"
                else:
                    stations_html = '<div style="color:#94A3B8; font-size:0.75rem; text-align:center; margin-top:8px; font-style:italic;">—</div>'
                    card_style = "background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px; flex:1; min-width:0;"
                    header_color = "#64748B"

                days_grid_html += (
                    f'<div style="{card_style}">'
                    f'<div style="font-weight:700; color:{header_color}; font-size:0.8rem; text-align:center; border-bottom:1px solid #E2E8F0; padding-bottom:4px; text-transform:uppercase;">{short_day}</div>'
                    f"{stations_html}"
                    "</div>"
                )

            ind_rec_card_html = (
                f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px; margin-top:14px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">'
                f'<div style="display:flex; gap:10px; width:100%;">{days_grid_html}</div>'
                f'</div>'
            )
            st.markdown(ind_rec_card_html, unsafe_allow_html=True)
        else:
            st.info(f"No recovery stations logged for {selected_player} during the week of {sel_rec_prof_mon_str}.")

        st.divider()

        # SECTION 6: LIVE TRACKING SUMMARY (Updated to 4 metrics)
        st.markdown(
            '<div class="vball-section-title">6. In-Practice Live Tracking Summary</div>',
            unsafe_allow_html=True,
        )

        ind_track_rows = []
        for k, v in st.session_state.tracking_data.items():
            parts = k.split("|")
            if len(parts) == 4 and v > 0:
                ind_track_rows.append({
                    "Week_Starting": parts[0],
                    "Date": parts[1],
                    "Athlete": parts[2],
                    "Metric": parts[3],
                    "Count": v
                })

        ind_track_df = pd.DataFrame(ind_track_rows) if ind_track_rows else pd.DataFrame(columns=["Week_Starting", "Date", "Athlete", "Metric", "Count"])
        p_ind_track = ind_track_df[ind_track_df["Athlete"] == selected_player] if not ind_track_df.empty else pd.DataFrame()

        local_now_ind = get_eastern_now()
        today_ind = local_now_ind.date()
        current_mon_ind = today_ind - datetime.timedelta(days=today_ind.weekday())

        c_tr_wk, _ = st.columns([1, 2])
        with c_tr_wk:
            sel_ind_mon = st.date_input(
                "Select Week Starting (Monday):",
                value=current_mon_ind,
                key=f"ind_prof_track_week_picker_{season_key}",
            )
            if sel_ind_mon.weekday() != 0:
                sel_ind_mon = sel_ind_mon - datetime.timedelta(days=sel_ind_mon.weekday())
            sel_ind_mon_str = sel_ind_mon.strftime("%Y-%m-%d")

        p_ind_track_wk = p_ind_track[p_ind_track["Week_Starting"] == sel_ind_mon_str] if not p_ind_track.empty else pd.DataFrame()

        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        to_total = p_ind_track_wk[p_ind_track_wk["Metric"] == "Turnover"]["Count"].sum() if not p_ind_track_wk.empty else 0
        nc_total = p_ind_track_wk[p_ind_track_wk["Metric"] == "Not Crashing"]["Count"].sum() if not p_ind_track_wk.empty else 0
        nbo_total = p_ind_track_wk[p_ind_track_wk["Metric"] == "No Box Out"]["Count"].sum() if not p_ind_track_wk.empty else 0
        ncb_total = p_ind_track_wk[p_ind_track_wk["Metric"] == "Not Calling Back"]["Count"].sum() if not p_ind_track_wk.empty else 0

        with t_col1:
            st.metric("Turnovers (Week)", int(to_total))
        with t_col2:
            st.metric("Not Crashing (Week)", int(nc_total))
        with t_col3:
            st.metric("No Box Outs (Week)", int(nbo_total))
        with t_col4:
            st.metric("Not Calling Back (Week)", int(ncb_total))

        if not p_ind_track_wk.empty:
            st.markdown(f"#### Daily Breakdown for Week of {sel_ind_mon_str}")
            pivot_ind_track = p_ind_track_wk.pivot_table(
                index="Metric",
                columns="Date",
                values="Count",
                aggfunc="sum",
                fill_value=0
            )
            pivot_ind_track["Total"] = pivot_ind_track.sum(axis=1)
            st.dataframe(pivot_ind_track, use_container_width=True)
        else:
            st.info(f"No in-practice tracking metrics logged for {selected_player} during the week of {sel_ind_mon_str}.")

        st.divider()

        # SECTION 7: ASSESSMENT RECORDS
        st.markdown(
            '<div class="vball-section-title">7. Additional Assessment Records</div>',
            unsafe_allow_html=True,
        )

        ind_records = []

        def get_formatted_peak(df_sub):
            if df_sub.empty:
                return None, None
            
            l_col = next((c for c in df_sub.columns if "l max force" in c.lower() or "left max" in c.lower()), None)
            r_col = next((c for c in df_sub.columns if "r max force" in c.lower() or "right max" in c.lower()), None)
            
            if l_col and r_col:
                df_sub["Peak_Val"] = df_sub[[l_col, r_col]].apply(pd.to_numeric, errors="coerce").max(axis=1)
                valid_rows = df_sub.dropna(subset=["Peak_Val"])
                if valid_rows.empty:
                    return None, None
                
                best_row = valid_rows.sort_values("Peak_Val", ascending=False).iloc[0]
                l_val = pd.to_numeric(best_row[l_col], errors="coerce")
                r_val = pd.to_numeric(best_row[r_col], errors="coerce")
                
                l_str = f"{l_val:.1f} N" if pd.notna(l_val) else "N/A"
                r_str = f"{r_val:.1f} N" if pd.notna(r_val) else "N/A"
                
                return f"{l_str} / {r_str}", format_date_clean(best_row.get("Date"))
            else:
                return None, None

        # 1. Knee
        p_knee_ind = knee_data[knee_data["Name"] == selected_player].copy() if not knee_data.empty and "Name" in knee_data.columns else pd.DataFrame()
        if not p_knee_ind.empty:
            dir_col = next((c for c in p_knee_ind.columns if "direction" in c.lower() or "test" in c.lower()), None)
            ke_df = p_knee_ind[p_knee_ind[dir_col].astype(str).str.contains("Extension", case=False, na=False)] if dir_col else p_knee_ind
            kf_df = p_knee_ind[p_knee_ind[dir_col].astype(str).str.contains("Flexion", case=False, na=False)] if dir_col else pd.DataFrame()

            val, dt = get_formatted_peak(ke_df)
            if val:
                ind_records.append({"Assessment": "Knee Extension (L/R)", "Peak Value": val, "Date": dt})

            val, dt = get_formatted_peak(kf_df)
            if val:
                ind_records.append({"Assessment": "Knee Flexion (L/R)", "Peak Value": val, "Date": dt})

        # 2. Hip
        p_hip_ind = hip_data[hip_data["Name"] == selected_player].copy() if not hip_data.empty and "Name" in hip_data.columns else pd.DataFrame()
        if not p_hip_ind.empty:
            dir_col = next((c for c in p_hip_ind.columns if "direction" in c.lower() or "test" in c.lower()), None)
            ad_df = p_hip_ind[p_hip_ind[dir_col].astype(str).str.contains("AD|Adduction", case=False, na=False)] if dir_col else p_hip_ind
            ab_df = p_hip_ind[p_hip_ind[dir_col].astype(str).str.contains("AB|Abduction", case=False, na=False)] if dir_col else pd.DataFrame()

            val, dt = get_formatted_peak(ad_df)
            if val:
                ind_records.append({"Assessment": "Hip Adduction (L/R)", "Peak Value": val, "Date": dt})

            val, dt = get_formatted_peak(ab_df)
            if val:
                ind_records.append({"Assessment": "Hip Abduction (L/R)", "Peak Value": val, "Date": dt})

        # 3. NordBord
        p_nord_ind = nordic_data[nordic_data["Name"] == selected_player].copy() if not nordic_data.empty and "Name" in nordic_data.columns else pd.DataFrame()
        if not p_nord_ind.empty:
            t_c = next((c for c in p_nord_ind.columns if "test" in c.lower()), None)
            if t_c:
                for test_type_val in p_nord_ind[t_c].dropna().unique():
                    sub_df = p_nord_ind[p_nord_ind[t_c] == test_type_val]
                    val, dt = get_formatted_peak(sub_df)
                    if val:
                        ind_records.append({"Assessment": f"NordBord ({test_type_val}) (L/R)", "Peak Value": val, "Date": dt})
            else:
                val, dt = get_formatted_peak(p_nord_ind)
                if val:
                    ind_records.append({"Assessment": "NordBord Hamstring (L/R)", "Peak Value": val, "Date": dt})

        # 4. Harness Belt Squat
        p_bs_ind = belt_squat_data[belt_squat_data["Name"] == selected_player].copy() if not belt_squat_data.empty and "Name" in belt_squat_data.columns else pd.DataFrame()
        if not p_bs_ind.empty:
            f_c = next((c for c in p_bs_ind.columns if "peak vertical force" in c.lower() or "force" in c.lower()), None)
            if f_c:
                p_bs_ind["PVF"] = pd.to_numeric(p_bs_ind[f_c].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
                valid_bs = p_bs_ind.dropna(subset=["PVF"])
                if not valid_bs.empty:
                    best_bs = valid_bs.sort_values("PVF", ascending=False).iloc[0]
                    ind_records.append({"Assessment": "Harness Belt Squat", "Peak Value": f"{best_bs['PVF']:.1f} N", "Date": format_date_clean(best_bs.get("Date"))})

        # 5. Ankle
        p_ank_ind = ankle_data[ankle_data["Name"] == selected_player].copy() if not ankle_data.empty and "Name" in ankle_data.columns else pd.DataFrame()
        if not p_ank_ind.empty:
            val, dt = get_formatted_peak(p_ank_ind)
            if val:
                ind_records.append({"Assessment": "Ankle Plantar Flexion (L/R)", "Peak Value": val, "Date": dt})

        if ind_records:
            st.markdown(render_vball_table(pd.DataFrame(ind_records)), unsafe_allow_html=True)
        else:
            st.info(f"No additional assessment logs found for {selected_player} in {season_label}.")

    # TAB 2: PRACTICE SCORE
    elif main_tab == "Practice Score":
        c_d, _ = st.columns([1, 3])
        with c_d:
            available_dates = (
                vol_data["Date_Str"].sort_values(ascending=False).unique()
                if not vol_data.empty
                else []
            )
            session_date = st.selectbox("Select Session Date:", available_dates, format_func=format_date_clean, key=f"sel_ps_date_{season_key}")

        st.markdown("<br>", unsafe_allow_html=True)

        for player_name in roster_players:
            p_row = (
                roster_raw[roster_raw["Name"] == player_name]
                if not roster_raw.empty
                else pd.DataFrame()
            )
            p_pos = (
                p_row["Position"].values[0]
                if not p_row.empty
                else "Guard / Forward"
            )
            p_img = (
                p_row["Picture"].values[0]
                if not p_row.empty
                else "https://via.placeholder.com/70"
            )

            vol_df, int_df, vol_score, int_score, comb_score, mins, wk, dy = (
                compute_practice_tables(player_name, str(session_date), vol_data, int_data)
            )

            vol_html_table = render_vball_table(vol_df)
            int_html_table = render_vball_table(int_df)

            v_bg, v_fg = get_vball_color(vol_score)
            i_bg, i_fg = get_vball_color(int_score)
            c_bg, c_fg = get_vball_color(comb_score)

            wk_str = str(wk).replace("Week ", "")
            dy_str = str(dy).replace("Day ", "")

            single_box_card_html = f"""
            <div class="practice-score-card" style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <img src="{p_img}" style="width:50px; height:50px; border-radius:50%; border:3px solid #FF8200; object-fit:cover;">
                        <div>
                            <h3 style="margin:0; font-size:1.15rem; color:#0F172A; font-weight:700;">{player_name}</h3>
                            <span style="color:#64748B; font-size:0.8rem;">{p_pos}</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.75rem;">Minutes: {mins}</span>
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.75rem;">Week {wk_str}</span>
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.75rem;">Day {dy_str}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 16px; width: 100%;">
                    <div style="flex: 1; min-width: 0;">
                        <div class="vball-section-title" style="background-color:#38BDF8; color:#0F172A; font-weight:700; font-size:0.85rem; padding:4px 8px; border-radius:6px; text-align:center; margin-bottom:8px; text-transform:uppercase;">Volume Metrics</div>
                        {vol_html_table}
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:6px; text-align:center; margin-top:6px;">
                            <div style="font-weight:700; color:#64748B; font-size:0.75rem;">VOLUME SCORE</div>
                            <div style="font-size:1.4rem; font-weight:800; padding:2px 0; border-radius:6px; background-color:{v_bg}; color:{v_fg}; margin-top:2px;">{vol_score}</div>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 0;">
                        <div class="vball-section-title" style="background-color:#38BDF8; color:#0F172A; font-weight:700; font-size:0.85rem; padding:4px 8px; border-radius:6px; text-align:center; margin-bottom:8px; text-transform:uppercase;">Intensity Metrics</div>
                        {int_html_table}
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:6px; text-align:center; margin-top:6px;">
                            <div style="font-weight:700; color:#64748B; font-size:0.75rem;">INTENSITY SCORE</div>
                            <div style="font-size:1.4rem; font-weight:800; padding:2px 0; border-radius:6px; background-color:{i_bg}; color:{i_fg}; margin-top:2px;">{int_score}</div>
                        </div>
                    </div>
                </div>
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:6px; text-align:center; margin-top:10px;">
                    <div style="font-weight:700; color:58595B; font-size:0.75rem;">COMBINED PRACTICE SCORE</div>
                    <div style="font-size:1.4rem; font-weight:800; padding:2px 0; border-radius:6px; background-color:{c_bg}; color:{c_fg}; margin-top:2px; max-width: 200px; margin-left: auto; margin-right: auto;">{comb_score}</div>
                </div>
            </div>
            """
            st.markdown(single_box_card_html, unsafe_allow_html=True)

    # TAB 3: COMPLIANCE
    elif main_tab == "Compliance":
        st.markdown(
            '<div class="vball-section-title">Team Performance Compliance Matrix</div>',
            unsafe_allow_html=True,
        )

        selected_player_comp = st.selectbox(
            "Select Athlete Compliance Overview:", roster_players, key=f"sel_comp_player_{season_key}"
        )

        p_row = (
            roster_raw[roster_raw["Name"] == selected_player_comp]
            if not roster_raw.empty
            else pd.DataFrame()
        )
        p_pos = (
            p_row["Position"].values[0]
            if not p_row.empty
            else "Guard / Forward | #00"
        )
        p_img = (
            p_row["Picture"].values[0]
            if not p_row.empty
            else "https://via.placeholder.com/60"
        )

        p_comp = (
            comp_data[comp_data["Player"] == selected_player_comp].sort_values("Date")
            if not comp_data.empty
            else pd.DataFrame()
        )

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 15px; background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 12px 16px; margin-bottom: 20px;">
                <img src="{p_img}" class="athlete-avatar" style="width:50px; height:50px;">
                <div>
                    <h3 style="margin:0; font-size:1.2rem; color:#0F172A; font-weight:700;">{selected_player_comp}</h3>
                    <span style="color:#64748B; font-size:0.85rem;">{p_pos}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for row_idx in range(0, len(compliance_metrics), 2):
            col1, col2 = st.columns(2)
            cols = [col1, col2]
            for j in range(2):
                metric_idx = row_idx + j
                if metric_idx < len(compliance_metrics):
                    col_name, display_title, unit = compliance_metrics[metric_idx]
                    subcard_html = render_metric_subcard_html(p_comp, col_name, display_title, unit)
                    with cols[j]:
                        st.markdown(subcard_html, unsafe_allow_html=True)

    # TAB 4: WEEKLY DATA
    elif main_tab == "Weekly Data":
        st.markdown(
            '<div class="vball-section-title">1. Team Weekly Accumulation Overview</div>',
            unsafe_allow_html=True,
        )

        weekly_agg = (
            (
                weekly_data.groupby("Week")
                .agg({
                    "Distance (mi)": "sum",
                    "High Speed Distance (mi)": "sum",
                    "Accels": "sum",
                    "Decels": "sum",
                })
                .reset_index()
            )
            if not weekly_data.empty
            else pd.DataFrame(
                columns=["Week", "Distance (mi)", "High Speed Distance (mi)", "Accels", "Decels"]
            )
        )

        weeks = weekly_agg["Week"].tolist() if not weekly_agg.empty else []

        w1, w2 = st.columns(2)
        with w1:
            fig_td = create_clean_bar_chart(
                weeks,
                weekly_agg.get("Distance (mi)", []),
                "Total Distance (mi)",
                "#38BDF8",
            )
            st.plotly_chart(fig_td, use_container_width=True, key=f"wk_td_{season_key}")

            fig_aal = create_clean_bar_chart(
                weeks,
                weekly_agg.get("Accels", []),
                "Accels",
                "#FF8200",
            )
            st.plotly_chart(fig_aal, use_container_width=True, key=f"wk_aal_{season_key}")

        with w2:
            fig_hsd = create_clean_bar_chart(
                weeks,
                weekly_agg.get("High Speed Distance (mi)", []),
                "High Speed Distance (mi)",
                "#38BDF8",
            )
            st.plotly_chart(fig_hsd, use_container_width=True, key=f"wk_hsd_{season_key}")

            fig_dl = create_clean_bar_chart(
                weeks,
                weekly_agg.get("Decels", []),
                "Decels",
                "#FF8200",
            )
            st.plotly_chart(fig_dl, use_container_width=True, key=f"wk_dl_{season_key}")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="vball-section-title">2. Individual Player Breakdown vs. Team Average</div>',
            unsafe_allow_html=True,
        )
        selected_player_w = st.selectbox("Select Athlete:", roster_players, key=f"sel_wk_player_{season_key}")

        p_weekly = (
            weekly_data[weekly_data["Player"] == selected_player_w]
            if not weekly_data.empty
            else pd.DataFrame()
        )
        t_weekly_avg = (
            (
                weekly_data.groupby("Week")
                .agg({
                    "Distance (mi)": "mean",
                    "High Speed Distance (mi)": "mean",
                    "Accels": "mean",
                    "Decels": "mean",
                })
                .reset_index()
            )
            if not weekly_data.empty
            else pd.DataFrame(
                columns=["Week", "Distance (mi)", "High Speed Distance (mi)", "Accels", "Decels"]
            )
        )

        all_weeks = t_weekly_avg["Week"].tolist() if not t_weekly_avg.empty else []

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_ind_td = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("Distance (mi)", []),
                p_weekly.get("Distance (mi)", []),
                f"Total Distance (mi) — {selected_player_w}",
                selected_player_w,
                "#FF8200",
            )
            st.plotly_chart(fig_ind_td, use_container_width=True, key=f"ind_td_{season_key}")

            fig_ind_aal = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("Accels", []),
                p_weekly.get("Accels", []),
                f"AAL — {selected_player_w}",
                selected_player_w,
                "#38BDF8",
            )
            st.plotly_chart(fig_ind_aal, use_container_width=True, key=f"ind_aal_{season_key}")

        with col_p2:
            fig_ind_hsd = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("High Speed Distance (mi)", []),
                p_weekly.get("High Speed Distance (mi)", []),
                f"High Speed Distance (mi) — {selected_player_w}",
                selected_player_w,
                "#FF8200",
            )
            st.plotly_chart(fig_ind_hsd, use_container_width=True, key=f"ind_hsd_{season_key}")

            fig_ind_dl = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg.get("Decels", []),
                p_weekly.get("Decels", []),
                f"Decels — {selected_player_w}",
                selected_player_w,
                "#38BDF8",
            )
            st.plotly_chart(fig_ind_dl, use_container_width=True, key=f"ind_dl_{season_key}")

    # TAB 5: TESTING
    elif main_tab == "Testing":
        testing_tab_intake, testing_tab_cmj, testing_tab_overall = st.tabs(
            ["Intake Assessment", "CMJ", "Overall Profile"]
        )

        with testing_tab_intake:
            st.markdown(
                f"<h3 style='color:#1D1D1F; font-weight:900; text-transform:uppercase;'>Athlete Intake Assessment ({season_label})</h3>",
                unsafe_allow_html=True,
            )
            c_int_ath, _ = st.columns([2, 2])
            with c_int_ath:
                selected_intake_athlete = st.selectbox(
                    "Select Athlete for Intake Assessment",
                    roster_players,
                    key=f"intake_ath_select_{season_key}",
                )

            calf_ath = ankle_data[ankle_data["Name"] == selected_intake_athlete].sort_values("Date") if not ankle_data.empty and "Name" in ankle_data.columns else pd.DataFrame()
            hip_ath = hip_data[hip_data["Name"] == selected_intake_athlete].sort_values("Date") if not hip_data.empty and "Name" in hip_data.columns else pd.DataFrame()
            sh_ath = knee_data[knee_data["Name"] == selected_intake_athlete].sort_values("Date") if not knee_data.empty and "Name" in knee_data.columns else pd.DataFrame()
            nord_ath = nordic_data[nordic_data["Name"] == selected_intake_athlete].sort_values("Date") if not nordic_data.empty and "Name" in nordic_data.columns else pd.DataFrame()
            bs_ath = belt_squat_data[belt_squat_data["Name"] == selected_intake_athlete].sort_values("Date") if not belt_squat_data.empty and "Name" in belt_squat_data.columns else pd.DataFrame()

            has_data = not (calf_ath.empty and hip_ath.empty and sh_ath.empty and nord_ath.empty and bs_ath.empty)

            def render_val_with_arrow(current, initial, fmt="{:.1f}", unit=""):
                if initial == 0:
                    return f"{fmt.format(current)}{unit}"
                diff = current - initial
                pct = (diff / initial) * 100
                arrow = "↑" if diff >= 0 else "↓"
                color = "#28a745" if diff >= 0 else "#dc3545"
                return f"{fmt.format(current)}{unit} <span style='color:{color}; font-size:11px; font-weight:bold;'>({arrow}{abs(pct):.1f}%)</span>"

            def get_peak_and_recent_row(df_sub, l_col, r_col):
                if df_sub.empty or not l_col or not r_col:
                    return (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)
                
                df_calc = df_sub.copy()
                df_calc["L_Val"] = pd.to_numeric(df_calc[l_col], errors="coerce").fillna(0.0)
                df_calc["R_Val"] = pd.to_numeric(df_calc[r_col], errors="coerce").fillna(0.0)
                df_calc["Max_Val"] = df_calc[["L_Val", "R_Val"]].max(axis=1)
                
                valid_rows = df_calc[df_calc["Max_Val"] > 0]
                if valid_rows.empty:
                    return (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)
                
                peak_row = valid_rows.sort_values("Max_Val", ascending=False).iloc[0]
                max_L, max_R = peak_row["L_Val"], peak_row["R_Val"]
                
                recent_row = valid_rows.sort_values("Date", ascending=True).iloc[-1]
                rec_L, rec_R = recent_row["L_Val"], recent_row["R_Val"]
                
                init_row = valid_rows.sort_values("Date", ascending=True).iloc[0]
                init_L, init_R = init_row["L_Val"], init_row["R_Val"]
                
                return (max_L, max_R), (rec_L, rec_R), (init_L, init_R)

            hud_col1, hud_col2 = st.columns([1.2, 1.8])

            with hud_col1:
                hud_svg_html = """
                <div style="background:#FFFFFF; border-radius:16px; padding:16px; border:1px solid #E5E5E7; box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                    <div style="color:#1D1D1F; font-weight:800; font-size:13px; letter-spacing:1px; text-transform:uppercase; border-bottom:2px solid #FF8200; padding-bottom:6px; margin-bottom:12px;">ANATOMY LOCATION MAP</div>
                    <div style="position:relative; width:100%; height:460px; background:#FAFDFD; border-radius:12px; border:1px solid #D5E5E8; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                        <svg viewBox="0 0 160 220" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                            <defs>
                                <linearGradient id="anatomicalBodyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stop-color="#C5CACC" />
                                    <stop offset="25%" stop-color="#E8ECEE" />
                                    <stop offset="50%" stop-color="#F2F5F7" />
                                    <stop offset="75%" stop-color="#D0D5D8" />
                                    <stop offset="100%" stop-color="#9AA0A6" />
                                </linearGradient>
                            </defs>
                            <ellipse cx="68" cy="214" rx="20" ry="3.5" fill="#000000" opacity="0.12" />
                            <g stroke="#2C3036" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                                <ellipse cx="68" cy="17" rx="7" ry="9" fill="url(#anatomicalBodyGrad)" />
                                <path d="M 65 25 L 63 33 M 71 25 L 73 33" stroke-width="1.2" />
                                <path d="M 63 33 C 58 33, 48 36, 42 40 C 37 43, 36 50, 39 56 L 43 56 C 47 52, 49 46, 52 44 M 73 33 C 78 33, 88 36, 94 40 C 99 43, 100 50, 97 56 L 93 56 C 89 52, 87 46, 84 44" fill="url(#anatomicalBodyGrad)" />
                                <path d="M 42 40 C 37 43, 35 52, 33 64 C 31 74, 29 82, 27 92 C 25 96, 23 100, 22 104 C 21 106, 23 107, 25 106 C 27 104, 28 98, 30 92 C 33 82, 36 74, 38 64 C 40 54, 42 48, 43 56 Z" fill="url(#anatomicalBodyGrad)" />
                                <path d="M 22 104 C 20 106, 18 108, 17 110 M 23 105 C 21 108, 20 110, 19 112 M 24 105 C 23 108, 22 110, 21 112 M 25 104 C 25 107, 24 109, 23 111" fill="none" stroke-width="0.8" />
                                <path d="M 94 40 C 99 43, 101 52, 103 64 C 105 74, 107 82, 109 92 C 111 96, 113 100, 114 104 C 115 106, 113 107, 111 106 C 109 104, 108 98, 106 92 C 103 82, 100 74, 98 64 C 96 54, 94 48, 93 56 Z" fill="url(#anatomicalBodyGrad)" />
                                <path d="M 114 104 C 116 106, 118 108, 119 110 M 113 105 C 115 108, 116 110, 117 112 M 112 105 C 113 108, 114 110, 115 112 M 111 104 C 111 107, 112 109, 113 111" fill="none" stroke-width="0.8" />
                                <path d="M 52 44 L 54 75 L 52 92 L 68 106 L 84 92 L 82 75 L 84 44 Z" fill="url(#anatomicalBodyGrad)" />
                                <path d="M 52 92 C 50 105, 49 122, 53 138 C 55 144, 55 152, 54 162 C 52 175, 52 192, 54 205 L 48 210 L 58 210 L 59 203 C 60 190, 60 175, 60 162 C 60 152, 60 144, 62 138 C 66 122, 66 105, 68 106 Z" fill="url(#anatomicalBodyGrad)" />
                                <path d="M 84 92 C 86 105, 87 122, 83 138 C 81 144, 81 152, 82 162 C 84 175, 84 192, 82 205 L 88 210 L 78 210 L 77 203 C 76 190, 76 175, 76 162 C 76 152, 76 144, 74 138 C 70 122, 70 105, 68 106 Z" fill="url(#anatomicalBodyGrad)" />
                                <line x1="68" y1="8" x2="68" y2="211" stroke="#FF8200" stroke-width="1.3" />
                                <line x1="51" y1="116" x2="85" y2="116" stroke="#D32F2F" stroke-width="1.1" />
                                <line x1="55" y1="168" x2="81" y2="168" stroke="#D32F2F" stroke-width="1.1" />
                            </g>
                            <line x1="82" y1="58" x2="112" y2="58" stroke="#FF8200" stroke-width="2" stroke-dasharray="2 2" />
                            <circle cx="82" cy="58" r="4" fill="#FF8200" stroke="#FFFFFF" stroke-width="1.2" />
                            <rect x="112" y="50" width="16" height="16" rx="4" fill="#FF8200" />
                            <text x="120" y="62" font-size="10" font-weight="900" fill="#FFFFFF" text-anchor="middle">1</text>
                            <line x1="58" y1="116" x2="24" y2="116" stroke="#4895DB" stroke-width="2" stroke-dasharray="2 2" />
                            <circle cx="58" cy="116" r="4" fill="#4895DB" stroke="#FFFFFF" stroke-width="1.2" />
                            <rect x="8" y="108" width="16" height="16" rx="4" fill="#4895DB" />
                            <text x="16" y="120" font-size="10" font-weight="900" fill="#FFFFFF" text-anchor="middle">2</text>
                            <line x1="74" y1="172" x2="112" y2="172" stroke="#4895DB" stroke-width="2" stroke-dasharray="2 2" />
                            <circle cx="74" cy="172" r="4" fill="#4895DB" stroke="#FFFFFF" stroke-width="1.2" />
                            <rect x="112" y="164" width="16" height="16" rx="4" fill="#4895DB" />
                            <text x="120" y="176" font-size="10" font-weight="900" fill="#FFFFFF" text-anchor="middle">3</text>
                            <line x1="60" y1="140" x2="24" y2="140" stroke="#FF8200" stroke-width="2" stroke-dasharray="2 2" />
                            <circle cx="60" cy="140" r="4" fill="#FF8200" stroke="#FFFFFF" stroke-width="1.2" />
                            <rect x="8" y="132" width="16" height="16" rx="4" fill="#FF8200" />
                            <text x="16" y="144" font-size="10" font-weight="900" fill="#FFFFFF" text-anchor="middle">4</text>
                            <line x1="68" y1="84" x2="112" y2="84" stroke="#4895DB" stroke-width="2" stroke-dasharray="2 2" />
                            <circle cx="68" cy="84" r="4" fill="#4895DB" stroke="#FFFFFF" stroke-width="1.2" />
                            <rect x="112" y="76" width="16" height="16" rx="4" fill="#4895DB" />
                            <text x="120" y="88" font-size="10" font-weight="900" fill="#FFFFFF" text-anchor="middle">5</text>
                        </svg>
                    </div>
                </div>
                """
                components.html(hud_svg_html, height=520)

            with hud_col2:
                st.markdown(
                    f"""
                    <style>
                    .hud-details-card {{ background: #FFFFFF; border-radius: 16px; padding: 20px; border: 1px solid #E5E5E7; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }}
                    .hud-header-title-light {{ color: #1D1D1F; font-weight: 800; font-size: 13px; letter-spacing: 1px; text-transform: uppercase; border-bottom: 2px solid #FF8200; padding-bottom: 6px; margin-bottom: 16px; }}
                    .hud-metric-row-light {{ background: #F8F9FA; border-left: 4px solid #FF8200; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; color: #1D1D1F; border: 1px solid #E5E5E7; border-left: 4px solid #FF8200; }}
                    .hud-metric-row-light-blue {{ background: #F8F9FA; border-left: 4px solid #4895DB; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; color: #1D1D1F; border: 1px solid #E5E5E7; border-left: 4px solid #4895DB; }}
                    .node-badge-orange {{ display: inline-block; width: 20px; height: 20px; background: #FF8200; color: #FFFFFF; font-weight: 900; font-size: 11px; border-radius: 4px; text-align: center; line-height: 20px; margin-right: 8px; }}
                    .node-badge-blue {{ display: inline-block; width: 20px; height: 20px; background: #4895DB; color: #FFFFFF; font-weight: 900; font-size: 11px; border-radius: 4px; text-align: center; line-height: 20px; margin-right: 8px; }}
                    </style>
                    <div class="hud-details-card">
                        <div class="hud-header-title-light">Location Assessment ({season_label})</div>
                    """,
                    unsafe_allow_html=True,
                )

                if has_data:
                    if not sh_ath.empty:
                        l_col = next((c for c in sh_ath.columns if "l max force" in c.lower() or "left max" in c.lower()), None)
                        r_col = next((c for c in sh_ath.columns if "r max force" in c.lower() or "right max" in c.lower()), None)
                        dir_c = next((c for c in sh_ath.columns if "direction" in c.lower() or "test" in c.lower()), None)
                        knee_ext = sh_ath[sh_ath[dir_c].astype(str).str.contains("Extension", case=False, na=False)] if dir_c else sh_ath
                        knee_flx = sh_ath[sh_ath[dir_c].astype(str).str.contains("Flexion", case=False, na=False)] if dir_c else sh_ath

                        (ke_maxL, ke_maxR), (ke_recL, ke_recR), (ke_initL, ke_initR) = get_peak_and_recent_row(knee_ext, l_col, r_col)
                        (kf_maxL, kf_maxR), (kf_recL, kf_recR), (kf_initL, kf_initR) = get_peak_and_recent_row(knee_flx, l_col, r_col)
                        latest_date_str = format_date_clean(knee_ext.sort_values("Date").iloc[-1].get("Date")) if not knee_ext.empty else "N/A"

                        st.markdown(
                            f"""
                            <div class="hud-metric-row-light">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                    <span style="font-weight:800; font-size:12px; color:#1D1D1F;"><span class="node-badge-orange">1</span>KNEE EXTENSION & FLEXION</span>
                                    <span style="font-size:10px; color:#6E6E73; font-weight:600;">Latest: {latest_date_str}</span>
                                </div>
                                <div style="font-size:11px; line-height:1.4; color:#1D1D1F;">
                                    <b>Extension:</b> Max L {ke_maxL:.1f}N | R {ke_maxR:.1f}N &nbsp;→&nbsp; <b>Recent:</b> L {render_val_with_arrow(ke_recL, ke_initL, '{:.1f}', 'N')} | R {render_val_with_arrow(ke_recR, ke_initR, '{:.1f}', 'N')}<br>
                                    <b>Flexion:</b> Max L {kf_maxL:.1f}N | R {kf_maxR:.1f}N &nbsp;→&nbsp; <b>Recent:</b> L {render_val_with_arrow(kf_recL, kf_initL, '{:.1f}', 'N')} | R {render_val_with_arrow(kf_recR, kf_initR, '{:.1f}', 'N')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if not hip_ath.empty:
                        l_col = next((c for c in hip_ath.columns if "l max force" in c.lower() or "left max" in c.lower()), None)
                        r_col = next((c for c in hip_ath.columns if "r max force" in c.lower() or "right max" in c.lower()), None)
                        dir_col = next((c for c in hip_ath.columns if "direction" in c.lower() or "test" in c.lower()), None)
                        hip_ad = hip_ath[hip_ath[dir_col].astype(str).str.contains("AD|Adduction", case=False, na=False)] if dir_col else hip_ath
                        hip_ab = hip_ath[hip_ath[dir_col].astype(str).str.contains("AB|Abduction", case=False, na=False)] if dir_col else hip_ath

                        (ad_maxL, ad_maxR), (ad_recL, ad_recR), (ad_initL, ad_initR) = get_peak_and_recent_row(hip_ad, l_col, r_col)
                        (ab_maxL, ab_maxR), (ab_recL, ab_recR), (ab_initL, ab_initR) = get_peak_and_recent_row(hip_ab, l_col, r_col)
                        date_str = format_date_clean(hip_ath.sort_values("Date").iloc[-1].get("Date")) if not hip_ath.empty else "N/A"

                        st.markdown(
                            f"""
                            <div class="hud-metric-row-light-blue">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                    <span style="font-weight:800; font-size:12px; color:#1D1D1F;"><span class="node-badge-blue">2</span>HIP ADDUCTION & ABDUCTION</span>
                                    <span style="font-size:10px; color:#6E6E73; font-weight:600;">Latest: {date_str}</span>
                                </div>
                                <div style="font-size:11px; line-height:1.4; color:#1D1D1F;">
                                    <b>Hip Adduction:</b> Max L {ad_maxL:.1f}N | R {ad_maxR:.1f}N &nbsp;→&nbsp; <b>Recent:</b> L {render_val_with_arrow(ad_recL, ad_initL, '{:.1f}', 'N')} | R {render_val_with_arrow(ad_recR, ad_initR, '{:.1f}', 'N')}<br>
                                    <b>Hip Abduction:</b> Max L {ab_maxL:.1f}N | R {ab_maxR:.1f}N &nbsp;→&nbsp; <b>Recent:</b> L {render_val_with_arrow(ab_recR, ad_initR, '{:.1f}', 'N')} | R {render_val_with_arrow(ab_recR, ad_initR, '{:.1f}', 'N')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if not calf_ath.empty:
                        l_col = next((c for c in calf_ath.columns if "l max force" in c.lower() or "left max" in c.lower()), None)
                        r_col = next((c for c in calf_ath.columns if "r max force" in c.lower() or "right max" in c.lower()), None)
                        (ank_maxL, ank_maxR), (ank_recL, ank_recR), (ank_initL, ank_initR) = get_peak_and_recent_row(calf_ath, l_col, r_col)
                        date_str = format_date_clean(calf_ath.sort_values("Date").iloc[-1].get("Date")) if not calf_ath.empty else "N/A"

                        st.markdown(
                            f"""
                            <div class="hud-metric-row-light-blue">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                    <span style="font-weight:800; font-size:12px; color:#1D1D1F;"><span class="node-badge-blue">3</span>ANKLE PLANTAR FLEXION</span>
                                    <span style="font-size:10px; color:#6E6E73; font-weight:600;">Latest: {date_str}</span>
                                </div>
                                <div style="font-size:11px; line-height:1.4; color:#1D1D1F;">
                                    <b>Max Force:</b> L {ank_maxL:.1f}N | R {ank_maxR:.1f}N &nbsp;→&nbsp; <b>Recent:</b> L {render_val_with_arrow(ank_recL, ank_initL, '{:.1f}', 'N')} | R {render_val_with_arrow(ank_recR, ank_initR, '{:.1f}', 'N')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if not nord_ath.empty:
                        l_col = next((c for c in nord_ath.columns if "l max force" in c.lower() or "left max" in c.lower()), None)
                        r_col = next((c for c in nord_ath.columns if "r max force" in c.lower() or "right max" in c.lower()), None)
                        (nord_maxL, nord_maxR), (nord_recL, nord_recR), (nord_initL, nord_initR) = get_peak_and_recent_row(nord_ath, l_col, r_col)
                        date_str = format_date_clean(nord_ath.sort_values("Date").iloc[-1].get("Date")) if not nord_ath.empty else "N/A"

                        st.markdown(
                            f"""
                            <div class="hud-metric-row-light">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                    <span style="font-weight:800; font-size:12px; color:#1D1D1F;"><span class="node-badge-orange">4</span>NORDBORD HAMSTRING</span>
                                    <span style="font-size:10px; color:#6E6E73; font-weight:600;">Latest: {date_str}</span>
                                </div>
                                <div style="font-size:11px; line-height:1.4; color:#1D1D1F;">
                                    <b>Peak Force:</b> L {nord_maxL:.1f}N | R {nord_maxR:.1f}N &nbsp;→&nbsp; <b>Recent:</b> L {render_val_with_arrow(nord_recL, nord_initL, '{:.1f}', 'N')} | R {render_val_with_arrow(nord_recR, nord_initR, '{:.1f}', 'N')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if not bs_ath.empty:
                        f_c = next((c for c in bs_ath.columns if "peak vertical force" in c.lower() or "force" in c.lower()), None)
                        if f_c:
                            bs_ath["PVF_Calc"] = pd.to_numeric(bs_ath[f_c].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce").fillna(0.0)
                            peak_bs_val = bs_ath["PVF_Calc"].max()
                            rec_bs_val = bs_ath.sort_values("Date").iloc[-1]["PVF_Calc"]
                            init_bs_val = bs_ath.sort_values("Date").iloc[0]["PVF_Calc"]
                            date_str = format_date_clean(bs_ath.sort_values("Date").iloc[-1].get("Date"))

                            st.markdown(
                                f"""
                                <div class="hud-metric-row-light-blue">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                        <span style="font-weight:800; font-size:12px; color:#1D1D1F;"><span class="node-badge-blue">5</span>HARNESS BELT SQUAT</span>
                                        <span style="font-size:10px; color:#6E6E73; font-weight:600;">Latest: {date_str}</span>
                                    </div>
                                    <div style="font-size:11px; line-height:1.4; color:#1D1D1F;">
                                        <b>Peak Vertical Force:</b> Max {peak_bs_val:.1f}N &nbsp;→&nbsp; <b>Recent:</b> {render_val_with_arrow(rec_bs_val, init_bs_val, '{:.1f}', 'N')}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                else:
                    st.info(f"No Intake Assessment records found for {selected_intake_athlete} in {season_label}.")

                st.markdown("</div>", unsafe_allow_html=True)

            st.divider()

            st.markdown(f"### Intake Assessment Raw Logs for {selected_intake_athlete} ({season_label})")

            with st.expander("NordBord Test Log", expanded=False):
                if not nord_ath.empty:
                    disp_nord = [c for c in nord_ath.columns if c not in ["Name", "Date_Str"]]
                    st.markdown(render_vball_table(nord_ath[disp_nord]), unsafe_allow_html=True)
                else:
                    st.info(f"No NordBord records for {selected_intake_athlete} in {season_label}.")

            with st.expander("Harness Belt Squat Log", expanded=False):
                if not bs_ath.empty:
                    disp_bs = [c for c in bs_ath.columns if c not in ["Name", "Date_Str", "PVF_Calc"]]
                    st.markdown(render_vball_table(bs_ath[disp_bs]), unsafe_allow_html=True)
                else:
                    st.info(f"No Harness Belt Squat records for {selected_intake_athlete} in {season_label}.")

            with st.expander("Knee Extension / Flexion Log", expanded=False):
                if not sh_ath.empty:
                    disp_knee = [c for c in sh_ath.columns if c not in ["Name", "Date_Str"]]
                    st.markdown(render_vball_table(sh_ath[disp_knee]), unsafe_allow_html=True)
                else:
                    st.info(f"No Knee Assessment records for {selected_intake_athlete} in {season_label}.")

            with st.expander("Hip Adduction / Abduction Log", expanded=False):
                if not hip_ath.empty:
                    hip_display_df = hip_ath.copy()
                    dir_col = next((c for c in hip_display_df.columns if "direction" in c.lower() or "test" in c.lower()), None)
                    test_col = next((c for c in hip_display_df.columns if c.lower() == "test"), None)

                    if dir_col:
                        hip_display_df["Test"] = hip_display_df[dir_col].apply(
                            lambda x: "Hip Adduction" if "AD" in str(x) or "Adduction" in str(x) else ("Hip Abduction" if "AB" in str(x) or "Abduction" in str(x) else str(x))
                        )
                    
                    omit_cols = ["Name", "Date_Str"]
                    if dir_col and dir_col != "Test":
                        omit_cols.append(dir_col)
                    if test_col and test_col != "Test":
                        omit_cols.append(test_col)

                    all_cols = [c for c in hip_display_df.columns if c not in omit_cols]
                    final_cols = []
                    if "Date" in all_cols:
                        final_cols.append("Date")
                        all_cols.remove("Date")
                    if "Test" in all_cols:
                        final_cols.append("Test")
                        all_cols.remove("Test")
                    final_cols.extend(all_cols)

                    st.markdown(render_vball_table(hip_display_df[final_cols]), unsafe_allow_html=True)
                else:
                    st.info(f"No Hip Assessment records for {selected_intake_athlete} in {season_label}.")

            with st.expander("Ankle Plantar Flexion Log", expanded=False):
                if not calf_ath.empty:
                    disp_ankle = [c for c in calf_ath.columns if c not in ["Name", "Date_Str"]]
                    st.markdown(render_vball_table(calf_ath[disp_ankle]), unsafe_allow_html=True)
                else:
                    st.info(f"No Ankle Assessment records for {selected_intake_athlete} in {season_label}.")

        # SECTION 5B: CMJ TAB
        with testing_tab_cmj:
            st.markdown(
                f'<div class="vball-section-title">CMJ History — {season_label}</div>',
                unsafe_allow_html=True,
            )

            c_filter, _ = st.columns([1, 2])
            with c_filter:
                selected_player_t = st.selectbox(
                    "Select Athlete:", roster_players, key=f"cmj_player_select_{season_key}"
                )

            p_cmj = (
                cmj_data[cmj_data["Name"] == selected_player_t]
                .sort_values("Date")
                .copy()
                if not cmj_data.empty
                else pd.DataFrame()
            )

            jump_cols = [c for c in p_cmj.columns if "jump" in c.lower() or "height" in c.lower()]
            j_col = jump_cols[0] if jump_cols else None
            rsi_cols = [c for c in p_cmj.columns if "rsi" in c.lower()]
            rsi_col = rsi_cols[0] if rsi_cols else None

            if not p_cmj.empty and j_col:
                p_cmj["Jump_Height_Clean"] = pd.to_numeric(
                    p_cmj[j_col].astype(str).str.replace(r"[^0-9.]", "", regex=True),
                    errors="coerce",
                )

                fig_jump_trend = go.Figure()
                fig_jump_trend.add_trace(
                    go.Scatter(
                        x=p_cmj["Date"],
                        y=p_cmj["Jump_Height_Clean"],
                        name="Jump Height",
                        mode="lines+markers",
                        connectgaps=True,
                        yaxis="y",
                        line=dict(color="#FF8200", width=4),
                        marker=dict(size=8, color="#FF8200"),
                    )
                )

                if rsi_col:
                    p_cmj["RSI_Clean"] = pd.to_numeric(
                        p_cmj[rsi_col].astype(str).str.replace(r"[^0-9.]", "", regex=True),
                        errors="coerce",
                    )
                    fig_jump_trend.add_trace(
                        go.Scatter(
                            x=p_cmj["Date"],
                            y=p_cmj["RSI_Clean"],
                            name="RSI Modified",
                            mode="lines+markers",
                            connectgaps=True,
                            yaxis="y2",
                            line=dict(color="#38BDF8", width=3, dash="dot"),
                            marker=dict(size=8, color="#38BDF8"),
                        )
                    )

                fig_jump_trend.update_layout(
                    height=320,
                    margin=dict(l=40, r=40, t=50, b=40),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.08,
                        xanchor="left",
                        x=0.01,
                        font=dict(size=13, color="#0F172A"),
                    ),
                    xaxis=dict(
                        title=None,
                        type="date",
                        tickformat="%b %d\n%Y",
                        showgrid=False,
                        showline=True,
                        linewidth=1.5,
                        linecolor="#0F172A",
                        tickfont=dict(color="#64748B", size=12),
                    ),
                    yaxis=dict(
                        showgrid=False,
                        showline=True,
                        linewidth=1.5,
                        linecolor="#0F172A",
                        tickfont=dict(color="#64748B", size=12),
                        side="left",
                    ),
                    yaxis2=dict(
                        showgrid=False,
                        showline=True,
                        linewidth=1.5,
                        linecolor="#0F172A",
                        tickfont=dict(color="#64748B", size=12),
                        overlaying="y",
                        side="right",
                        anchor="x",
                    ),
                )
                st.plotly_chart(fig_jump_trend, use_container_width=True, key=f"cmj_trend_{season_key}")

                st.divider()

                display_cols = [
                    c for c in p_cmj.columns if c not in ["Name", "Date_Str", "Jump_Height_Clean", "RSI_Clean"]
                ]
                st.markdown(f"### Jump History Logs for {selected_player_t} ({season_label})")
                st.markdown(render_vball_table(p_cmj[display_cols]), unsafe_allow_html=True)
            else:
                st.info(f"No Countermovement Jump (CMJ) logs found for {selected_player_t} in {season_label}.")

        # SECTION 5C: OVERALL PROFILE
        with testing_tab_overall:
            st.markdown(
                f'<div class="vball-section-title">Master Athletic Performance Summary ({season_label})</div>',
                unsafe_allow_html=True,
            )
            c_ov_ath, _ = st.columns([1, 2])
            with c_ov_ath:
                selected_ov_athlete = st.selectbox(
                    "Select Athlete for Master Profile:",
                    roster_players,
                    key=f"overall_ath_select_{season_key}",
                )

            records = []

            def get_formatted_peak_overall(df_sub):
                if df_sub.empty:
                    return None, None
                
                l_col = next((c for c in df_sub.columns if "l max force" in c.lower() or "left max" in c.lower()), None)
                r_col = next((c for c in df_sub.columns if "r max force" in c.lower() or "right max" in c.lower()), None)
                
                if l_col and r_col:
                    df_sub["Peak_Val"] = df_sub[[l_col, r_col]].apply(pd.to_numeric, errors="coerce").max(axis=1)
                    valid_rows = df_sub.dropna(subset=["Peak_Val"])
                    if valid_rows.empty:
                        return None, None
                    
                    best_row = valid_rows.sort_values("Peak_Val", ascending=False).iloc[0]
                    l_val = pd.to_numeric(best_row[l_col], errors="coerce")
                    r_val = pd.to_numeric(best_row[r_col], errors="coerce")
                    
                    l_str = f"{l_val:.1f} N" if pd.notna(l_val) else "N/A"
                    r_str = f"{r_val:.1f} N" if pd.notna(r_val) else "N/A"
                    
                    return f"{l_str} / {r_str}", format_date_clean(best_row.get("Date"))
                else:
                    return None, None

            p_cmj_ov = cmj_data[cmj_data["Name"] == selected_ov_athlete] if not cmj_data.empty and "Name" in cmj_data.columns else pd.DataFrame()
            if not p_cmj_ov.empty:
                jh_c = next((c for c in p_cmj_ov.columns if "jump" in c.lower() or "height" in c.lower()), None)
                if jh_c:
                    p_cmj_ov["JH_Val"] = pd.to_numeric(p_cmj_ov[jh_c].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
                    valid_cmj = p_cmj_ov.dropna(subset=["JH_Val"])
                    if not valid_cmj.empty:
                        best_cmj = valid_cmj.sort_values("JH_Val", ascending=False).iloc[0]
                        records.append({
                            "Category": "Countermovement Jump",
                            "Best Test Value": f"{best_cmj['JH_Val']:.2f} cm",
                            "Date Achieved": format_date_clean(best_cmj.get("Date"))
                        })

            p_nord_ov = nordic_data[nordic_data["Name"] == selected_ov_athlete].copy() if not nordic_data.empty and "Name" in nordic_data.columns else pd.DataFrame()
            if not p_nord_ov.empty:
                t_c = next((c for c in p_nord_ov.columns if "test" in c.lower()), None)
                if t_c:
                    for test_type_val in p_nord_ov[t_c].dropna().unique():
                        sub_df = p_nord_ov[p_nord_ov[t_c] == test_type_val]
                        val, dt = get_formatted_peak_overall(sub_df)
                        if val:
                            records.append({
                                "Category": f"NordBord - {test_type_val} (L/R)",
                                "Best Test Value": val,
                                "Date Achieved": dt
                            })
                else:
                    val, dt = get_formatted_peak_overall(p_nord_ov)
                    if val:
                        records.append({
                            "Category": "NordBord Hamstring (L/R)",
                            "Best Test Value": val,
                            "Date Achieved": dt
                        })

            p_bs_ov = belt_squat_data[belt_squat_data["Name"] == selected_ov_athlete] if not belt_squat_data.empty and "Name" in belt_squat_data.columns else pd.DataFrame()
            if not p_bs_ov.empty:
                f_c = next((c for c in p_bs_ov.columns if "peak vertical force" in c.lower() or "force" in c.lower()), None)
                if f_c:
                    p_bs_ov["PVF"] = pd.to_numeric(p_bs_ov[f_c].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
                    valid_bs = p_bs_ov.dropna(subset=["PVF"])
                    if not valid_bs.empty:
                        best_bs = valid_bs.sort_values("PVF", ascending=False).iloc[0]
                        records.append({
                            "Category": "Harness Belt Squat",
                            "Best Test Value": f"{best_bs['PVF']:.1f} N",
                            "Date Achieved": format_date_clean(best_bs.get("Date"))
                        })

            p_knee_ov = knee_data[knee_data["Name"] == selected_ov_athlete].copy() if not knee_data.empty and "Name" in knee_data.columns else pd.DataFrame()
            if not p_knee_ov.empty:
                dir_col = next((c for c in p_knee_ov.columns if "direction" in c.lower() or "test" in c.lower()), None)
                ke_df = p_knee_ov[p_knee_ov[dir_col].astype(str).str.contains("Extension", case=False, na=False)] if dir_col else p_knee_ov
                kf_df = p_knee_ov[p_knee_ov[dir_col].astype(str).str.contains("Flexion", case=False, na=False)] if dir_col else pd.DataFrame()

                val, dt = get_formatted_peak_overall(ke_df)
                if val:
                    records.append({"Category": "Knee Extension (L/R)", "Best Test Value": val, "Date Achieved": dt})

                val, dt = get_formatted_peak_overall(kf_df)
                if val:
                    records.append({"Category": "Knee Flexion (L/R)", "Best Test Value": val, "Date Achieved": dt})

            p_hip_ov = hip_data[hip_data["Name"] == selected_ov_athlete].copy() if not hip_data.empty and "Name" in hip_data.columns else pd.DataFrame()
            if not p_hip_ov.empty:
                dir_col = next((c for c in p_hip_ov.columns if "direction" in c.lower() or "test" in c.lower()), None)
                ad_df = p_hip_ov[p_hip_ov[dir_col].astype(str).str.contains("AD|Adduction", case=False, na=False)] if dir_col else p_hip_ov
                ab_df = p_hip_ov[p_hip_ov[dir_col].astype(str).str.contains("AB|Abduction", case=False, na=False)] if dir_col else pd.DataFrame()

                val, dt = get_formatted_peak_overall(ad_df)
                if val:
                    records.append({"Category": "Hip Adduction (L/R)", "Best Test Value": val, "Date Achieved": dt})

                val, dt = get_formatted_peak_overall(ab_df)
                if val:
                    records.append({"Category": "Hip Abduction (L/R)", "Best Test Value": val, "Date Achieved": dt})

            p_ank_ov = ankle_data[ankle_data["Name"] == selected_ov_athlete].copy() if not ankle_data.empty and "Name" in ankle_data.columns else pd.DataFrame()
            if not p_ank_ov.empty:
                val, dt = get_formatted_peak_overall(p_ank_ov)
                if val:
                    records.append({"Category": "Ankle Plantar Flexion (L/R)", "Best Test Value": val, "Date Achieved": dt})

            if records:
                ov_df = pd.DataFrame(records)
                st.markdown(f"### Peak Performance Snapshot for {selected_ov_athlete} ({season_label})")
                st.markdown(render_vball_table(ov_df), unsafe_allow_html=True)
            else:
                st.info(f"No testing records found across modules for {selected_ov_athlete} in {season_label}.")

    # TAB 6: RECOVERY
    elif main_tab == "Recovery":
        rec_tab_tracker, rec_tab_summary = st.tabs(
            ["Live Recovery Tracker", "Team Recovery Summary"]
        )

        local_now = get_eastern_now()
        today = local_now.date()
        current_monday = today - datetime.timedelta(days=today.weekday())

        live_rec_df = fetch_live_recovery_sheet()

        if "recovery_local_state" not in st.session_state:
            st.session_state.recovery_local_state = {}

        if not live_rec_df.empty:
            for _, row in live_rec_df.iterrows():
                wk_val = str(row.get("Week_Starting", "")).strip()
                ath_val = str(row.get("Athlete", "")).strip()
                stn_val = str(row.get("Station", "")).strip()
                dy_val = str(row.get("Day", "")).strip()
                dur_val = str(row.get("Duration_Minutes", "")).strip()
                if wk_val and ath_val and stn_val and dy_val:
                    key = f"{wk_val}|{ath_val}|{stn_val}|{dy_val}"
                    if key not in st.session_state.recovery_local_state:
                        st.session_state.recovery_local_state[key] = dur_val

        def send_recovery_update(ath_name, stn_label, wk_s, dy_s, action_val, duration=None):
            time_val = get_eastern_time_str() if action_val == "add" else ""
            payload = {
                "Week_Starting": str(wk_s).strip(),
                "Athlete": str(ath_name).strip(),
                "Station": str(stn_label).strip(),
                "Day": str(dy_s).strip(),
                "Timestamp": time_val,
                "Action": action_val,
            }
            if duration is not None:
                payload["Duration_Minutes"] = duration

            try:
                macro_url = (
                    st.secrets.get("MACRO_URL")
                    or st.secrets.get("Live Track")
                    or st.secrets.get("sheets", {}).get("live_track_url")
                )
                if macro_url:
                    requests.post(
                        macro_url,
                        data=json.dumps(payload),
                        headers={"Content-Type": "text/plain;charset=utf-8"},
                        allow_redirects=True,
                        timeout=8,
                    )
            except Exception as ex:
                print(f"Recovery webhook POST failed: {ex}")

        @st.dialog("Log Recovery Duration")
        def log_duration_modal(ath_name, stn_label, state_key, wk_s, dy_s):
            st.markdown(f"Logging **{stn_label}** for **{ath_name}**")
            duration_val = st.number_input(
                "Duration (Minutes):",
                min_value=1,
                max_value=180,
                value=15,
                step=1,
                key=f"input_dur_{state_key}",
            )
            col_save, col_skip = st.columns(2)
            with col_save:
                if st.button("Save & Log", use_container_width=True, type="primary"):
                    st.session_state.recovery_local_state[state_key] = str(duration_val)
                    send_recovery_update(ath_name, stn_label, wk_s, dy_s, "add", duration=duration_val)
                    st.rerun()
            with col_skip:
                if st.button("Skip Duration", use_container_width=True):
                    st.session_state.recovery_local_state[state_key] = ""
                    send_recovery_update(ath_name, stn_label, wk_s, dy_s, "add", duration="")
                    st.rerun()

        def handle_recovery_check_change(ath_name, stn_label, key_name, wk_s, dy_s):
            is_checked = st.session_state[key_name]
            state_key = f"{str(wk_s).strip()}|{str(ath_name).strip()}|{str(stn_label).strip()}|{str(dy_s).strip()}"

            if is_checked:
                log_duration_modal(ath_name, stn_label, state_key, wk_s, dy_s)
            else:
                if state_key in st.session_state.recovery_local_state:
                    del st.session_state.recovery_local_state[state_key]
                send_recovery_update(ath_name, stn_label, wk_s, dy_s, "remove")

        with rec_tab_tracker:
            st.markdown(
                '<div class="vball-section-title">Athlete Recovery Checkbox Grid</div>',
                unsafe_allow_html=True,
            )

            c_rec1, c_rec2 = st.columns(2)
            with c_rec1:
                selected_rec_monday = st.date_input(
                    "Select Week Starting (Monday):",
                    value=current_monday,
                    key=f"rec_week_picker_{season_key}",
                )
                if selected_rec_monday.weekday() != 0:
                    selected_rec_monday = (
                        selected_rec_monday
                        - datetime.timedelta(days=selected_rec_monday.weekday())
                    )
                week_str = selected_rec_monday.strftime("%Y-%m-%d")

            with c_rec2:
                days_options = [
                    (selected_rec_monday + datetime.timedelta(days=i)).strftime("%A (%m/%d)")
                    for i in range(7)
                ]
                current_day_str = local_now.strftime("%A (%m/%d)")
                default_idx = (
                    days_options.index(current_day_str)
                    if current_day_str in days_options
                    else 0
                )
                selected_rec_day = st.selectbox(
                    "Select Day:",
                    days_options,
                    index=default_idx,
                    key=f"rec_day_picker_{season_key}",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            stations = [
                "Normatec",
                "Tubs",
                "Firefly",
                "BFR",
                "Mobility",
                "Marc Pro",
                "Tempering",
            ]

            for i in range(0, len(roster_players), 2):
                grid_cols = st.columns(2)
                for j in range(2):
                    if i + j < len(roster_players):
                        player = roster_players[i + j]
                        p_row = (
                            roster_raw[roster_raw["Name"] == player]
                            if not roster_raw.empty
                            else pd.DataFrame()
                        )
                        p_pos = (
                            p_row["Position"].values[0]
                            if not p_row.empty
                            else "Athlete"
                        )
                        p_img = (
                            p_row["Picture"].values[0]
                            if not p_row.empty
                            else "https://via.placeholder.com/70"
                        )

                        with grid_cols[j]:
                            st.markdown(
                                f"""
                                <div class="rec-grid-card">
                                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 8px;">
                                        <img src="{p_img}" class="athlete-avatar" style="width: 55px; height: 55px;">
                                        <div>
                                            <h4 style="margin: 0; color: #0F172A; font-weight: 700;">{player}</h4>
                                            <span style="color: #64748B; font-size: 0.85rem;">{p_pos}</span>
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            chk_cols = st.columns(3)
                            for s_idx, station_label in enumerate(stations):
                                state_key = f"{str(week_str).strip()}|{str(player).strip()}|{str(station_label).strip()}|{str(selected_rec_day).strip()}"
                                is_checked = state_key in st.session_state.recovery_local_state

                                cb_key = f"rec_cb_{season_key}_{player.replace(' ', '_').replace(',', '')}_{station_label.replace(' ', '_').replace('(', '').replace(')', '')}_{week_str}_{selected_rec_day.replace(' ', '_')}"

                                with chk_cols[s_idx % 3]:
                                    st.checkbox(
                                        f"{station_label}",
                                        value=is_checked,
                                        key=cb_key,
                                        on_change=handle_recovery_check_change,
                                        args=(
                                            player,
                                            station_label,
                                            cb_key,
                                            week_str,
                                            selected_rec_day,
                                        ),
                                    )
                            st.markdown("<br>", unsafe_allow_html=True)

        with rec_tab_summary:
            st.markdown(
                '<div class="vball-section-title">Team Recovery Master Summary</div>',
                unsafe_allow_html=True,
            )

            c_sum_wk, _ = st.columns([1, 2])
            with c_sum_wk:
                summary_selected_monday = st.date_input(
                    "Filter Summary by Week Starting (Monday):",
                    value=current_monday,
                    key=f"rec_summary_week_picker_{season_key}",
                )
                if summary_selected_monday.weekday() != 0:
                    summary_selected_monday = (
                        summary_selected_monday
                        - datetime.timedelta(days=summary_selected_monday.weekday())
                    )
                summary_week_str = summary_selected_monday.strftime("%Y-%m-%d")

            st.markdown("<br>", unsafe_allow_html=True)

            summary_rows = []
            for item, dur in st.session_state.recovery_local_state.items():
                parts = item.split("|")
                if len(parts) == 4:
                    dur_clean = pd.to_numeric(dur, errors="coerce")
                    dur_val = int(dur_clean) if pd.notna(dur_clean) else 0
                    summary_rows.append({
                        "Week_Starting": parts[0],
                        "Athlete": parts[1],
                        "Station": parts[2],
                        "Day": parts[3],
                        "Duration_Minutes": dur_val,
                    })

            all_summary_df = (
                pd.DataFrame(summary_rows)
                if summary_rows
                else pd.DataFrame(
                    columns=["Week_Starting", "Athlete", "Station", "Day", "Duration_Minutes"]
                )
            )

            summary_df = (
                all_summary_df[all_summary_df["Week_Starting"] == summary_week_str]
                if not all_summary_df.empty and "Week_Starting" in all_summary_df.columns
                else pd.DataFrame(columns=["Week_Starting", "Athlete", "Station", "Day", "Duration_Minutes"])
            )

            if not summary_df.empty and "Station" in summary_df.columns:
                total_completions = len(summary_df)
                total_duration_all = summary_df["Duration_Minutes"].sum()
                active_athletes = (
                    summary_df["Athlete"].nunique()
                    if "Athlete" in summary_df.columns
                    else 0
                )
                
                hrs = total_duration_all // 60
                mins = total_duration_all % 60
                total_time_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"

                kpi_html = (
                    '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">'
                    '<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #FF8200; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">'
                    '<div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">Total Recovery Duration</div>'
                    f'<div style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin-top: 4px;">{total_time_str}</div>'
                    f'<div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">{total_duration_all} Total Minutes Logged</div>'
                    "</div>"
                    '<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #38BDF8; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">'
                    '<div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">Active Athletes Logged</div>'
                    f'<div style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin-top: 4px;">{active_athletes}</div>'
                    f'<div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">Logged Recovery This Week</div>'
                    "</div>"
                    '<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #58595B; border-radius: 10px; padding: 16px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">'
                    '<div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">Total Check-ins</div>'
                    f'<div style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin-top: 4px;">{total_completions}</div>'
                    f'<div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">Across All Stations</div>'
                    "</div>"
                    "</div>"
                )
                st.markdown(kpi_html, unsafe_allow_html=True)

                st.markdown(
                    f"<h4 style='color:#0F172A; font-size:1.05rem; font-weight:700; margin-bottom:12px;'>Station Usage & Duration Breakdown (Week of {summary_week_str})</h4>",
                    unsafe_allow_html=True,
                )

                stn_agg = (
                    summary_df.groupby("Station")
                    .agg(
                        Usages=("Station", "count"),
                        Total_Minutes=("Duration_Minutes", "sum")
                    )
                    .reset_index()
                    .sort_values(by="Total_Minutes", ascending=False)
                )

                def format_mins_str(m):
                    if m <= 0:
                        return "--"
                    h = m // 60
                    rem = m % 60
                    return f"{h}h {rem}m" if h > 0 else f"{rem}m"

                stn_agg["Formatted_Duration"] = stn_agg["Total_Minutes"].apply(format_mins_str)

                col_stn_chart, col_stn_tbl = st.columns([1.6, 1.2])

                with col_stn_chart:
                    fig_dur_bar = px.bar(
                        stn_agg,
                        x="Station",
                        y="Total_Minutes",
                        text="Formatted_Duration",
                        title="Total Duration (Minutes) by Station",
                    )
                    fig_dur_bar.update_traces(
                        marker_color="#FF8200",
                        marker_line_color="#D96B00",
                        marker_line_width=1.5,
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>Total Time: %{text}<br>Minutes: %{y}m<extra></extra>",
                    )
                    fig_dur_bar.update_layout(
                        showlegend=False,
                        height=290,
                        margin=dict(l=10, r=10, t=35, b=10),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        title_font=dict(size=13, color="#0F172A"),
                        xaxis=dict(
                            title=None,
                            showgrid=False,
                            tickfont=dict(color="#475569", size=11, weight="bold"),
                        ),
                        yaxis=dict(
                            title="Minutes",
                            showgrid=True,
                            gridcolor="#F1F5F9",
                            zeroline=False,
                        ),
                    )
                    st.plotly_chart(fig_dur_bar, use_container_width=True, key=f"dur_bar_{season_key}")

                with col_stn_tbl:
                    display_stn_df = stn_agg.rename(
                        columns={
                            "Station": "Station",
                            "Usages": "Total Logs",
                            "Formatted_Duration": "Total Time",
                            "Total_Minutes": "Minutes",
                        }
                    )[["Station", "Total Logs", "Total Time"]]

                    st.markdown(
                        f"""
                        <div style="font-weight:700; font-size:0.9rem; margin-bottom: 8px; color:#0F172A;">
                            Station Summary Table
                        </div>
                        {render_vball_table(display_stn_df)}
                        """,
                        unsafe_allow_html=True,
                    )

                st.divider()

                st.markdown(
                    f"<h4 style='color:#0F172A; font-size:1.05rem; font-weight:700; margin-bottom:12px;'>Weekly Athlete Recovery Timeline (Week of {summary_week_str})</h4>",
                    unsafe_allow_html=True,
                )
                if "Athlete" in summary_df.columns:
                    ath_grouped = summary_df.groupby("Athlete")
                    days_order = [
                        ("Monday", "Mon"),
                        ("Tuesday", "Tue"),
                        ("Wednesday", "Wed"),
                        ("Thursday", "Thu"),
                        ("Friday", "Fri"),
                        ("Saturday", "Sat"),
                        ("Sunday", "Sun"),
                    ]

                    for ath_name, group in ath_grouped:
                        day_stations_map = {}
                        for _, row in group.iterrows():
                            raw_day = str(row.get("Day", ""))
                            stn = str(row.get("Station", ""))
                            dur = row.get("Duration_Minutes", 0)
                            stn_display = f"{stn} ({dur}m)" if dur > 0 else stn
                            day_key = next(
                                (
                                    full
                                    for full, _ in days_order
                                    if full in raw_day
                                ),
                                raw_day,
                            )
                            if day_key not in day_stations_map:
                                day_stations_map[day_key] = []
                            day_stations_map[day_key].append(stn_display)

                        days_grid_html = ""
                        for full_day, short_day in days_order:
                            stations_list = day_stations_map.get(full_day, [])

                            if stations_list:
                                stations_html = "".join([
                                    f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:3px solid #FF8200; border-radius:4px; padding:4px 8px; margin-top:4px; font-weight:700; color:#0F172A; font-size:0.78rem; text-align:center;">{stn}</div>'
                                    for stn in stations_list
                                ])
                                card_style = "background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:10px; flex:1; min-width:0;"
                                header_color = "#FF8200"
                            else:
                                stations_html = '<div style="color:#94A3B8; font-size:0.75rem; text-align:center; margin-top:8px; font-style:italic;">—</div>'
                                card_style = "background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px; flex:1; min-width:0;"
                                header_color = "#64748B"

                            days_grid_html += (
                                f'<div style="{card_style}">'
                                f'<div style="font-weight:700; color:{header_color}; font-size:0.8rem; text-align:center; border-bottom:1px solid #E2E8F0; padding-bottom:4px; text-transform:uppercase;">{short_day}</div>'
                                f"{stations_html}"
                                "</div>"
                            )

                        card_html = (
                            '<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">'
                            f'<div style="font-weight:800; color:#0F172A; font-size:1rem; margin-bottom:12px;">{ath_name}</div>'
                            f'<div style="display:flex; gap:10px; width:100%;">{days_grid_html}</div>'
                            "</div>"
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info(f"No recovery data recorded for the week of {summary_week_str}.")

    # TAB 7: TRACKING (Updated 4 metrics: Turnover, Not Crashing, No Box Out, Not Calling Back)
    elif main_tab == "Tracking":
        track_tab_live, track_tab_summary = st.tabs(
            ["Practice Live Tracker", "Weekly & Daily Summary"]
        )

        local_now = get_eastern_now()
        today = local_now.date()
        current_monday = today - datetime.timedelta(days=today.weekday())

        with track_tab_live:
            st.markdown(
                '<div class="vball-section-title">In-Practice Performance Stat Tracker</div>',
                unsafe_allow_html=True,
            )

            col_tr1, col_tr2 = st.columns(2)
            with col_tr1:
                selected_track_monday = st.date_input(
                    "Select Week Starting (Monday):",
                    value=current_monday,
                    key=f"track_week_picker_{season_key}",
                )
                if selected_track_monday.weekday() != 0:
                    selected_track_monday = (
                        selected_track_monday
                        - datetime.timedelta(days=selected_track_monday.weekday())
                    )
                track_week_str = selected_track_monday.strftime("%Y-%m-%d")

            with col_tr2:
                track_days_options = [
                    (selected_track_monday + datetime.timedelta(days=i)).strftime("%Y-%m-%d (%A)")
                    for i in range(7)
                ]
                current_day_str = local_now.strftime("%Y-%m-%d (%A)")
                default_idx = (
                    track_days_options.index(current_day_str)
                    if current_day_str in track_days_options
                    else 0
                )
                selected_track_day = st.selectbox(
                    "Select Practice Date:",
                    track_days_options,
                    index=default_idx,
                    key=f"track_day_picker_{season_key}",
                )

            session_date_val = selected_track_day.split(" ")[0]

            st.markdown("<br>", unsafe_allow_html=True)

            def modify_counter(p_name, metric, delta, wk_s, date_s):
                wk_clean = format_date_clean(wk_s)
                dt_clean = format_date_clean(date_s)
                key = f"{wk_clean}|{dt_clean}|{p_name}|{metric}"
                
                curr = st.session_state.tracking_data.get(key, 0)
                new_val = max(0, curr + delta)
                st.session_state.tracking_data[key] = new_val

                macro_url = (
                    st.secrets.get("MACRO_URL")
                    or st.secrets.get("Live Track")
                    or st.secrets.get("sheets", {}).get("live_track_url")
                )

                if macro_url:
                    payload = {
                        "tracking_logs": [
                            {
                                "Week_Starting": wk_clean,
                                "Date": dt_clean,
                                "Athlete": str(p_name).strip(),
                                "Metric": str(metric).strip(),
                                "Count": new_val,
                                "Timestamp": get_eastern_time_str(),
                            }
                        ]
                    }
                    try:
                        requests.post(
                            macro_url,
                            data=json.dumps(payload),
                            headers={"Content-Type": "text/plain;charset=utf-8"},
                            allow_redirects=True,
                            timeout=8
                        )
                    except Exception as ex:
                        print(f"Tracking auto-sync POST failed: {ex}")

            for i in range(0, len(roster_players), 2):
                grid_cols = st.columns(2)
                for j in range(2):
                    if i + j < len(roster_players):
                        player = roster_players[i + j]
                        p_row = (
                            roster_raw[roster_raw["Name"] == player]
                            if not roster_raw.empty
                            else pd.DataFrame()
                        )
                        p_pos = (
                            p_row["Position"].values[0]
                            if not p_row.empty
                            else "Athlete"
                        )
                        p_img = (
                            p_row["Picture"].values[0]
                            if not p_row.empty
                            else "https://via.placeholder.com/70"
                        )

                        with grid_cols[j]:
                            st.markdown(
                                f"""
                                <div class="rec-grid-card">
                                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 8px;">
                                        <img src="{p_img}" class="athlete-avatar" style="width: 55px; height: 55px;">
                                        <div>
                                            <h4 style="margin: 0; color: #0F172A; font-weight: 700;">{player}</h4>
                                            <span style="color: #64748B; font-size: 0.85rem;">{p_pos}</span>
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            m_cols = st.columns(4)
                            metrics = ["Turnover", "Not Crashing", "No Box Out", "Not Calling Back"]
                            for m_idx, metric_name in enumerate(metrics):
                                key = f"{track_week_str}|{session_date_val}|{player}|{metric_name}"
                                val = st.session_state.tracking_data.get(key, 0)
                                with m_cols[m_idx]:
                                    st.markdown(
                                        f"<div style='text-align:center; font-weight:700; font-size:0.75rem; color:#475569; min-height:34px; line-height:1.2;'>{metric_name}</div>",
                                        unsafe_allow_html=True,
                                    )
                                    b_col1, b_col2, b_col3 = st.columns([1, 1.2, 1])
                                    with b_col1:
                                        st.button(
                                            "−",
                                            key=f"dec_{season_key}_{player}_{metric_name}_{session_date_val}",
                                            on_click=modify_counter,
                                            args=(player, metric_name, -1, track_week_str, session_date_val),
                                        )
                                    with b_col2:
                                        st.markdown(
                                            f"<div style='text-align:center; font-size:1.1rem; font-weight:800; padding-top:2px;'>{val}</div>",
                                            unsafe_allow_html=True,
                                        )
                                    with b_col3:
                                        st.button(
                                            "+",
                                            key=f"inc_{season_key}_{player}_{metric_name}_{session_date_val}",
                                            on_click=modify_counter,
                                            args=(player, metric_name, 1, track_week_str, session_date_val),
                                        )

                            st.markdown("<br>", unsafe_allow_html=True)

        with track_tab_summary:
            st.markdown(
                '<div class="vball-section-title">Tracking Summary Dashboard</div>',
                unsafe_allow_html=True,
            )

            t_rows = []
            for k, v in st.session_state.tracking_data.items():
                parts = k.split("|")
                if len(parts) == 4 and v > 0:
                    t_rows.append({
                        "Week_Starting": parts[0],
                        "Date": parts[1],
                        "Athlete": parts[2],
                        "Metric": parts[3],
                        "Count": v
                    })

            track_df = pd.DataFrame(t_rows) if t_rows else pd.DataFrame(columns=["Week_Starting", "Date", "Athlete", "Metric", "Count"])

            if not track_df.empty:
                filtered_wk_df = track_df[track_df["Week_Starting"] == track_week_str]

                total_tracking = int(filtered_wk_df["Count"].sum())
                active_athletes = filtered_wk_df["Athlete"].nunique()
                metric_counts = (
                    filtered_wk_df.groupby("Metric")["Count"]
                    .sum()
                    .sort_values(ascending=False)
                )
                top_metric = metric_counts.index[0] if not metric_counts.empty else "N/A"

                kpi_html = (
                    '<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:24px;">'
                    '<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:5px solid #FF8200; border-radius:10px; padding:16px; text-align:center; box-shadow:0 2px 4px rgba(0,0,0,0.02);">'
                    '<div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">Total Tracking Events</div>'
                    f'<div style="font-size:1.8rem; font-weight:800; color:#0F172A; margin-top:4px;">{total_tracking}</div>'
                    '</div>'
                    '<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:5px solid #38BDF8; border-radius:10px; padding:16px; text-align:center; box-shadow:0 2px 4px rgba(0,0,0,0.02);">'
                    '<div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">Active Athletes Logged</div>'
                    f'<div style="font-size:1.8rem; font-weight:800; color:#0F172A; margin-top:4px;">{active_athletes}</div>'
                    '</div>'
                    '<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:5px solid #58595B; border-radius:10px; padding:16px; text-align:center; box-shadow:0 2px 4px rgba(0,0,0,0.02);">'
                    '<div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">Most Recorded Action</div>'
                    f'<div style="font-size:1.8rem; font-weight:800; color:#0F172A; margin-top:4px;">{top_metric}</div>'
                    '</div>'
                    '</div>'
                )

                st.markdown(kpi_html, unsafe_allow_html=True)

                st.markdown(
                    f"<h4 style='color:#0F172A; font-size:1.05rem; font-weight:700; margin-bottom:12px;'>Daily Tracking Breakdown ({session_date_val})</h4>",
                    unsafe_allow_html=True,
                )

                daily_df = filtered_wk_df[filtered_wk_df["Date"] == session_date_val]

                if not daily_df.empty:
                    pivot_daily = daily_df.pivot_table(
                        index="Athlete",
                        columns="Metric",
                        values="Count",
                        aggfunc="sum",
                        fill_value=0
                    ).reset_index()

                    daily_config = {
                        col: st.column_config.Column(alignment="center")
                        for col in pivot_daily.columns
                    }

                    st.dataframe(
                        pivot_daily,
                        column_config=daily_config,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No stats recorded for the selected date.")

                st.divider()

                st.markdown(
                    "<h4 style='color:#0F172A; font-size:1.05rem; font-weight:700; margin-bottom:12px;'>Weekly Athlete Tracking Timeline</h4>",
                    unsafe_allow_html=True,
                )

                if "Athlete" in filtered_wk_df.columns:
                    ath_grouped = filtered_wk_df.groupby("Athlete")
                    days_order = [
                        ("Monday", "Mon"),
                        ("Tuesday", "Tue"),
                        ("Wednesday", "Wed"),
                        ("Thursday", "Thu"),
                        ("Friday", "Fri"),
                        ("Saturday", "Sat"),
                        ("Sunday", "Sun"),
                    ]

                    for ath_name, group in ath_grouped:
                        day_metrics_map = {}
                        for _, row in group.iterrows():
                            raw_date = str(row.get("Date", ""))
                            metric = str(row.get("Metric", ""))
                            count = int(row.get("Count", 0))

                            try:
                                parsed_date = pd.to_datetime(raw_date)
                                day_name = parsed_date.day_name()
                            except:
                                day_name = next(
                                    (full for full, _ in days_order if full.lower() in raw_date.lower()),
                                    raw_date,
                                )

                            if day_name not in day_metrics_map:
                                day_metrics_map[day_name] = []

                            day_metrics_map[day_name].append((metric, count))

                        days_grid_html = ""
                        for full_day, short_day in days_order:
                            metrics_list = day_metrics_map.get(full_day, [])

                            if metrics_list:
                                metrics_html = ""
                                for metric, count in metrics_list:
                                    metrics_html += (
                                        f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:3px solid #FF8200; border-radius:4px; padding:4px 8px; margin-top:4px; font-weight:700; color:#0F172A; font-size:0.78rem; text-align:center;">{metric}: {count}</div>'
                                    )
                                card_style = 'background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:10px; flex:1; min-width:0;'
                                header_color = "#FF8200"
                            else:
                                metrics_html = '<div style="color:#94A3B8; font-size:0.75rem; text-align:center; margin-top:8px; font-style:italic;">—</div>'
                                card_style = 'background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px; flex:1; min-width:0;'
                                header_color = "#64748B"

                            days_grid_html += (
                                f'<div style="{card_style}">'
                                f'<div style="font-weight:700; color:{header_color}; font-size:0.8rem; text-align:center; border-bottom:1px solid #E2E8F0; padding-bottom:4px; text-transform:uppercase;">{short_day}</div>'
                                f'{metrics_html}'
                                '</div>'
                            )

                        card_html = (
                            '<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">'
                            f'<div style="font-weight:800; color:#0F172A; font-size:1rem; margin-bottom:12px;">{ath_name}</div>'
                            f'<div style="display:flex; gap:10px; width:100%;">{days_grid_html}</div>'
                            '</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.info("No athlete tracking data available.")
            else:
                st.info(f"No tracking data recorded for the week of {track_week_str}.")


# -----------------------------------------------------------------------------
# 8. TAB ROUTING
# -----------------------------------------------------------------------------
with season_tab_summer:
    render_dashboard_content("Summer", "summer")

with season_tab_post_summer:
    render_dashboard_content("Pre-Season", "pre_season")
