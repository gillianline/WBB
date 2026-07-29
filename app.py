import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & BASE STYLING
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
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 3px solid #FF8200;
            object-fit: cover;
            background-color: #F1F5F9;
        }
        .athlete-info h2 { margin: 0; font-size: 1.5rem; font-weight: 700; color: #0F172A; }
        .athlete-info p { margin: 2px 0 0 0; color: #64748B; font-size: 0.9rem; }

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

        .roster-card {
            background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px;
            padding: 18px; margin-bottom: 25px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }

        .compliance-metric-card {
            background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;
            padding: 12px 14px; text-align: center;
        }
        .compliance-metric-label { font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px; }
        .compliance-metric-value { font-size: 1.25rem; font-weight: 800; color: #0F172A; }
        .compliance-metric-sub { font-size: 0.75rem; color: #94A3B8; margin-top: 2px; }
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
    try:
        vol_df = pd.read_csv(st.secrets["sheets"]["volume_url"])
        int_df = pd.read_csv(st.secrets["sheets"]["intensity_url"])
        comp_df = pd.read_csv(st.secrets["sheets"]["compliance_url"])
        weekly_df = pd.read_csv(st.secrets["sheets"]["weekly_url"])
        cmj_df = pd.read_csv(st.secrets["sheets"]["cmj_url"])
        roster_df = pd.read_csv(st.secrets["sheets"]["roster_url"])

        # Convert date columns to datetime
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
# 4. HELPER FUNCTIONS & CALCULATIONS
# -----------------------------------------------------------------------------
def get_vball_color(score):
    if score is None or pd.isna(score): return "#E2E8F0", "#475569"
    if score < 45: return "#FFD6D6", "#991B1B"
    elif score < 65: return "#FEF08A", "#854D0E"
    elif score < 85: return "#BAE6FD", "#0369A1"
    else: return "#BBF7D0", "#166534"

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
        height=240,
        margin=dict(l=0, r=0, t=35, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title=None, yaxis_title=None
    )
    return fig

def create_weekly_benchmark_chart(weeks, athlete_vals, team_avg_vals, title_text, bar_color="#38BDF8"):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=weeks, y=athlete_vals, name="Athlete Output", marker_color=bar_color))
    fig.add_trace(go.Scatter(
        x=weeks, y=team_avg_vals, name="Team Average", mode="markers",
        marker=dict(symbol="line-ew", size=24, line=dict(width=3, color="black"))
    ))
    fig.update_layout(
        title=title_text, title_font=dict(size=14, color="#0F172A"),
        height=250, margin=dict(l=0, r=0, t=35, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def compute_practice_tables(player_name, session_date):
    """Calculates Volume and Intensity grades and scores from live Google Sheets data."""
    v_player = vol_raw[(vol_raw['Player'] == player_name) & (vol_raw['Date'] == session_date)]
    i_player = int_raw[(int_raw['Player'] == player_name) & (int_raw['Date'] == session_date)]
    
    # Baselines (First 2 weeks highest values)
    v_base = vol_raw[vol_raw['Player'] == player_name].sort_values('Date').head(14)
    i_base = int_raw[int_raw['Player'] == player_name].sort_values('Date').head(14)

    vol_metrics = ["Distance (mi)", "Accumulated Acceleration Load", "Decels Load", "FCTs", "Physio Load", "Mechanical Load", "Jump Load (J)"]
    int_metrics = ["Physio Intensity", "Acceleration Load (load | High AAL)", "Distance (speed | High Speed) (mi)", "Speed (max.) (mph)", "Sprints", "Exertions", "High Metabolic Power Distance (m)"]

    vol_rows, int_rows = [], []

    # Volume Calculations
    for m in vol_metrics:
        curr = v_player[m].values[0] if not v_player.empty else 0.0
        mx = v_base[m].max() if not v_base.empty and m in v_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        vol_rows.append({"Metric": m, "Current": curr, "Max": mx, "Grade": grade})

    # Intensity Calculations
    for m in int_metrics:
        curr = i_player[m].values[0] if not i_player.empty else 0.0
        mx = i_base[m].max() if not i_base.empty and m in i_base else curr
        grade = round((curr / mx * 100), 0) if mx > 0 else 0
        int_rows.append({"Metric": m, "Current": curr, "Max": mx, "Grade": grade})

    vol_df_out = pd.DataFrame(vol_rows)
    int_df_out = pd.DataFrame(int_rows)

    vol_score = int(vol_df_out['Grade'].mean()) if not vol_df_out.empty else 0
    int_score = int(int_df_out['Grade'].mean()) if not int_df_out.empty else 0

    return vol_df_out, int_df_out, vol_score, int_score


# -----------------------------------------------------------------------------
# 5. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.markdown("### LADY VOLS BASKETBALL")
st.sidebar.caption("Performance Analytics Engine")

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
    # TAB 1: INDIVIDUAL PROFILE
    # =========================================================================
    if main_tab == "Individual Profile":
        c_sel, _ = st.columns([1, 2])
        with c_sel:
            selected_player = st.selectbox("Select Athlete Profile:", roster_players)

        # Athlete Roster Metadata
        p_row = roster_raw[roster_raw['Name'] == selected_player]
        p_pos = p_row['Position'].values[0] if not p_row.empty else "Athlete"
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
            v_hist = vol_raw[vol_raw['Player'] == selected_player].sort_values('Date')
            if not v_hist.empty:
                fig1 = px.line(v_hist, x="Date", y="Distance (mi)", markers=True, color_discrete_sequence=["#FF8200"])
                fig1.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=230, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
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
            vol_df, int_df, vol_score, int_score = compute_practice_tables(selected_player, latest_date)
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
    # TAB 2: PRACTICE SCORE
    # =========================================================================
    elif main_tab == "Practice Score":
        c_d, _ = st.columns([1, 3])
        with c_d:
            available_dates = vol_raw['Date'].sort_values(ascending=False).dt.date.unique()
            session_date = st.selectbox("Select Session Date:", available_dates)

        st.markdown("<br>", unsafe_allow_html=True)

        for player_name in roster_players:
            p_row = roster_raw[roster_raw['Name'] == player_name]
            p_pos = p_row['Position'].values[0] if not p_row.empty else "Athlete"
            p_img = p_row['Picture'].values[0] if not p_row.empty else "https://via.placeholder.com/70"

            vol_df, int_df, vol_score, int_score = compute_practice_tables(player_name, pd.to_datetime(session_date))

            st.markdown(f"""
                <div class="roster-card">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                        <img src="{p_img}" class="athlete-avatar" style="width:60px; height:60px;">
                        <div>
                            <h3 style="margin:0; font-size:1.3rem; color:#0F172A;">{player_name}</h3>
                            <span style="color:#64748B; font-size:0.85rem;">{p_pos}</span>
                        </div>
                    </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="vball-section-title">Volume Metrics</div>', unsafe_allow_html=True)
                st.markdown(render_vball_table(vol_df), unsafe_allow_html=True)
                v_bg, v_fg = get_vball_color(vol_score)
                st.markdown(f"""
                    <div class="score-box-container">
                        <div style="font-weight: 700; color: #64748B; font-size: 0.85rem;">VOLUME SCORE</div>
                        <div class="score-box-value" style="background-color: {v_bg}; color: {v_fg};">{vol_score}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="vball-section-title">Intensity Metrics</div>', unsafe_allow_html=True)
                st.markdown(render_vball_table(int_df), unsafe_allow_html=True)
                i_bg, i_fg = get_vball_color(int_score)
                st.markdown(f"""
                    <div class="score-box-container">
                        <div style="font-weight: 700; color: #64748B; font-size: 0.85rem;">INTENSITY SCORE</div>
                        <div class="score-box-value" style="background-color: {i_bg}; color: {i_fg};">{int_score}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)


    # =========================================================================
    # TAB 3: COMPLIANCE
    # =========================================================================
    elif main_tab == "Compliance":
        st.markdown('<div class="vball-section-title">Max Speed & Exposure Compliance Roster</div>', unsafe_allow_html=True)

        for player_name in roster_players:
            p_row = roster_raw[roster_raw['Name'] == player_name]
            p_pos = p_row['Position'].values[0] if not p_row.empty else "Athlete"
            p_img = p_row['Picture'].values[0] if not p_row.empty else "https://via.placeholder.com/70"

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

                st.markdown(f"""
                    <div class="roster-card">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <img src="{p_img}" class="athlete-avatar" style="width:60px; height:60px;">
                                <div>
                                    <h3 style="margin:0; font-size:1.3rem; color:#0F172A;">{player_name}</h3>
                                    <span style="color:#64748B; font-size:0.85rem;">{p_pos}</span>
                                </div>
                            </div>
                            <div style="background-color:{badge_bg}; color:{badge_fg}; font-weight:700; padding:6px 14px; border-radius:20px; font-size:0.85rem;">
                                {days_since} Days Since Max Speed Ever
                            </div>
                        </div>
                """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""
                        <div class="compliance-metric-card">
                            <div class="compliance-metric-label">Recent Speed</div>
                            <div class="compliance-metric-value">{recent_speed:.1f} mph</div>
                            <div class="compliance-metric-sub">{recent_date}</div>
                        </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                        <div class="compliance-metric-card">
                            <div class="compliance-metric-label">All-Time Max Speed</div>
                            <div class="compliance-metric-value">{all_time_max:.1f} mph</div>
                            <div class="compliance-metric-sub">{max_date}</div>
                        </div>
                    """, unsafe_allow_html=True)

                with c3:
                    st.markdown(f"""
                        <div class="compliance-metric-card">
                            <div class="compliance-metric-label">% of All-Time Max</div>
                            <div class="compliance-metric-value" style="color:#FF8200;">{pct_max}</div>
                            <div class="compliance-metric-sub">Recent vs. Peak Output</div>
                        </div>
                    """, unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                        <div class="compliance-metric-card">
                            <div class="compliance-metric-label">Recency Status</div>
                            <div class="compliance-metric-value">{days_since} Days</div>
                            <div class="compliance-metric-sub">Elapsed Threshold</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)


    # =========================================================================
    # TAB 4: WEEKLY DATA
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

        st.markdown('<div class="vball-section-title">2. Individual Player Weekly Breakdown vs. Team Average</div>', unsafe_allow_html=True)
        selected_player_w = st.selectbox("Select Athlete:", roster_players)

        p_weekly = weekly_raw[weekly_raw['Player'] == selected_player_w]
        t_weekly_avg = weekly_raw.groupby('Week').agg({
            'Distance (mi)': 'mean',
            'Distance (speed | High Speed) (mi)': 'mean',
            'Accumulated Acceleration Load': 'mean',
            'Decels Load': 'mean'
        }).reset_index()

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_td = create_weekly_benchmark_chart(weeks, p_weekly['Distance (mi)'], t_weekly_avg['Distance (mi)'], f"Total Distance (mi) — {selected_player_w}", "#FF8200")
            st.plotly_chart(fig_ind_td, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_aal = create_weekly_benchmark_chart(weeks, p_weekly['Accumulated Acceleration Load'], t_weekly_avg['Accumulated Acceleration Load'], f"AAL — {selected_player_w}", "#38BDF8")
            st.plotly_chart(fig_ind_aal, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_p2:
            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_hsd = create_weekly_benchmark_chart(weeks, p_weekly['Distance (speed | High Speed) (mi)'], t_weekly_avg['Distance (speed | High Speed) (mi)'], f"High Speed Distance (mi) — {selected_player_w}", "#FF8200")
            st.plotly_chart(fig_ind_hsd, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="light-card-box">', unsafe_allow_html=True)
            fig_ind_dl = create_weekly_benchmark_chart(weeks, p_weekly['Decels Load'], t_weekly_avg['Decels Load'], f"Deceleration Load — {selected_player_w}", "#38BDF8")
            st.plotly_chart(fig_ind_dl, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


    # =========================================================================
    # TAB 5: TESTING
    # =========================================================================
    elif main_tab == "Testing":
        st.markdown('<div class="vball-section-title">CMJ</div>', unsafe_allow_html=True)

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
