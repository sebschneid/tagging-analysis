import pathlib
import shutil

import streamlit as st

from tagging import data, plot


# data_path = pathlib.Path("../data")
# output_path = pathlib.Path("./test_output")
# dataset = "solin"
# data_file = "solin.csv"

data_path = pathlib.Path("/tmp")
upload_path = data_path / "upload"

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
st.header("Dataset format")
naming_scheme = st.radio("Naming Scheme for phases", ["old", "new"])
naming_suffix = st.text_input("Suffix for relevant phase names", value="_peak")

st.sidebar.header("Plot Style")
ymin = st.sidebar.number_input(
    "Minimal value on y axis", min_value=-50, max_value=0, value=-35, step=1
)
ymax = st.sidebar.number_input(
    "Maximal value on y axis", min_value=0, max_value=50, value=35, step=1
)

st.sidebar.header("Match information")
match_meta = st.sidebar.text_input("Match Metainfo", value="Year, League")
team_home = st.sidebar.text_input("Home team name", value="HomeTeam")
team_away = st.sidebar.text_input("Away team name", value="AwayTeam")
score_home = st.sidebar.number_input("Home score", value=0, min_value=0)
score_away = st.sidebar.number_input("Away score", value=0, min_value=0)
result = f"{score_home} - {score_away}"

home_possession_name = "possesion"
away_counter_name = "negative_transition"
away_possession_name = "pressing"
home_counter_name = "positive_transition"

if naming_scheme == "new":
    home_possession_name = "possesion_home"
    away_counter_name = "counter_away"
    away_possession_name = "possession_away"
    home_counter_name = "counter_home"

if uploaded_file is not None:
    data.extract_single_csv(uploaded_file, data_path, file_from_disk=False)

    if st.button("Create graphs"):
        fig, ax = plot.make_phase_plot_for_dataset(
            upload_path,
            home_possession_name,
            away_counter_name,
            away_possession_name,
            home_counter_name,
            file_suffix=naming_suffix,
            ymin=ymin,
            ymax=ymax,
            home_team=team_home,
            away_team=team_away,
            result=result,
            match_meta=match_meta,
        )

        shutil.rmtree(upload_path)
        st.pyplot(fig)
