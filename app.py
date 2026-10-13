"""
Football Player Performance Analytics Dashboard
================================================
All player data is SYNTHETIC and entirely fictitious.
It does not represent real players, clubs, or competitions.
"""

import datetime
import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Constants ────────────────────────────────────────────────────────────────
DATA_FILE = pathlib.Path(__file__).parent / "football_players.csv"
ACCENT = "#00ff87"
CARD_BG = "#1a1f2e"
PAGE_BG = "#0e1117"
MUTED = "#8b949e"
PLOTLY_TEMPLATE = "plotly_dark"
POSITION_ORDER = ["GK", "DEF", "MID", "FWD"]
POSITION_COLORS = {"GK": "#94a3b8", "DEF": "#60a5fa", "MID": "#fbbf24", "FWD": "#00ff87"}
SYNTHETIC_NOTE = (
    "⚠️ **Synthetic Data** — All statistics are computer-generated and "
    "do **not** represent real players, clubs, or competitions."
)

REQUIRED_COLUMNS = {
    "player_id", "player_name", "team", "position", "season",
    "age", "matches_played", "minutes_played", "goals", "assists",
    "shots", "shots_on_target", "passes", "key_passes",
    "tackles", "interceptions", "yellow_cards", "red_cards", "rating",
}

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    /* Base background */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {PAGE_BG};
        color: #e6edf3;
    }}
    [data-testid="stSidebar"] {{
        background-color: #161b22;
    }}
    /* KPI card */
    .kpi-card {{
        background: {CARD_BG};
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {ACCENT};
        line-height: 1.1;
    }}
    .kpi-label {{
        font-size: 0.78rem;
        color: {MUTED};
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    /* Section header */
    .section-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {ACCENT};
        border-left: 3px solid {ACCENT};
        padding-left: 10px;
        margin: 24px 0 12px 0;
    }}
    /* Stat comparison row */
    .stat-row {{
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #30363d;
        font-size: 0.88rem;
    }}
    .stat-row:last-child {{ border-bottom: none; }}
    .stat-label {{ color: {MUTED}; }}
    .stat-val   {{ font-weight: 600; color: #e6edf3; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading player data…")
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        st.error(
            f"Dataset not found at `{DATA_FILE}`. "
            "Run `python generate_data.py` first, then refresh."
        )
        st.stop()

    df = pd.read_csv(DATA_FILE)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        st.error(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
        st.stop()

    # Drop fully-empty rows; fill remaining numeric nulls with 0
    df.dropna(how="all", inplace=True)
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    df["player_name"] = df["player_name"].fillna("Unknown")
    df["team"] = df["team"].fillna("Unknown")
    df["position"] = df["position"].fillna("Unknown")
    df["season"] = df["season"].fillna("Unknown")

    # Derived metrics
    df["goals_per_90"] = (df["goals"] / (df["minutes_played"] / 90)).replace([np.inf, -np.inf], 0).round(2)
    df["assists_per_90"] = (df["assists"] / (df["minutes_played"] / 90)).replace([np.inf, -np.inf], 0).round(2)
    df["shot_accuracy_pct"] = np.where(
        df["shots"] > 0, (df["shots_on_target"] / df["shots"] * 100).round(1), 0.0
    )
    df["goal_conversion_pct"] = np.where(
        df["shots"] > 0, (df["goals"] / df["shots"] * 100).round(1), 0.0
    )
    df["goal_contributions"] = df["goals"] + df["assists"]

    return df


# ── Sidebar + filtering ───────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown(
            f"<h2 style='color:{ACCENT};margin-bottom:0'>⚽ Football</h2>"
            "<p style='color:#8b949e;margin-top:2px;font-size:0.82rem'>Analytics Dashboard</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        page = st.radio(
            "Navigate",
            ["Overview", "Player Analysis", "Team Analysis", "Position Analysis"],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**Filters**")

        all_seasons = sorted(df["season"].unique().tolist())
        sel_seasons = st.multiselect("Season", all_seasons, default=all_seasons, key="f_season")
        if not sel_seasons:
            sel_seasons = all_seasons

        df1 = df[df["season"].isin(sel_seasons)]

        all_teams = sorted(df1["team"].unique().tolist())
        sel_teams = st.multiselect("Team", all_teams, default=all_teams, key="f_team")
        if not sel_teams:
            sel_teams = all_teams

        df2 = df1[df1["team"].isin(sel_teams)]

        sel_positions = st.multiselect(
            "Position", POSITION_ORDER,
            default=POSITION_ORDER, key="f_position"
        )
        if not sel_positions:
            sel_positions = POSITION_ORDER

        df3 = df2[df2["position"].isin(sel_positions)]

        player_opts = ["All"] + sorted(df3["player_name"].unique().tolist())
        sel_player = st.selectbox("Player", player_opts, key="f_player")

        if sel_player != "All":
            df3 = df3[df3["player_name"] == sel_player]

        st.divider()
        st.caption(f"{len(df3):,} player records shown")

    return page, df3


# ── Helper: KPI card HTML ─────────────────────────────────────────────────────
def kpi_card(label: str, value: str) -> str:
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f"</div>"
    )


def section(title: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# ── Page 1: Overview ──────────────────────────────────────────────────────────
def render_overview(df: pd.DataFrame):
    st.markdown("## 📊 Overview")
    st.info(SYNTHETIC_NOTE)

    if df.empty:
        st.warning("No players match the current filters. Adjust the sidebar filters to see data.")
        return

    # KPI cards
    total_players = df["player_id"].nunique()
    total_goals = int(df["goals"].sum())
    total_assists = int(df["assists"].sum())
    total_minutes = int(df["minutes_played"].sum())
    avg_rating = round(float(df["rating"].mean()), 2)

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val in zip(
        [c1, c2, c3, c4, c5],
        ["Total Players", "Total Goals", "Total Assists", "Minutes Played", "Avg Rating"],
        [f"{total_players:,}", f"{total_goals:,}", f"{total_assists:,}",
         f"{total_minutes:,}", f"{avg_rating}"],
    ):
        col.markdown(kpi_card(label, val), unsafe_allow_html=True)

    st.markdown("")

    col_l, col_r = st.columns(2)

    with col_l:
        section("Top 10 Goal Scorers")
        top_scorers = (
            df.groupby("player_name", as_index=False)
            .agg(goals=("goals", "sum"), team=("team", "first"))
            .nlargest(10, "goals")
            .sort_values("goals")
        )
        fig = px.bar(
            top_scorers, x="goals", y="player_name", orientation="h",
            hover_data={"team": True},
            labels={"goals": "Goals", "player_name": "Player"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[ACCENT],
        )
        fig.update_layout(yaxis_title=None, margin=dict(l=0, r=20, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        section("Player Rating Distribution")
        fig2 = px.histogram(
            df, x="rating", nbins=20,
            labels={"rating": "Rating", "count": "Players"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[ACCENT],
        )
        fig2.update_layout(margin=dict(l=0, r=20, t=10, b=10), bargap=0.05)
        st.plotly_chart(fig2, use_container_width=True)

    section("Top 10 Goal Contributors (Goals + Assists)")
    top_contrib = (
        df.groupby("player_name", as_index=False)
        .agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            team=("team", "first"),
            position=("position", "first"),
        )
        .nlargest(10, "goals")
    )
    top_contrib["goal_contributions"] = top_contrib["goals"] + top_contrib["assists"]
    top_contrib = top_contrib.sort_values("goal_contributions", ascending=False)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name="Goals", x=top_contrib["player_name"], y=top_contrib["goals"],
        marker_color=ACCENT,
    ))
    fig3.add_trace(go.Bar(
        name="Assists", x=top_contrib["player_name"], y=top_contrib["assists"],
        marker_color="#7c5cd8",
    ))
    fig3.update_layout(
        barmode="stack", template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title=None, yaxis_title="Contributions",
    )
    st.plotly_chart(fig3, use_container_width=True)

    render_stats_table(df)


# ── Page 2: Player Analysis ───────────────────────────────────────────────────
def render_player_analysis(df: pd.DataFrame):
    st.markdown("## 👤 Player Analysis")
    st.info(SYNTHETIC_NOTE)

    if df.empty:
        st.warning("No players match the current filters.")
        return

    players = sorted(df["player_name"].unique().tolist())

    # ── Player comparison ──────────────────────────────────────────────────
    section("Player Comparison")
    col_a, col_b = st.columns(2)
    with col_a:
        player_a = st.selectbox("Player A", players, index=0, key="pa_a")
    with col_b:
        default_b = players[1] if len(players) > 1 else players[0]
        player_b = st.selectbox("Player B", players, index=players.index(default_b), key="pa_b")

    def player_stats(name: str) -> pd.Series:
        rows = df[df["player_name"] == name]
        return rows.iloc[0] if len(rows) == 1 else rows.mean(numeric_only=True).round(2)

    def player_meta(name: str) -> dict:
        row = df[df["player_name"] == name].iloc[0]
        return {"team": row["team"], "position": row["position"], "season": row["season"]}

    COMPARE_STATS = [
        ("Age", "age"), ("Matches", "matches_played"), ("Minutes", "minutes_played"),
        ("Goals", "goals"), ("Assists", "assists"), ("Shots", "shots"),
        ("Shot Accuracy %", "shot_accuracy_pct"), ("Passes", "passes"),
        ("Key Passes", "key_passes"), ("Tackles", "tackles"),
        ("Interceptions", "interceptions"), ("Rating", "rating"),
    ]

    sa, sb = player_stats(player_a), player_stats(player_b)
    ma, mb = player_meta(player_a), player_meta(player_b)

    c1, c2 = st.columns(2)
    for col, name, stats, meta in [(c1, player_a, sa, ma), (c2, player_b, sb, mb)]:
        rows_html = "".join(
            f'<div class="stat-row"><span class="stat-label">{lbl}</span>'
            f'<span class="stat-val">{stats.get(key, "—")}</span></div>'
            for lbl, key in COMPARE_STATS
        )
        col.markdown(
            f'<div class="kpi-card" style="text-align:left">'
            f'<div style="font-size:1.05rem;font-weight:700;color:{ACCENT};margin-bottom:8px">{name}</div>'
            f'<div style="font-size:0.78rem;color:{MUTED};margin-bottom:12px">'
            f'{meta["team"]} · {meta["position"]} · {meta["season"]}</div>'
            f"{rows_html}</div>",
            unsafe_allow_html=True,
        )

    # Visual stat bar comparison
    compare_keys = ["goals", "assists", "shots", "passes", "tackles", "rating"]
    compare_labels = ["Goals", "Assists", "Shots", "Passes", "Tackles", "Rating"]
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        name=player_a,
        x=compare_labels,
        y=[float(sa.get(k, 0)) for k in compare_keys],
        marker_color=ACCENT,
    ))
    fig_cmp.add_trace(go.Bar(
        name=player_b,
        x=compare_labels,
        y=[float(sb.get(k, 0)) for k in compare_keys],
        marker_color="#7c5cd8",
    ))
    fig_cmp.update_layout(
        barmode="group", template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title="Value",
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.divider()

    col_l, col_r = st.columns(2)

    # ── Goals vs Assists scatter ───────────────────────────────────────────
    with col_l:
        section("Goals vs Assists")
        if df.shape[0] < 2:
            st.info("Not enough players for scatter plot.")
        else:
            fig_ga = px.scatter(
                df, x="assists", y="goals",
                color="position",
                color_discrete_map=POSITION_COLORS,
                category_orders={"position": POSITION_ORDER},
                hover_data={"player_name": True, "team": True, "season": True,
                            "rating": True, "position": False},
                labels={"goals": "Goals", "assists": "Assists", "player_name": "Player"},
                template=PLOTLY_TEMPLATE,
                size_max=12,
            )
            fig_ga.update_traces(marker=dict(size=8, opacity=0.85))
            fig_ga.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title="Position")
            st.plotly_chart(fig_ga, use_container_width=True)

    # ── Shots vs Goals bubble ─────────────────────────────────────────────
    with col_r:
        section("Shots vs Goals (size = minutes played)")
        plot_df = df[df["shots"] > 0].copy()
        if plot_df.empty:
            st.info("No shot data available for current filter.")
        else:
            fig_sg = px.scatter(
                plot_df, x="shots", y="goals",
                size="minutes_played",
                color="shot_accuracy_pct",
                color_continuous_scale="Tealgrn",
                hover_data={"player_name": True, "team": True, "shot_accuracy_pct": True,
                            "goal_conversion_pct": True, "minutes_played": False},
                labels={
                    "shots": "Shots", "goals": "Goals",
                    "shot_accuracy_pct": "Shot Acc. %",
                    "player_name": "Player",
                },
                template=PLOTLY_TEMPLATE,
            )
            fig_sg.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_sg, use_container_width=True)

    render_stats_table(df)


# ── Page 3: Team Analysis ─────────────────────────────────────────────────────
def render_team_analysis(df: pd.DataFrame):
    st.markdown("## 🏟️ Team Analysis")
    st.info(SYNTHETIC_NOTE)

    if df.empty:
        st.warning("No players match the current filters.")
        return

    team_agg = (
        df.groupby("team", as_index=False)
        .agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            players=("player_id", "nunique"),
            avg_rating=("rating", "mean"),
            total_minutes=("minutes_played", "sum"),
        )
        .sort_values("goals", ascending=False)
    )
    team_agg["avg_rating"] = team_agg["avg_rating"].round(2)

    col_l, col_r = st.columns(2)

    with col_l:
        section("Goals & Assists by Team")
        fig_ta = go.Figure()
        fig_ta.add_trace(go.Bar(
            name="Goals", x=team_agg["team"], y=team_agg["goals"],
            marker_color=ACCENT,
        ))
        fig_ta.add_trace(go.Bar(
            name="Assists", x=team_agg["team"], y=team_agg["assists"],
            marker_color="#7c5cd8",
        ))
        fig_ta.update_layout(
            barmode="group", template=PLOTLY_TEMPLATE,
            legend=dict(orientation="h", y=1.1),
            xaxis_tickangle=-35,
            margin=dict(l=0, r=0, t=30, b=60),
            yaxis_title="Count",
        )
        st.plotly_chart(fig_ta, use_container_width=True)

    with col_r:
        section("Squad Size by Team")
        fig_pc = px.bar(
            team_agg.sort_values("players", ascending=False),
            x="team", y="players",
            labels={"team": "Team", "players": "Players"},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#60a5fa"],
        )
        fig_pc.update_layout(xaxis_tickangle=-35, margin=dict(l=0, r=0, t=10, b=60), yaxis_title="Players")
        st.plotly_chart(fig_pc, use_container_width=True)

    section("Average Rating by Team")
    fig_ar = px.bar(
        team_agg.sort_values("avg_rating", ascending=False),
        x="team", y="avg_rating",
        labels={"team": "Team", "avg_rating": "Avg Rating"},
        template=PLOTLY_TEMPLATE,
        color="avg_rating",
        color_continuous_scale="Tealgrn",
        range_color=[5.0, 9.5],
    )
    fig_ar.update_layout(xaxis_tickangle=-35, margin=dict(l=0, r=0, t=10, b=60), yaxis_title="Avg Rating")
    st.plotly_chart(fig_ar, use_container_width=True)

    section("Team Summary Table")
    display_team = team_agg.rename(columns={
        "team": "Team", "goals": "Goals", "assists": "Assists",
        "players": "Players", "avg_rating": "Avg Rating", "total_minutes": "Total Minutes",
    })
    st.dataframe(display_team, use_container_width=True, hide_index=True)

    render_stats_table(df)


