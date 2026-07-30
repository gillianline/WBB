import io
import urllib.request
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import requests

def save_to_secret_sheet(athlete, metric, count_val):
    sheet_url = st.secrets.get("Live Track") or st.secrets.get("sheets", {}).get("live_track_url")
    
    if not sheet_url:
        print("Sync Error: No URL found in st.secrets")
        return

    payload = {
        "Week_Starting": str(week_starting),
        "Athlete": athlete,
        "Metric": metric,
        "Day": day_selected,
        "Count": int(count_val),
    }

    try:
        # requests.post automatically follows Google's 302 redirects while preserving payload data
        response = requests.post(sheet_url, json=payload, timeout=5)
        print(f"Sync Response: {response.status_code}")
    except Exception as e:
        print(f"Sync error: {e}")

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
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
        }
        .vball-table th {
            background-color: #F1F5F9; color: #475569; font-weight: 700; text-align: left;
            padding: 8px 12px; border-bottom: 2px solid #E2E8F0; text-transform: uppercase; font-size: 0.72rem;
        }
        .vball-table td { padding: 8px 12px; border-bottom: 1px solid #F1F5F9; color: #0F172A; }
        .vball-table tr:last-child td { border-bottom: none; }
        .grade-badge { font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; }

        .compliance-card {
            background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px;
            padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        .compliance-metric-card {
            background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;
            padding: 10px 8px; text-align: center;
        }
        .compliance-metric-label { font-size: 0.7rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 2px; }
        .compliance-metric-value { font-size: 1.1rem; font-weight: 800; color: #0F172A; }
        .compliance-metric-sub { font-size: 0.7rem; color: #94A3B8; margin-top: 2px; }
    </style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. PASSWORD PROTECTION
# -----------------------------------------------------------------------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown(
            '<div class="console-header">LADY VOLS PERFORMANCE CONSOLE - LOGIN</div>',
            unsafe_allow_html=True,
        )
        pwd = st.text_input("Enter Dashboard Password:", type="password")
        if st.button("Login"):
            target_password = st.secrets.get("dashboard_password", "ladyvols")
            if pwd == target_password:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        return False
    return True


if not check_password():
    st.stop()


# -----------------------------------------------------------------------------
# 3. DATA LOADING VIA SECRETS
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_sheet_data():
    def fetch_csv(secret_key):
        url = st.secrets["sheets"][secret_key]
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req) as response:
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

        # Clean date columns across all dataframes
        # Clean date columns across all dataframes
        for df in [vol_df, int_df, comp_df, weekly_df, cmj_df]:
            date_col = [c for c in df.columns if "date" in c.lower()]
            if date_col:
                df["Date"] = pd.to_datetime(df[date_col[0]], errors="coerce")
                df["Date_Str"] = df["Date"].dt.strftime("%Y-%m-%d")  # Ensures clean YYYY-MM-DD

        return vol_df, int_df, comp_df, weekly_df, cmj_df, roster_df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets secrets: {e}")
        st.stop()


vol_raw, int_raw, comp_raw, weekly_raw, cmj_raw, roster_raw = load_sheet_data()

def auto_save_live_tally(player_name, metric, new_val, track_date, session_type):
    """Sends immediate updates to your secret Google Sheet backend."""
    save_url = st.secrets["sheets"].get("live_tracking_url")
    if save_url:
        payload = {
            "Date": str(track_date),
            "Session": session_type,
            "Player": player_name,
            "Metric": metric,
            "Value": new_val,
        }
        try:
            req = urllib.request.Request(
                save_url,
                data=str(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                pass
        except Exception as e:
            # Silent fallback / background log so UI stays fast
            print(f"Auto-save warning: {e}")
            
# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_vball_color(score):
    if score is None or pd.isna(score):
        return "#E2E8F0", "#475569"
    if score < 50:
        return "#BBF7D0", "#166534"  # Green
    elif score < 75:
        return "#FEF08A", "#854D0E"  # Yellow
    else:
        return "#FFD6D6", "#991B1B"  # Red


def render_vball_table(df):
    html = '<table class="vball-table"><thead><tr>'
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
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


def compute_practice_tables(player_name, session_date_str):
    v_player = vol_raw[
        (vol_raw["Player"] == player_name)
        & (vol_raw["Date_Str"] == str(session_date_str))
    ]
    i_player = int_raw[
        (int_raw["Player"] == player_name)
        & (int_raw["Date_Str"] == str(session_date_str))
    ]

    v_base = (
        vol_raw[vol_raw["Player"] == player_name].sort_values("Date").head(14)
    )
    i_base = (
        int_raw[int_raw["Player"] == player_name].sort_values("Date").head(14)
    )

    vol_metrics = [
        "Distance (mi)",
        "Accumulated Acceleration Load",
        "Decels Load",
        "FCTs",
        "Physio Load",
        "Mechanical Load",
        "Jump Load (J)",
    ]
    int_metrics = [
        "Physio Intensity",
        "Acceleration Load (load | High AAL)",
        "Distance (speed | High Speed) (mi)",
        "Speed (max.) (mph)",
        "Sprints",
        "Exertions",
        "High Metabolic Power Distance (m)",
    ]

    vol_rows, int_rows = [], []

    for m in vol_metrics:
        curr = (
            v_player[m].values[0] if not v_player.empty and m in v_player else 0.0
        )
        mx = v_base[m].max() if not v_base.empty and m in v_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        vol_rows.append({"Metric": m, "Current": curr, "Max": mx, "Grade": grade})

    for m in int_metrics:
        curr = (
            i_player[m].values[0] if not i_player.empty and m in i_player else 0.0
        )
        mx = i_base[m].max() if not i_base.empty and m in i_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        int_rows.append({"Metric": m, "Current": curr, "Max": mx, "Grade": grade})

    vol_df_out = pd.DataFrame(vol_rows)
    int_df_out = pd.DataFrame(int_rows)

    vol_score = int(vol_df_out["Grade"].mean()) if not vol_df_out.empty else 0
    int_score = int(int_df_out["Grade"].mean()) if not int_df_out.empty else 0

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
        minutes,
        week_num,
        day_num,
    )


def get_clean_jump_col(df):
    for col in df.columns:
        if "jump height" in col.lower():
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[^0-9.]", "", regex=True),
                errors="coerce",
            )
            return col
    return None


# -----------------------------------------------------------------------------
# 5. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.markdown("### LADY VOLS BASKETBALL")
st.sidebar.caption("Performance Analytics Console")

main_tab = st.sidebar.radio(
    "Console View:",
    options=[
        "Individual Profile",
        "Practice Score",
        "Compliance",
        "Weekly Data",
        "Testing",
        "Live Tracking"
    ],
    index=0,
)

st.sidebar.divider()
st.sidebar.markdown("### DATA MANAGEMENT")

if st.sidebar.button("🔄 Refresh Google Sheets Data"):
    st.cache_data.clear()
    st.sidebar.success("Data reloaded!")
    st.rerun()

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()


# -----------------------------------------------------------------------------
# 6. VIEW CONTROLLERS
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="console-header">
        <span>LADY VOLS BASKETBALL ANALYTICS</span>
        <span style="font-size: 0.9rem; font-weight: 600; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 4px;">SUMMER PHASE</span>
    </div>
""",
    unsafe_allow_html=True,
)

active_season = st.tabs(["Summer"])[0]

with active_season:
    st.markdown("<br>", unsafe_allow_html=True)
    roster_players = (
        roster_raw["Name"].tolist()
        if not roster_raw.empty
        else vol_raw["Player"].unique().tolist()
    )

    # =========================================================================
    # TAB 1: INDIVIDUAL PROFILE
    # =========================================================================
    if main_tab == "Individual Profile":
        c_sel, _ = st.columns([1, 2])
        with c_sel:
            selected_player = st.selectbox("Select Athlete Profile:", roster_players)

        p_row = roster_raw[roster_raw["Name"] == selected_player]
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

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown(
                '<div class="vball-section-title">Practice Scores History</div>',
                unsafe_allow_html=True,
            )
            v_p = vol_raw[vol_raw["Player"] == selected_player].sort_values("Date")

            if not v_p.empty:
                score_history = []
                for d_str in v_p["Date_Str"].unique():
                    _, _, v_sc, i_sc, _, _, _ = compute_practice_tables(
                        selected_player, d_str
                    )
                    score_history.append(
                        {"Date": d_str, "Volume Score": v_sc, "Intensity Score": i_sc}
                    )

                df_score_trend = pd.DataFrame(score_history)

                fig1 = px.line(
                    df_score_trend,
                    x="Date",
                    y=["Volume Score", "Intensity Score"],
                    markers=True,
                    color_discrete_sequence=["#FF8200", "#38BDF8"],
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
                st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            st.markdown(
                '<div class="vball-section-title">CMJ History</div>',
                unsafe_allow_html=True,
            )
            cmj_p = cmj_raw[cmj_raw["Name"] == selected_player].sort_values("Date")
            j_col = get_clean_jump_col(cmj_p)

            if not cmj_p.empty and j_col:
                fig2 = px.bar(
                    cmj_p, x="Date_Str", y=j_col, color_discrete_sequence=["#94A3B8"]
                )
                fig2.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=230,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title=None,
                    yaxis_title="Jump Height",
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        st.markdown("### Most Recent Practice Score Breakdown")
        latest_date_str = vol_raw[vol_raw["Player"] == selected_player][
            "Date_Str"
        ].max()

        if pd.notna(latest_date_str):
            vol_df, int_df, vol_score, int_score, mins, wk, dy = (
                compute_practice_tables(selected_player, latest_date_str)
            )

            wk_str = str(wk).replace("Week ", "")
            dy_str = str(dy).replace("Day ", "")

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

            col_v, col_i = st.columns(2)

            with col_v:
                st.markdown(
                    '<div class="vball-section-title">Volume Score Metrics</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(render_vball_table(vol_df), unsafe_allow_html=True)
                v_bg, v_fg = get_vball_color(vol_score)
                st.markdown(
                    f"""
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center; margin-top:10px;">
                            <div style="font-weight: 700; color: #64748B; font-size: 0.9rem;">VOLUME SCORE</div>
                            <div style="font-size: 2rem; font-weight: 800; padding: 6px 0; border-radius: 6px; background-color: {v_bg}; color: {v_fg}; margin-top: 4px;">{vol_score}</div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_i:
                st.markdown(
                    '<div class="vball-section-title">Intensity Score Metrics</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(render_vball_table(int_df), unsafe_allow_html=True)
                i_bg, i_fg = get_vball_color(int_score)
                st.markdown(
                    f"""
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center; margin-top:10px;">
                            <div style="font-weight: 700; color: #64748B; font-size: 0.9rem;">INTENSITY SCORE</div>
                            <div style="font-size: 2rem; font-weight: 800; padding: 6px 0; border-radius: 6px; background-color: {i_bg}; color: {i_fg}; margin-top: 4px;">{int_score}</div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

    # =========================================================================
    # TAB 2: PRACTICE SCORE
    # =========================================================================
    elif main_tab == "Practice Score":
        c_d, _ = st.columns([1, 3])
        with c_d:
            available_dates = (
                vol_raw["Date_Str"].sort_values(ascending=False).unique()
            )
            session_date = st.selectbox("Select Session Date:", available_dates)

        st.markdown("<br>", unsafe_allow_html=True)

        for player_name in roster_players:
            p_row = roster_raw[roster_raw["Name"] == player_name]
            p_pos = (
                p_row["Position"].values[0] if not p_row.empty else "Guard / Forward"
            )
            p_img = (
                p_row["Picture"].values[0]
                if not p_row.empty
                else "https://via.placeholder.com/70"
            )

            vol_df, int_df, vol_score, int_score, mins, wk, dy = (
                compute_practice_tables(player_name, str(session_date))
            )

            vol_html_table = render_vball_table(vol_df)
            int_html_table = render_vball_table(int_df)

            v_bg, v_fg = get_vball_color(vol_score)
            i_bg, i_fg = get_vball_color(int_score)

            wk_str = str(wk).replace("Week ", "")
            dy_str = str(dy).replace("Day ", "")

            single_box_card_html = f"""
            <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <img src="{p_img}" style="width:60px; height:60px; border-radius:50%; border:3px solid #FF8200; object-fit:cover;">
                        <div>
                            <h3 style="margin:0; font-size:1.3rem; color:#0F172A; font-weight:700;">{player_name}</h3>
                            <span style="color:#64748B; font-size:0.85rem;">{p_pos}</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Minutes: {mins}</span>
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Week {wk_str}</span>
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Day {dy_str}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 20px; width: 100%;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="background-color:#38BDF8; color:#0F172A; font-weight:700; font-size:0.95rem; padding:6px 12px; border-radius:6px; text-align:center; margin-bottom:12px; text-transform:uppercase;">Volume Metrics</div>
                        {vol_html_table}
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center; margin-top:10px;">
                            <div style="font-weight:700; color:#64748B; font-size:0.85rem;">VOLUME SCORE</div>
                            <div style="font-size:2rem; font-weight:800; padding:6px 0; border-radius:6px; background-color:{v_bg}; color:{v_fg}; margin-top:4px;">{vol_score}</div>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="background-color:#38BDF8; color:#0F172A; font-weight:700; font-size:0.95rem; padding:6px 12px; border-radius:6px; text-align:center; margin-bottom:12px; text-transform:uppercase;">Intensity Metrics</div>
                        {int_html_table}
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center; margin-top:10px;">
                            <div style="font-weight:700; color:#64748B; font-size:0.85rem;">INTENSITY SCORE</div>
                            <div style="font-size:2rem; font-weight:800; padding:6px 0; border-radius:6px; background-color:{i_bg}; color:{i_fg}; margin-top:4px;">{int_score}</div>
                        </div>
                    </div>
                </div>
            </div>
            """

            st.markdown(single_box_card_html, unsafe_allow_html=True)

    # =========================================================================
    # TAB 3: COMPLIANCE
    # =========================================================================
    elif main_tab == "Compliance":
        comp_sub_tab1, comp_sub_tab2 = st.tabs(
            ["Speed Compliance", "CMJ Compliance"]
        )

        with comp_sub_tab1:
            st.markdown(
                '<div class="vball-section-title">Max Speed & Exposure Compliance Grid</div>',
                unsafe_allow_html=True,
            )

            for i in range(0, len(roster_players), 2):
                col1, col2 = st.columns(2)
                cols = [col1, col2]

                for j in range(2):
                    if i + j < len(roster_players):
                        player_name = roster_players[i + j]
                        p_row = roster_raw[roster_raw["Name"] == player_name]
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

                        p_comp = comp_raw[comp_raw["Player"] == player_name].sort_values(
                            "Date"
                        )

                        if not p_comp.empty:
                            all_time_max = p_comp["Speed (MPH)"].max()
                            max_row = p_comp[p_comp["Speed (MPH)"] == all_time_max].iloc[-1]
                            max_date = max_row["Date_Str"]

                            recent_row = p_comp.iloc[-1]
                            recent_speed = recent_row["Speed (MPH)"]
                            recent_date = recent_row["Date_Str"]

                            pct_max = (
                                f"{(recent_speed / all_time_max * 100):.1f}%"
                                if all_time_max > 0
                                else "-- %"
                            )
                            days_since = (
                                pd.to_datetime("today") - pd.to_datetime(max_date)
                            ).days

                            badge_bg = "#BBF7D0" if days_since <= 7 else "#FFD6D6"
                            badge_fg = "#166534" if days_since <= 7 else "#991B1B"

                            with cols[j]:
                                st.markdown(
                                    f"""
                                    <div class="compliance-card">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                            <div style="display: flex; align-items: center; gap: 12px;">
                                                <img src="{p_img}" class="athlete-avatar" style="width:50px; height:50px;">
                                                <div>
                                                    <h4 style="margin:0; font-size:1.1rem; color:#0F172A;">{player_name}</h4>
                                                    <span style="color:#64748B; font-size:0.8rem;">{p_pos}</span>
                                                </div>
                                            </div>
                                            <div style="background-color:{badge_bg}; color:{badge_fg}; font-weight:700; padding:4px 10px; border-radius:12px; font-size:0.75rem;">
                                                {days_since} Days
                                            </div>
                                        </div>
                                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">Recent Speed</div>
                                                <div class="compliance-metric-value">{recent_speed:.1f} mph</div>
                                                <div class="compliance-metric-sub">{recent_date}</div>
                                            </div>
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">All-Time Max Speed</div>
                                                <div class="compliance-metric-value">{all_time_max:.1f} mph</div>
                                                <div class="compliance-metric-sub">{max_date}</div>
                                            </div>
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">% of All-Time Max</div>
                                                <div class="compliance-metric-value" style="color:#FF8200;">{pct_max}</div>
                                                <div class="compliance-metric-sub">Recent vs. Peak Output</div>
                                            </div>
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">Recency Status</div>
                                                <div class="compliance-metric-value">{days_since} Days</div>
                                                <div class="compliance-metric-sub">Elapsed Threshold</div>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

        with comp_sub_tab2:
            st.markdown(
                '<div class="vball-section-title">CMJ Jump Height Exposure & Compliance Grid</div>',
                unsafe_allow_html=True,
            )

            for i in range(0, len(roster_players), 2):
                col1, col2 = st.columns(2)
                cols = [col1, col2]

                for j in range(2):
                    if i + j < len(roster_players):
                        player_name = roster_players[i + j]
                        p_row = roster_raw[roster_raw["Name"] == player_name]
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

                        p_cmj = cmj_raw[cmj_raw["Name"] == player_name].sort_values("Date")
                        j_col = get_clean_jump_col(p_cmj)

                        if not p_cmj.empty and j_col:
                            all_time_max_cmj = p_cmj[j_col].max()
                            max_row_cmj = p_cmj[p_cmj[j_col] == all_time_max_cmj].iloc[-1]
                            max_date_cmj = max_row_cmj["Date_Str"]

                            recent_row_cmj = p_cmj.iloc[-1]
                            recent_cmj = recent_row_cmj[j_col]
                            recent_date_cmj = recent_row_cmj["Date_Str"]

                            pct_max_cmj = (
                                f"{(recent_cmj / all_time_max_cmj * 100):.1f}%"
                                if all_time_max_cmj > 0
                                else "-- %"
                            )
                            days_since_cmj = (
                                pd.to_datetime("today") - pd.to_datetime(max_date_cmj)
                            ).days

                            badge_bg_cmj = "#BBF7D0" if days_since_cmj <= 7 else "#FFD6D6"
                            badge_fg_cmj = "#166534" if days_since_cmj <= 7 else "#991B1B"

                            with cols[j]:
                                st.markdown(
                                    f"""
                                    <div class="compliance-card">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                            <div style="display: flex; align-items: center; gap: 12px;">
                                                <img src="{p_img}" class="athlete-avatar" style="width:50px; height:50px;">
                                                <div>
                                                    <h4 style="margin:0; font-size:1.1rem; color:#0F172A;">{player_name}</h4>
                                                    <span style="color:#64748B; font-size:0.8rem;">{p_pos}</span>
                                                </div>
                                            </div>
                                            <div style="background-color:{badge_bg_cmj}; color:{badge_fg_cmj}; font-weight:700; padding:4px 10px; border-radius:12px; font-size:0.75rem;">
                                                {days_since_cmj} Days
                                            </div>
                                        </div>
                                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">Recent Jump Height</div>
                                                <div class="compliance-metric-value">{recent_cmj:.1f} cm</div>
                                                <div class="compliance-metric-sub">{recent_date_cmj}</div>
                                            </div>
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">All-Time Max Jump</div>
                                                <div class="compliance-metric-value">{all_time_max_cmj:.1f} cm</div>
                                                <div class="compliance-metric-sub">{max_date_cmj}</div>
                                            </div>
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">% of All-Time Max</div>
                                                <div class="compliance-metric-value" style="color:#FF8200;">{pct_max_cmj}</div>
                                                <div class="compliance-metric-sub">Recent vs. Peak Output</div>
                                            </div>
                                            <div class="compliance-metric-card">
                                                <div class="compliance-metric-label">Recency Status</div>
                                                <div class="compliance-metric-value">{days_since_cmj} Days</div>
                                                <div class="compliance-metric-sub">Elapsed Threshold</div>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

    # =========================================================================
    # TAB 4: WEEKLY DATA
    # =========================================================================
    elif main_tab == "Weekly Data":
        st.markdown(
            '<div class="vball-section-title">1. Team Weekly Accumulation Overview</div>',
            unsafe_allow_html=True,
        )

        weekly_agg = (
            weekly_raw.groupby("Week")
            .agg({
                "Distance (mi)": "sum",
                "Distance (speed | High Speed) (mi)": "sum",
                "Accumulated Acceleration Load": "sum",
                "Decels Load": "sum",
            })
            .reset_index()
        )

        weeks = weekly_agg["Week"].tolist()

        w1, w2 = st.columns(2)
        with w1:
            fig_td = create_clean_bar_chart(
                weeks, weekly_agg["Distance (mi)"], "Total Distance (mi)", "#38BDF8"
            )
            st.plotly_chart(fig_td, use_container_width=True)

            fig_aal = create_clean_bar_chart(
                weeks,
                weekly_agg["Accumulated Acceleration Load"],
                "Accumulated Acceleration Load (AAL)",
                "#FF8200",
            )
            st.plotly_chart(fig_aal, use_container_width=True)

        with w2:
            fig_hsd = create_clean_bar_chart(
                weeks,
                weekly_agg["Distance (speed | High Speed) (mi)"],
                "High Speed Distance (mi)",
                "#38BDF8",
            )
            st.plotly_chart(fig_hsd, use_container_width=True)

            fig_dl = create_clean_bar_chart(
                weeks, weekly_agg["Decels Load"], "Deceleration Load", "#FF8200"
            )
            st.plotly_chart(fig_dl, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="vball-section-title">2. Individual Player Breakdown vs. Team Average</div>',
            unsafe_allow_html=True,
        )
        selected_player_w = st.selectbox("Select Athlete:", roster_players)

        p_weekly = weekly_raw[weekly_raw["Player"] == selected_player_w]
        t_weekly_avg = (
            weekly_raw.groupby("Week")
            .agg({
                "Distance (mi)": "mean",
                "Distance (speed | High Speed) (mi)": "mean",
                "Accumulated Acceleration Load": "mean",
                "Decels Load": "mean",
            })
            .reset_index()
        )

        all_weeks = t_weekly_avg["Week"].tolist()

        def create_team_bar_athlete_line_chart(
            weeks, team_avg_vals, athlete_vals, title_text, bar_color="#38BDF8"
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
                    name=f"{selected_player_w} Output",
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

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_ind_td = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg["Distance (mi)"],
                p_weekly["Distance (mi)"],
                f"Total Distance (mi) — {selected_player_w}",
                "#FF8200",
            )
            st.plotly_chart(fig_ind_td, use_container_width=True)

            fig_ind_aal = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg["Accumulated Acceleration Load"],
                p_weekly["Accumulated Acceleration Load"],
                f"AAL — {selected_player_w}",
                "#38BDF8",
            )
            st.plotly_chart(fig_ind_aal, use_container_width=True)

        with col_p2:
            fig_ind_hsd = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg["Distance (speed | High Speed) (mi)"],
                p_weekly["Distance (speed | High Speed) (mi)"],
                f"High Speed Distance (mi) — {selected_player_w}",
                "#FF8200",
            )
            st.plotly_chart(fig_ind_hsd, use_container_width=True)

            fig_ind_dl = create_team_bar_athlete_line_chart(
                all_weeks,
                t_weekly_avg["Decels Load"],
                p_weekly["Decels Load"],
                f"Deceleration Load — {selected_player_w}",
                "#38BDF8",
            )
            st.plotly_chart(fig_ind_dl, use_container_width=True)

    # =========================================================================
    # TAB 5: TESTING
    # =========================================================================
    elif main_tab == "Testing":
        st.markdown(
            '<div class="vball-section-title">CMJ History</div>',
            unsafe_allow_html=True,
        )

        c_filter, _ = st.columns([1, 2])
        with c_filter:
            selected_player_t = st.selectbox("Select Athlete:", roster_players)

        p_cmj = cmj_raw[cmj_raw["Name"] == selected_player_t].sort_values("Date").copy()

        # Robust column detection
        jump_cols = [c for c in p_cmj.columns if "jump" in c.lower() or "height" in c.lower()]
        j_col = jump_cols[0] if jump_cols else None

        rsi_cols = [c for c in p_cmj.columns if "rsi" in c.lower()]
        rsi_col = rsi_cols[0] if rsi_cols else None

        display_cols = [c for c in p_cmj.columns if c not in ["Name", "Date_Str"]]
        st.markdown(f"### Jump History for {selected_player_t}")
        st.markdown(render_vball_table(p_cmj[display_cols]), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not p_cmj.empty and j_col:
            # Clean numeric values directly
            p_cmj["Jump_Height_Clean"] = pd.to_numeric(
                p_cmj[j_col].astype(str).str.replace(r"[^0-9.]", "", regex=True),
                errors="coerce",
            )

            fig_jump_trend = go.Figure()

            # 1. ORANGE SOLID LINE: JUMP HEIGHT (Left Axis)
            fig_jump_trend.add_trace(
                go.Scatter(
                    x=p_cmj["Date"],  # Pass raw datetime series
                    y=p_cmj["Jump_Height_Clean"],
                    name="Jump Height",
                    mode="lines+markers",
                    connectgaps=True,
                    yaxis="y",
                    line=dict(color="#FF8200", width=4),
                    marker=dict(size=8, color="#FF8200"),
                )
            )

            # 2. BLUE DOTTED LINE: RSI MODIFIED (Right Axis)
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

            # 3. DUAL Y-AXES LAYOUT
            fig_jump_trend.update_layout(
                height=320,
                margin=dict(l=40, r=40, t=50, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                
                # Top-Left Horizontal Legend
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.08,
                    xanchor="left",
                    x=0.01,
                    font=dict(size=13, color="#0F172A"),
                ),
                
                # Bottom X-Axis (Explicit Plotly Date Formatter)
                xaxis=dict(
                    title=None,
                    type="date",
                    tickformat="%b %d\n%Y",  # Overrides default 00:00:00 time format
                    showgrid=False,
                    showline=True,
                    linewidth=1.5,
                    linecolor="#0F172A",
                    tickfont=dict(color="#64748B", size=12),
                ),
                
                # Left Y-Axis (Jump Height)
                yaxis=dict(
                    showgrid=False,
                    showline=True,
                    linewidth=1.5,
                    linecolor="#0F172A",
                    tickfont=dict(color="#64748B", size=12),
                    side="left",
                ),
                
                # Right Y-Axis (RSI Modified)
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

            st.plotly_chart(fig_jump_trend, use_container_width=True)

 # =========================================================================
    # TAB 6: LIVE TRACKING (REAL-TIME TWO-WAY SHEET SYNC)
    # =========================================================================
    elif main_tab == "Live Tracking":
        st.markdown(
            '<div class="vball-section-title">Live Tracking</div>',
            unsafe_allow_html=True,
        )

        # ---------------------------------------------------------------------
        # 1. LIVE SHEET READ ENGINE (ALWAYS PULLS FRESH DATA FROM CLOUD)
        # ---------------------------------------------------------------------
        def fetch_fresh_sheet_data():
            try:
                if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                    # Unique timestamp guarantees Google doesn't serve a cached CSV
                    cache_buster = f"&t={pd.to_datetime('now').timestamp()}"
                    csv_url = url.replace("/edit", f"/gviz/tq?tqx=out:csv&sheet=Sheet1{cache_buster}")
                    return pd.read_csv(csv_url)
            except Exception as e:
                print(f"Sheet fetch error: {e}")
            return pd.DataFrame(
                columns=[
                    "Week_Starting",
                    "Athlete",
                    "Metric",
                    "Day",
                    "Count",
                    "Timestamp",
                ]
            )

        # Pull fresh data from Google Sheets on every run
        live_historical_df = fetch_fresh_sheet_data()
        st.session_state.live_historical_df = live_historical_df

        # ---------------------------------------------------------------------
        # 2. SESSION CONTROLS
        # ---------------------------------------------------------------------
        local_now = pd.to_datetime("now") - pd.Timedelta(hours=4)
        today = local_now.date()
        current_monday = today - pd.Timedelta(days=today.weekday())

        col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
        with col_s1:
            selected_monday = st.date_input("Week Starting:", value=current_monday, key="lt_selected_monday")
            if selected_monday.weekday() != 0:
                selected_monday = selected_monday - pd.Timedelta(days=selected_monday.weekday())
            week_str = selected_monday.strftime("%Y-%m-%d")
        with col_s2:
            day_selected = st.selectbox(
                "Day:", 
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                key="lt_day_selected"
            )
        with col_s3:
            if st.button("🔄 Refresh Sheet Data", key="manual_sheet_sync"):
                st.cache_data.clear()
                st.rerun()

        metrics_to_track = ["Box Out", "Turnovers", "Offensive Rebounds"]

        st.divider()

        # ---------------------------------------------------------------------
        # 3. PLAYER CARDS (2-COLUMN GRID SIDE-BY-SIDE)
        # ---------------------------------------------------------------------
        st.markdown("### Player Trackers")

        roster_df = roster_raw if 'roster_raw' in locals() else roster
        roster_list = roster_df.to_dict('records')

        for i in range(0, len(roster_list), 2):
            col1, col2 = st.columns(2)
            cols = [col1, col2]

            for j in range(2):
                if i + j < len(roster_list):
                    player_data = roster_list[i + j]
                    p_name = player_data.get("Athlete") or player_data.get("Name")
                    p_pos = player_data.get("Position", "Guard / Forward")
                    p_img = str(player_data.get("Picture")) if pd.notna(player_data.get("Picture")) else "https://cdn-icons-png.flaticon.com/512/186/186037.png"

                    with cols[j]:
                        with st.container():
                            st.markdown(
                                f"""
                                <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                                    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px; border-bottom: 1px solid #E2E8F0; margin-bottom: 12px;">
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <img src="{p_img}" style="width:50px; height:50px; border-radius:50%; border:2px solid #FF8200; object-fit:cover;">
                                            <div>
                                                <h4 style="margin:0; font-size:1.1rem; color:#0F172A; font-weight:700;">{p_name}</h4>
                                                <span style="color:#64748B; font-size:0.8rem;">{p_pos}</span>
                                            </div>
                                        </div>
                                    </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            for m in metrics_to_track:
                                # Count occurrences dynamically from fresh live_historical_df
                                current_count = 0
                                if not live_historical_df.empty and set(["Athlete", "Metric", "Day"]).issubset(live_historical_df.columns):
                                    matches = live_historical_df[
                                        (live_historical_df["Athlete"].astype(str).str.strip() == str(p_name).strip()) &
                                        (live_historical_df["Metric"].astype(str).str.strip() == str(m).strip()) &
                                        (live_historical_df["Day"].astype(str).str.strip() == str(day_selected).strip())
                                    ]
                                    current_count = len(matches)

                                m_col1, m_col2, m_col3, m_col4 = st.columns([2.8, 1, 1, 1])

                                with m_col1:
                                    st.markdown(f"<div style='font-size:0.9rem; font-weight:600; color:#0F172A; padding-top:4px;'>{m}</div>", unsafe_allow_html=True)

                                with m_col2:
                                    if st.button("➖", key=f"dec_{p_name.replace(' ', '')}_{m}_{day_selected}"):
                                        if current_count > 0:
                                            target_url = (
                                                st.secrets.get("MACRO_URL") 
                                                or st.secrets.get("Live Track") 
                                                or st.secrets.get("sheets", {}).get("live_track_url")
                                            )
                                            payload = {
                                                "Week_Starting": week_str,
                                                "Athlete": str(p_name).strip(),
                                                "Metric": str(m).strip(),
                                                "Day": str(day_selected).strip(),
                                                "Action": "remove",
                                            }
                                            if target_url:
                                                try:
                                                    requests.post(target_url, json=payload, timeout=4)
                                                except Exception as err:
                                                    print(f"Sync error: {err}")

                                            st.cache_data.clear()
                                            st.rerun()

                                with m_col3:
                                    st.markdown(f"<div style='text-align:center; font-size:1.1rem; font-weight:800; color:#FF8200; padding-top:2px;'>{current_count}</div>", unsafe_allow_html=True)

                                with m_col4:
                                    if st.button("➕", key=f"inc_{p_name.replace(' ', '')}_{m}_{day_selected}"):
                                        time_str = local_now.strftime("%m/%d/%Y %H:%M:%S")

                                        target_url = (
                                            st.secrets.get("MACRO_URL") 
                                            or st.secrets.get("Live Track") 
                                            or st.secrets.get("sheets", {}).get("live_track_url")
                                        )
                                        payload = {
                                            "Week_Starting": week_str,
                                            "Athlete": str(p_name).strip(),
                                            "Metric": str(m).strip(),
                                            "Day": str(day_selected).strip(),
                                            "Count": 1,
                                            "Timestamp": time_str,
                                            "Action": "add",
                                        }
                                        if target_url:
                                            try:
                                                requests.post(target_url, json=payload, timeout=4)
                                            except Exception as err:
                                                print(f"Sync error: {err}")

                                        st.cache_data.clear()
                                        st.rerun()

                            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 4. TRACKING SUMMARY TABLE
        # ---------------------------------------------------------------------
        st.divider()
        st.markdown("### Session Summary Table")

        summary_list = []
        for p in [r.get("Athlete") or r.get("Name") for r in roster_list]:
            row_dict = {
                "Week_Starting": week_str,
                "Athlete": p,
                "Day": day_selected,
            }
            for m in metrics_to_track:
                count_val = 0
                if not live_historical_df.empty and set(["Athlete", "Metric", "Day"]).issubset(live_historical_df.columns):
                    match_records = live_historical_df[
                        (live_historical_df["Athlete"].astype(str).str.strip() == str(p).strip()) &
                        (live_historical_df["Metric"].astype(str).str.strip() == str(m).strip()) &
                        (live_historical_df["Day"].astype(str).str.strip() == str(day_selected).strip())
                    ]
                    count_val = len(match_records)
                row_dict[m] = count_val
            summary_list.append(row_dict)

        df_live_summary = pd.DataFrame(summary_list)
        st.markdown(render_vball_table(df_live_summary), unsafe_allow_html=True)
