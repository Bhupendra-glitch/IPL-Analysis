import pandas as pd
import streamlit as st
from utils import load_data

try:
    import plotly.express as px
except ImportError:
    px = None

st.title("📈 EDA Dashboard")
st.caption("Explore how IPL matches, scoring, tosses, and results have changed over time.")

matches, deliveries = load_data()

season_options = sorted(matches["season"].dropna().unique(), key=str)
match_type_options = sorted(matches["match_type"].dropna().unique(), key=str)

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_seasons = st.multiselect(
        "Seasons",
        season_options,
        default=season_options,
    )
with filter_col2:
    selected_match_types = st.multiselect(
        "Match types",
        match_type_options,
        default=match_type_options,
    )

filtered_matches = matches[
    matches["season"].isin(selected_seasons)
    & matches["match_type"].isin(selected_match_types)
].copy()

if filtered_matches.empty:
    st.warning("No matches match the selected filters.")
    st.stop()

filtered_match_ids = filtered_matches["id"].dropna().unique()
filtered_deliveries = deliveries[deliveries["match_id"].isin(filtered_match_ids)]
total_runs = int(filtered_deliveries["total_runs"].sum())
average_runs = total_runs / len(filtered_matches)
toss_decision_matches = filtered_matches[filtered_matches["toss_decision"].notna()]
toss_advantage = (
    (toss_decision_matches["toss_winner"] == toss_decision_matches["winner"]).mean() * 100
    if not toss_decision_matches.empty
    else 0
)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Matches", f"{len(filtered_matches):,}")
metric_col2.metric("Total Runs", f"{total_runs:,}")
metric_col3.metric("Average Runs / Match", f"{average_runs:,.0f}")
metric_col4.metric("Toss Winner Also Won", f"{toss_advantage:.1f}%")

st.subheader("Trends and patterns")

matches_by_season = (
    filtered_matches.groupby("season", sort=False).size().reset_index(name="Matches")
)
matches_by_season["season"] = matches_by_season["season"].astype(str)

wins = (
    filtered_matches["winner"]
    .dropna()
    .value_counts()
    .rename_axis("Team")
    .reset_index(name="Wins")
    .head(10)
)

result_counts = (
    filtered_matches["result"]
    .fillna("Unknown")
    .replace("NA", "Unknown")
    .value_counts()
    .rename_axis("Result")
    .reset_index(name="Matches")
)

toss_results = (
    filtered_matches["toss_decision"]
    .fillna("Unknown")
    .value_counts()
    .rename_axis("Decision")
    .reset_index(name="Matches")
)

if px is not None:
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            px.line(
                matches_by_season,
                x="season",
                y="Matches",
                markers=True,
                title="Matches played by season",
            ),
            use_container_width=True,
        )
    with chart_col2:
        st.plotly_chart(
            px.bar(
                wins,
                x="Team",
                y="Wins",
                color="Wins",
                title="Most match wins",
                color_continuous_scale="Oranges",
            ),
            use_container_width=True,
        )

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.plotly_chart(
            px.pie(
                result_counts,
                names="Result",
                values="Matches",
                hole=0.35,
                title="How matches were decided",
            ),
            use_container_width=True,
        )
    with chart_col4:
        st.plotly_chart(
            px.bar(
                toss_results,
                x="Decision",
                y="Matches",
                color="Decision",
                title="Toss decisions",
            ),
            use_container_width=True,
        )
else:
    st.warning("Plotly is not installed. Install it with `pip install plotly` for interactive charts.")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.line_chart(matches_by_season.set_index("season"))
    with chart_col2:
        st.bar_chart(wins.set_index("Team"))
    st.dataframe(result_counts, use_container_width=True)
    st.dataframe(toss_results, use_container_width=True)

st.subheader("Filtered match summary")
summary_columns = [
    "season",
    "date",
    "team1",
    "team2",
    "winner",
    "result",
    "result_margin",
    "toss_winner",
    "toss_decision",
]
available_summary_columns = [
    column for column in summary_columns if column in filtered_matches.columns
]
st.dataframe(
    filtered_matches[available_summary_columns].sort_values("date", ascending=False),
    use_container_width=True,
    hide_index=True,
)
import streamlit as st
from utils import load_data

try:
    import plotly.express as px
except ImportError:
    px = None

st.title("📈 EDA Dashboard")

matches, _ = load_data()

wins = matches['winner'].value_counts().reset_index()
wins.columns = ['Team', 'Wins']

if px is not None:
    fig = px.bar(wins, x='Team', y='Wins', title="Most Wins by Teams")
    st.plotly_chart(fig)
else:
    st.warning("Plotly is not installed. Install it with `pip install plotly` to view the full EDA chart.")
    st.bar_chart(wins.set_index('Team'))