# ── Page 4: Position Analysis ─────────────────────────────────────────────────
def render_position_analysis(df: pd.DataFrame):
    st.markdown("## 🎯 Position Analysis")
    st.info(SYNTHETIC_NOTE)

    if df.empty:
        st.warning("No players match the current filters.")
        return

    present_positions = [p for p in POSITION_ORDER if p in df["position"].values]

    col_l, col_r = st.columns(2)

    with col_l:
        section("Rating by Position")
        fig_rb = px.box(
            df[df["position"].isin(present_positions)],
            x="position", y="rating",
            color="position",
            color_discrete_map=POSITION_COLORS,
            category_orders={"position": present_positions},
            labels={"rating": "Rating", "position": "Position"},
            template=PLOTLY_TEMPLATE,
        )
        fig_rb.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_rb, use_container_width=True)

    with col_r:
        section("Goals by Position")
        fig_gb = px.box(
            df[df["position"].isin(present_positions)],
            x="position", y="goals",
            color="position",
            color_discrete_map=POSITION_COLORS,
            category_orders={"position": present_positions},
            labels={"goals": "Goals", "position": "Position"},
            template=PLOTLY_TEMPLATE,
        )
        fig_gb.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_gb, use_container_width=True)

    # ── Radar chart ────────────────────────────────────────────────────────
    section("Positional Profile — Radar Chart")
    radar_metrics = ["goals", "assists", "passes", "tackles", "interceptions", "rating"]
    radar_labels  = ["Goals", "Assists", "Passes", "Tackles", "Interceptions", "Rating"]

    pos_means = df[df["position"].isin(present_positions)].groupby("position")[radar_metrics].mean()

    # Normalise each metric to 0–1 so axes are comparable
    normed = (pos_means - pos_means.min()) / (pos_means.max() - pos_means.min() + 1e-9)

    fig_radar = go.Figure()
    for pos in present_positions:
        if pos not in normed.index:
            continue
        r_vals = normed.loc[pos].tolist()
        r_vals += [r_vals[0]]  # close the loop
        theta = radar_labels + [radar_labels[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals, theta=theta,
            fill="toself",
            name=pos,
            line_color=POSITION_COLORS.get(pos, "#ffffff"),
            fillcolor=POSITION_COLORS.get(pos, "#ffffff"),
            opacity=0.35,
        ))
    fig_radar.update_layout(
        template=PLOTLY_TEMPLATE,
        polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9))),
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=40, t=20, b=60),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Stacked goal contributions by position ────────────────────────────
    section("Goal Contributions by Position (Goals vs Assists)")
    pos_contrib = (
        df[df["position"].isin(present_positions)]
        .groupby("position", as_index=False)
        .agg(goals=("goals", "sum"), assists=("assists", "sum"))
    )
    pos_contrib = pos_contrib.set_index("position").reindex(present_positions).reset_index()

    fig_stk = go.Figure()
    fig_stk.add_trace(go.Bar(
        name="Goals", x=pos_contrib["position"], y=pos_contrib["goals"],
        marker_color=ACCENT,
    ))
    fig_stk.add_trace(go.Bar(
        name="Assists", x=pos_contrib["position"], y=pos_contrib["assists"],
        marker_color="#7c5cd8",
    ))
    fig_stk.update_layout(
        barmode="stack", template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Position", yaxis_title="Total",
    )
    st.plotly_chart(fig_stk, use_container_width=True)

    render_stats_table(df)


