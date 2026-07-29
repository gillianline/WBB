import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import urllib.request

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lady Vols Basketball | Performance Console",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
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
            border: 1px solid #E2E8F0;
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
        .athlete-info h2 { margin: 0; font-size: 1.4rem; font-weight: 700; color: #0F172A; }
        .athlete-info p { margin: 2px 0 0 0; color: #64748B; font-size: 0.88rem; }

        .vball-section-title {
            background-color: #38BDF8; color: #0F172A; font-weight: 700; font-size: 1.05rem;
            padding: 8px 16px; border-radius: 6px; text-align: center;
            margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;
        }

        .score-box-container {
            background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
            padding: 10px; text-align: center; margin-top: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .score-box-value {
            font-size: 2rem; font-weight: 800; padding: 6px 0; border-radius: 6px;
            color: #0F172A; margin-top: 4px;
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
        
        .light-card-box {
            background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
            padding: 15px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }

        /* Unified Roster Card Styling for Practice & Compliance */
        .roster-card {
            background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px;
            padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }

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
        
        .session-meta-pill {
            background-color: #F1F5F9; border: 1px solid #E2E8F0; color: #475569;
            padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;
        }
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. PASSWORD PROTECTION
# -----------------------------------------------------------------------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown('<div class="console-header">LADY VOLS PERFORMANCE CONSOLE - LOGIN</div>', unsafe_allow_html=True)
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
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return pd.read_csv(response, on_bad_lines='skip', engine='python')

    try:
        vol_df = fetch_csv("volume_url")
        int_df = fetch_csv("intensity_url")
        comp_df = fetch_csv("compliance_url")
        weekly_df = fetch_csv("weekly_url")
        cmj_df = fetch_csv("cmj_url")
        roster_df = fetch_csv("roster_url")

        for df in [vol_df, int_df, comp_df, weekly_df, cmj_df]:
            date_col = [c for c in df.columns if "date" in c.lower()]
            if date_col:
                df[date_col[0]] = pd.to_datetime(df[date_col[0]])

        return vol_df, int_df, comp_df, weekly_df, cmj_df, roster_df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets secrets: {e}")
        st.stop()

vol_raw, int_raw, comp_raw, weekly_raw, cmj_raw, roster_raw = load_sheet_data()


# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS & COLOR LOGIC (Green = Low Load)
# -----------------------------------------------------------------------------
def get_vball_color(score):
    if score is None or pd.isna(score): return "#E2E8F0", "#475569"
    if score < 50: return "#BBF7D0", "#166534"      # Green (Low/Optimal Load)
    elif score < 75: return "#FEF08A", "#854D0E"    # Yellow (Moderate)
    else: return "#FFD6D6", "#991B1B"               # Red (High Load)

def render_vball_table(df):
    html = '<table class="vball-table"><thead><tr>'
    for col in df.columns: html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = row[col]
            if col == "Grade":
                bg_c, fg_c = get_vball_color(val)
                html += f'<td><span class="grade-badge" style="background-color:{bg_c}; color:{fg_c};">{val}</span></td>'
            elif isinstance(val, float): html += f'<td>{val:.2f}</td>'
            else: html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def create_clean_bar_chart(x_vals, y_vals, title_text, bar_color="#38BDF8"):
    fig = px.bar(x=x_vals, y=y_vals, title=title_text)
    fig.update_traces(marker_color=bar_color)
    fig.update_layout(
        title_font=dict(size=14, color="#0F172A"),
        height=240, margin=dict(l=0, r=0, t=35, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title=None, yaxis_title=None
    )
    return fig

def compute_practice_tables(player_name, session_date):
    v_player = vol_raw[(vol_raw['Player'] == player_name) & (vol_raw['Date'] == session_date)]
    i_player = int_raw[(int_raw['Player'] == player_name) & (int_raw['Date'] == session_date)]
    
    v_base = vol_raw[vol_raw['Player'] == player_name].sort_values('Date').head(14)
    i_base = int_raw[int_raw['Player'] == player_name].sort_values('Date').head(14)

    vol_metrics = ["Distance (mi)", "Accumulated Acceleration Load", "Decels Load", "FCTs", "Physio Load", "Mechanical Load", "Jump Load (J)"]
    int_metrics = ["Physio Intensity", "Acceleration Load (load | High AAL)", "Distance (speed | High Speed) (mi)", "Speed (max.) (mph)", "Sprints", "Exertions", "High Metabolic Power Distance (m)"]

    vol_rows, int_rows = [], []

    for m in vol_metrics:
        curr = v_player[m].values[0] if not v_player.empty and m in v_player else 0.0
        mx = v_base[m].max() if not v_base.empty and m in v_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        vol_rows.append({"Metric": m, "Current": curr, "Max": mx, "Grade": grade})

    for m in int_metrics:
        curr = i_player[m].values[0] if not i_player.empty and m in i_player else 0.0
        mx = i_base[m].max() if not i_base.empty and m in i_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        int_rows.append({"Metric": m, "Current": curr, "Max": mx, "Grade": grade})

    vol_df_out = pd.DataFrame(vol_rows)
    int_df_out = pd.DataFrame(int_rows)

    vol_score = int(vol_df_out['Grade'].mean()) if not vol_df_out.empty else 0
    int_score = int(int_df_out['Grade'].mean()) if not int_df_out.empty else 0

    minutes = v_player['Minutes'].values[0] if not v_player.empty and 'Minutes' in v_player else "--"
    week_num = v_player['Week'].values[0] if not v_player.empty and 'Week' in v_player else "--"
    day_num = v_player['Day'].values[0] if not v_player.empty and 'Day' in v_player else "--"

    return vol_df_out, int_df_out, vol_score, int_score, minutes, week_num, day_num


# -----------------------------------------------------------------------------
# 5. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.markdown("### LADY VOLS BASKETBALL")
st.sidebar.caption("Performance Analytics Console")

main_tab = st.sidebar.radio(
    "Console View:",
    options=["Individual Profile", "Practice Score", "Compliance", "Weekly Data", "Testing"],
    index=0
)

st.sidebar.divider()
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()


# -----------------------------------------------------------------------------
# 6. VIEW CONTROLLERS
# -----------------------------------------------------------------------------

st.markdown("""
    <div class="console-header">
        <span>LADY VOLS BASKETBALL ANALYTICS</span>
        <span style="font-size: 0.9rem; font-weight: 600; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 4px;">SUMMER PHASE</span>
    </div>
""", unsafe_allow_html=True)

active_season = st.tabs(["Summer"])[0]

with active_season:
    st.markdown("<br>", unsafe_allow_html=True)
    roster_players = roster_raw['Name'].tolist() if not roster_raw.empty else vol_raw['Player'].unique().tolist()

    # =========================================================================
    # TAB 1: INDIVIDUAL PROFILE (Practice Trend + CMJ + Daily Score Breakdown)
    # =========================================================================
    if main_tab == "Individual Profile":
        c_sel, _ = st.columns([1, 2])
        with c_sel:
            selected_player = st.selectbox("Select Athlete Profile:", roster_players)

        p_row = roster_raw[roster_raw['Name'] == selected_player]
        p_pos = p_row['Position'].values[0] if not p_row.empty else "Guard / Forward | #00"
        p_img = p_row['Picture'].values[0] if not p_row.empty else "https://via.placeholder.com/80"

        st.markdown(f"""
            <div class="athlete-card">
                <img src="{p_img}" class="athlete-avatar">
                <div class="athlete-info">
                    <h2>{selected_player}</h2>
                    <p>{p_pos}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown('<div class="vball-section-title">Practice Scores History</div>', unsafe_allow_html=True)
            v_p = vol_raw[vol_raw['Player'] == selected_player].sort_values('Date')
            
            if not v_p.empty:
                score_history = []
                for d in v_p['Date'].unique():
                    _, _, v_sc, i_sc, _, _, _ = compute_practice_tables(selected_player, d)
                    score_history.append({"Date": d, "Volume Score": v_sc, "Intensity Score": i_sc})
                
                df_score_trend = pd.DataFrame(score_history)

                fig1 = px.line(
                    df_score_trend, 
                    x="Date", 
                    y=["Volume Score", "Intensity Score"], 
                    markers=True, 
                    color_discrete_sequence=["#FF8200", "#38BDF8"]
                )
                fig1.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0), 
                    height=230, 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
                )
                st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col_g2:
            st.markdown('<div class="vball-section-title">CMJ History</div>', unsafe_allow_html=True)
            cmj_p = cmj_raw[cmj_raw['Name'] == selected_player].sort_values('Date')
            if not cmj_p.empty:
                fig2 = px.bar(cmj_p, x="Date", y="Jump Height (Imp-Mom) [cm]", color_discrete_sequence=["#94A3B8"])
                fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=230, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        st.markdown('### Most Recent Practice Score Breakdown')
        latest_date = vol_raw[vol_raw['Player'] == selected_player]['Date'].max()
        if pd.notna(latest_date):
            vol_df, int_df, vol_score, int_score, mins, wk, dy = compute_practice_tables(selected_player, latest_date)
            
            st.markdown(f"""
                <div style="margin-bottom: 12px; display: flex; gap: 10px;">
                    <span class="session-meta-pill">Minutes: {mins}</span>
                    <span class="session-meta-pill">Week: {wk}</span>
                    <span class="session-meta-pill">Day: {dy}</span>
                </div>
            """, unsafe_allow_html=True)

            col_v, col_i = st.columns(2)

            with col_v:
                st.markdown('<div class="vball-section-title">Volume Score Metrics</div>', unsafe_allow_html=True)
                st.markdown(render_vball_table(vol_df), unsafe_allow_html=True)
                v_bg, v_fg = get_vball_color(vol_score)
                st.markdown(f"""
                    <div class="score-box-container">
                        <div style="font-weight: 700; color: #64748B; font-size: 0.9rem;">VOLUME SCORE</div>
                        <div class="score-box-value" style="background-color: {v_bg}; color: {v_fg};">{vol_score}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_i:
                st.markdown('<div class="vball-section-title">Intensity Score Metrics</div>', unsafe_allow_html=True)
                st.markdown(render_vball_table(int_df), unsafe_allow_html=True)
                i_bg, i_fg = get_vball_color(int_score)
                st.markdown(f"""
                    <div class="score-box-container">
                        <div style="font-weight: 700; color: #64748B; font-size: 0.9rem;">INTENSITY SCORE</div>
                        <div class="score-box-value" style="background-color: {i_bg}; color: {i_fg};">{int_score}</div>
                    </div>
                """, unsafe_allow_html=True)


    # =========================================================================
    # TAB 2: PRACTICE SCORE (100% Single Box HTML Container)
    # =========================================================================
    elif main_tab == "Practice Score":
        c_d, _ = st.columns([1, 3])
        with c_d:
            available_dates = vol_raw['Date'].sort_values(ascending=False).dt.date.unique()
            session_date = st.selectbox("Select Session Date:", available_dates)

        st.markdown("<br>", unsafe_allow_html=True)

        for player_name in roster_players:
            p_row = roster_raw[roster_raw['Name'] == player_name]
            p_pos = p_row['Position'].values[0] if not p_row.empty else "Forward"
            p_img = p_row['Picture'].values[0] if not p_row.empty else "https://via.placeholder.com/70"

            vol_df, int_df, vol_score, int_score, mins, wk, dy = compute_practice_tables(player_name, pd.to_datetime(session_date))

            vol_html_table = render_vball_table(vol_df)
            int_html_table = render_vball_table(int_df)

            v_bg, v_fg = get_vball_color(vol_score)
            i_bg, i_fg = get_vball_color(int_score)

            # Single HTML string containing the outer card and inner 2-column flexbox grid
            single_box_card_html = f"""
            <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                
                <!-- TOP HEADER INSIDE BOX -->
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
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Week {wk}</span>
                        <span style="background:#F1F5F9; border:1px solid #E2E8F0; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.8rem;">Day {dy}</span>
                    </div>
                </div>

                <!-- DUAL TABLES FLEX GRID INSIDE THE SAME BOX -->
                <div style="display: flex; gap: 20px; width: 100%;">
                    
                    <!-- LEFT COLUMN: VOLUME METRICS -->
                    <div style="flex: 1; min-width: 0;">
                        <div style="background-color:#38BDF8; color:#0F172A; font-weight:700; font-size:0.95rem; padding:6px 12px; border-radius:6px; text-align:center; margin-bottom:12px; text-transform:uppercase;">Volume Metrics</div>
                        {vol_html_table}
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center; margin-top:10px;">
                            <div style="font-weight:700; color:#64748B; font-size:0.85rem;">VOLUME SCORE</div>
                            <div style="font-size:2rem; font-weight:800; padding:6px 0; border-radius:6px; background-color:{v_bg}; color:{v_fg}; margin-top:4px;">{vol_score}</div>
                        </div>
                    </div>

                    <!-- RIGHT COLUMN: INTENSITY METRICS -->
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
    # TAB 3: COMPLIANCE (Sub-Tabs for Speed & CMJ Grids)
    # =========================================================================
    elif main_tab == "Compliance":
        comp_sub_tab1, comp_sub_tab2 = st.tabs(["Speed Compliance", "CMJ Compliance"])

        with comp_sub_tab1:
            st.markdown('<div class="vball-section-title">Max Speed & Exposure Compliance Grid</div>', unsafe_allow_html=True)

            for i in range(0, len(roster_players), 2):
                col1, col2 = st.columns(2)
                cols = [col1, col2]

                for j in range(2):
                    if i + j < len(roster_players):
                        player_name = roster_players[i + j]
                        p_row = roster_raw[roster_raw['Name'] == player_name]
                        p_pos = p_row['Position'].values[0] if not p_row.empty else "Guard / Forward | #00"
                        p_img = p_row['Picture'].values[0] if not p_row.empty else "https://via.placeholder.com/60"

                        p_comp = comp_raw[comp_raw['Player'] == player_name].sort_values('Date')

                        if not p_comp.empty:
                            all_time_max = p_comp['Speed (MPH)'].max()
                            max_row = p_comp[p_comp['Speed (MPH)'] == all_time_max].iloc[-1]
                            max_date = max_row['Date'].strftime('%Y-%m-%d')

                            recent_row = p_comp.iloc[-1]
                            recent_speed = recent_row['Speed (MPH)']
                            recent_date = recent_row['Date'].strftime('%Y-%m-%d')

                            pct_max = f"{(recent_speed / all_time_max * 100):.1f}%" if all_time_max > 0 else "-- %"
                            days_since = (pd.to_datetime('today') - pd.to_datetime(max_date)).days

                            badge_bg = "#BBF7D0" if days_since <= 7 else "#FFD6D6"
                            badge_fg = "#166534" if days_since <= 7 else "#991B1B"

                            with cols[j]:
                                st.markdown(f"""
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
                                """, unsafe_allow_html=True)

        with comp_sub_tab2:
            st.markdown('<div class="vball-section-title">CMJ Jump Height Exposure & Compliance Grid</div>', unsafe_allow_html=True)

            for i in range(0, len(roster_players), 2):
                col1, col2 = st.columns(2)
                cols = [col1, col2]

                for j in range(2):
                    if i + j < len(roster_players):
                        player_name = roster_players[i + j]
                        p_row = roster_raw[roster_raw['Name'] == player_name]
                        p_pos = p_row['Position'].values[0] if not p_row.empty else "Guard / Forward | #00"
                        p_img = p_row['Picture'].values[0] if not p_row.empty else "https://via.placeholder.com/60"

                        p_cmj = cmj_raw[cmj_raw['Name'] == player_name].sort_values('Date')

                        if not p_cmj.empty and "Jump Height (Imp-Mom) [cm]" in p_cmj.columns:
                            all_time_max_cmj = p_cmj['Jump Height (Imp-Mom) [cm]'].max()
                            max_row_cmj = p_cmj[p_cmj['Jump Height (Imp-Mom) [cm]'] == all_time_max_cmj].iloc[-1]
                            max_date_cmj = pd.to_datetime(max_row_cmj['Date']).strftime('%Y-%m-%d')

                            recent_row_cmj = p_cmj.iloc[-1]
                            recent_cmj = recent_row_cmj['Jump Height (Imp-Mom) [cm]']
                            recent_date_cmj = pd.to_datetime(recent_row_cmj['Date']).strftime('%Y-%m-%d')

                            pct_max_cmj = f"{(recent_cmj / all_time_max_cmj * 100):.1f}%" if all_time_max_cmj > 0 else "-- %"
                            days_since_cmj = (pd.to_datetime('today') - pd.to_datetime(max_date_cmj)).days

                            badge_bg_cmj = "#BBF7D0" if days_since_cmj <= 7 else "#FFD6D6"
                            badge_fg_cmj = "#166534" if days_since_cmj <= 7 else "#991B1B"

                            with cols[j]:
                                st.markdown(f"""
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
                                """, unsafe_allow_html=True)


    # =========================================================================
    # TAB 4: WEEKLY DATA (Team Bars + Individual Overlay Lines)
    # =========================================================================
    elif main_tab == "Weekly Data":
        st.markdown('<div class="vball-section-title">1. Team Weekly Accumulation Overview</div>', unsafe_allow_html=True)

        weekly_agg = weekly_raw.groupby('Week').agg({
            'Distance (mi)': 'sum',
            'Distance (speed | High Speed) (mi)': 'sum',
            'Accumulated Acceleration Load': 'sum',
            'Decels Load': 'sum'
        }).reset_index()

        weeks = weekly_agg['Week'].tolist()

        w1, w2 = st.columns(2)
        with w1:
            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_td = create_clean_bar_chart(weeks, weekly_agg['Distance (mi)'], "Total Distance (mi)", "#38BDF8")
            st.plotly_chart(fig_td, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_aal = create_clean_bar_chart(weeks, weekly_agg['Accumulated Acceleration Load'], "Accumulated Acceleration Load (AAL)", "#FF8200")
            st.plotly_chart(fig_aal, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with w2:
            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_hsd = create_clean_bar_chart(weeks, weekly_agg['Distance (speed | High Speed) (mi)'], "High Speed Distance (mi)", "#38BDF8")
            st.plotly_chart(fig_hsd, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_dl = create_clean_bar_chart(weeks, weekly_agg['Decels Load'], "Deceleration Load", "#FF8200")
            st.plotly_chart(fig_dl, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="vball-section-title">2. Individual Player Breakdown vs. Team Average</div>', unsafe_allow_html=True)
        selected_player_w = st.selectbox("Select Athlete:", roster_players)

        p_weekly = weekly_raw[weekly_raw['Player'] == selected_player_w]
        t_weekly_avg = weekly_raw.groupby('Week').agg({
            'Distance (mi)': 'mean',
            'Distance (speed | High Speed) (mi)': 'mean',
            'Accumulated Acceleration Load': 'mean',
            'Decels Load': 'mean'
        }).reset_index()

        all_weeks = t_weekly_avg['Week'].tolist()

        def create_team_bar_athlete_line_chart(weeks, team_avg_vals, athlete_vals, title_text, bar_color="#38BDF8"):
            fig = go.Figure()
            fig.add_trace(go.Bar(x=weeks, y=team_avg_vals, name="Team Average", marker_color=bar_color))
            fig.add_trace(go.Scatter(
                x=weeks, y=athlete_vals, name=f"{selected_player_w} Output", mode="markers",
                marker=dict(symbol="line-ew", size=24, line=dict(width=3, color="black"))
            ))
            fig.update_layout(
                title=title_text, title_font=dict(size=14, color="#0F172A"),
                height=250, margin=dict(l=0, r=0, t=35, b=0),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            return fig

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_td = create_team_bar_athlete_line_chart(all_weeks, t_weekly_avg['Distance (mi)'], p_weekly['Distance (mi)'], f"Total Distance (mi) — {selected_player_w}", "#FF8200")
            st.plotly_chart(fig_ind_td, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_aal = create_team_bar_athlete_line_chart(all_weeks, t_weekly_avg['Accumulated Acceleration Load'], p_weekly['Accumulated Acceleration Load'], f"AAL — {selected_player_w}", "#38BDF8")
            st.plotly_chart(fig_ind_aal, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_p2:
            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_hsd = create_team_bar_athlete_line_chart(all_weeks, t_weekly_avg['Distance (speed | High Speed) (mi)'], p_weekly['Distance (speed | High Speed) (mi)'], f"High Speed Distance (mi) — {selected_player_w}", "#FF8200")
            st.plotly_chart(fig_ind_hsd, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_dl = create_team_bar_athlete_line_chart(all_weeks, t_weekly_avg['Decels Load'], p_weekly['Decels Load'], f"Deceleration Load — {selected_player_w}", "#38BDF8")
            st.plotly_chart(fig_ind_dl, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


    # =========================================================================
    # TAB 5: TESTING
    # =========================================================================
    elif main_tab == "Testing":
        st.markdown('<div class="vball-section-title">CMJ History</div>', unsafe_allow_html=True)

        c_filter, _ = st.columns([1, 2])
        with c_filter:
            selected_player_t = st.selectbox("Select Athlete:", roster_players)

        p_cmj = cmj_raw[cmj_raw['Name'] == selected_player_t].sort_values('Date')

        display_cols = [c for c in p_cmj.columns if c not in ['Name']]
        st.markdown(f"### Jump History for {selected_player_t}")
        st.markdown(render_vball_table(p_cmj[display_cols]), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
        fig_jump_trend = go.Figure()
        fig_jump_trend.add_trace(go.Scatter(
            x=p_cmj["Date"], y=p_cmj["Jump Height (Imp-Mom) [cm]"],
            name="Jump Height (Imp-Mom) [cm]", mode="lines+markers",
            line=dict(color="#FF8200", width=3), marker=dict(size=8)
        ))
        fig_jump_trend.add_trace(go.Scatter(
            x=p_cmj["Date"], y=p_cmj["RSI-modified (Imp-Mom) [m/s]"],
            name="RSI-modified (Imp-Mom) [m/s]", mode="lines+markers",
            yaxis="y2", line=dict(color="#38BDF8", width=3), marker=dict(size=8)
        ))

        fig_jump_trend.update_layout(
            title=f"Jump Height & RSI-modified Progression Over Time ({selected_player_t})",
            title_font=dict(size=14, color="#0F172A"),
            height=320, margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="Jump Height [cm]"),
            yaxis2=dict(title="RSI-modified [m/s]", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_jump_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