# ── Stats Table + CSV Download (shared across all pages) ─────────────────────
def render_stats_table(df: pd.DataFrame):
    st.divider()
    section("Player Statistics Table")

    search = st.text_input(
        "🔍 Search player name", value="", placeholder="Type to filter…", key=f"search_{id(df)}"
    )
    display_df = df.copy()
    if search.strip():
        mask = display_df["player_name"].str.contains(search.strip(), case=False, na=False)
        display_df = display_df[mask]

    DISPLAY_COLS = {
        "player_name": "Player", "team": "Team", "position": "Pos",
        "season": "Season", "age": "Age", "matches_played": "MP",
        "minutes_played": "Mins", "goals": "G", "assists": "A",
        "shots": "Shots", "shots_on_target": "SoT",
        "shot_accuracy_pct": "Shot Acc%", "goal_conversion_pct": "Conv%",
        "passes": "Passes", "key_passes": "KP", "tackles": "Tkl",
        "interceptions": "Int", "yellow_cards": "YC", "red_cards": "RC",
        "rating": "Rating",
    }

    table_df = display_df[[c for c in DISPLAY_COLS if c in display_df.columns]].rename(columns=DISPLAY_COLS)

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    today = datetime.date.today().isoformat()
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name=f"football_players_filtered_{today}.csv",
        mime="text/csv",
        key=f"dl_{id(df)}",
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df_all = load_data()
    page, df_filtered = render_sidebar(df_all)

    if page == "Overview":
        render_overview(df_filtered)
    elif page == "Player Analysis":
        render_player_analysis(df_filtered)
    elif page == "Team Analysis":
        render_team_analysis(df_filtered)
    elif page == "Position Analysis":
        render_position_analysis(df_filtered)


if __name__ == "__main__":
    main()
