import pathlib
import shutil

import streamlit as st

from tagging import data, plot, helpers

data_path = pathlib.Path("/tmp")
upload_path = data_path / "upload"

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
st.header("Dataset format")
naming_scheme = st.radio("Naming Scheme for phases", ["old", "new"])
naming_suffix = st.text_input("Suffix for relevant phase names", value="_peak")

st.sidebar.header("Plot Selection")
add_halftimes = st.sidebar.checkbox("Graphs for both halftimes", value=True)
add_poss_vs_counter = st.sidebar.checkbox(
    "Graphs for possession vs counter", value=True
)

st.sidebar.header("Plot Style")
ymin = st.sidebar.number_input(
    "Minimal value on y axis", min_value=-50, max_value=0, value=-28, step=1
)
ymax = st.sidebar.number_input(
    "Maximal value on y axis", min_value=0, max_value=50, value=28, step=1
)

st.sidebar.header("Match information")
match_meta = st.sidebar.text_input("Match Metainfo", value="Year, League")
team_home = st.sidebar.text_input("Home team name", value="HomeTeam")
team_away = st.sidebar.text_input("Away team name", value="AwayTeam")
score_home = st.sidebar.number_input("Home score", value=0, min_value=0)
score_away = st.sidebar.number_input("Away score", value=0, min_value=0)

## Select time in the video
minute_start = st.sidebar.number_input(
    "Start minute considered in video",
    value=0,
)
print(type(minute_start))
second_start = st.sidebar.number_input(
    "Start second considered im video", value=0
)
print(type(second_start))
seconds_start = int(minute_start * 60 + second_start)

minute_stop = st.sidebar.number_input(
    "Last minute considered in video", value=120
)
second_stop = st.sidebar.number_input(
    "Last second considered in video", value=0
)
seconds_stop = int(minute_stop * 60 + second_stop)


## Names for data
home_possession_name = "possesion"
away_counter_name = "negative_transition"
away_possession_name = "pressing"
home_counter_name = "positive_transition"

if naming_scheme == "new":
    home_possession_name = "possesion_home"
    away_counter_name = "counter_away"
    away_possession_name = "possession_away"
    home_counter_name = "counter_home"

## Result string
result = f"{score_home} - {score_away}"

if uploaded_file is not None:
    data.extract_single_csv(uploaded_file, data_path, file_from_disk=False)

    if st.button("Create graphs"):
        # part time
        (
            own_buildup,
            own_counter,
            opp_buildup,
            opp_counter,
        ) = data.aggregate_phases(
            data_path=upload_path,
            filter_time=True,
            seconds_start=seconds_start,
            seconds_stop=seconds_stop,
            home_possession_name=home_possession_name,
            away_counter_name=away_counter_name,
            away_possession_name=away_possession_name,
            home_counter_name=home_counter_name,
            file_suffix=naming_suffix,
        )
        fig_part_time, ax = plot.make_phase_plot_for_dataset(
            own_buildup=own_buildup,
            own_counter=own_counter,
            opp_buildup=opp_buildup,
            opp_counter=opp_counter,
            ymin=ymin,
            ymax=ymax,
            home_team=team_home,
            away_team=team_away,
            result=result,
            match_meta=match_meta,
        )

        # full time
        (
            own_buildup,
            own_counter,
            opp_buildup,
            opp_counter,
        ) = data.aggregate_phases(
            data_path=upload_path,
            filter_time=False,
            seconds_start=None,
            seconds_stop=None,
            home_possession_name=home_possession_name,
            away_counter_name=away_counter_name,
            away_possession_name=away_possession_name,
            home_counter_name=home_counter_name,
            file_suffix=naming_suffix,
        )
        fig_full_time, ax = plot.make_phase_plot_for_dataset(
            own_buildup=own_buildup,
            own_counter=own_counter,
            opp_buildup=opp_buildup,
            opp_counter=opp_counter,
            ymin=ymin,
            ymax=ymax,
            home_team=team_home,
            away_team=team_away,
            result=result,
            match_meta=match_meta,
        )

        st.subheader("Graph for selected timeframe")
        st.pyplot(fig_part_time)

        st.subheader("Graph for complete match")
        st.pyplot(fig_full_time)

        if add_poss_vs_counter:
            fig_own_poss, ax = plot.make_phase_plot_for_dataset(
                own_buildup=own_buildup,
                opp_counter=opp_counter,
                ymin=ymin,
                ymax=ymax,
                home_team=team_home,
                away_team=team_away,
                result=result,
                match_meta=match_meta,
            )

            fig_own_counter, ax = plot.make_phase_plot_for_dataset(
                own_counter=own_counter,
                opp_buildup=opp_buildup,
                ymin=ymin,
                ymax=ymax,
                home_team=team_home,
                away_team=team_away,
                result=result,
                match_meta=match_meta,
            )

            st.subheader("Graphs for possession vs counter")

            st.markdown("#### Own possession vs. opponent counter")
            st.pyplot(fig_own_poss)

            st.markdown("#### Own counter vs. opponent possession")
            st.pyplot(fig_own_counter)

        if add_halftimes:
            # first half
            seconds_start_first_half = seconds_start
            seconds_stop_first_half = seconds_stop / 2
            (
                own_buildup,
                own_counter,
                opp_buildup,
                opp_counter,
            ) = data.aggregate_phases(
                data_path=upload_path,
                filter_time=True,
                seconds_start=seconds_start_first_half,
                seconds_stop=seconds_stop_first_half,
                home_possession_name=home_possession_name,
                away_counter_name=away_counter_name,
                away_possession_name=away_possession_name,
                home_counter_name=home_counter_name,
                file_suffix=naming_suffix,
            )
            fig_first_half, ax = plot.make_phase_plot_for_dataset(
                own_buildup=own_buildup,
                own_counter=own_counter,
                opp_buildup=opp_buildup,
                opp_counter=opp_counter,
                ymin=ymin / 2,
                ymax=ymax / 2,
                home_team=team_home,
                away_team=team_away,
                result=result,
                match_meta=match_meta,
            )

            # second half
            seconds_start_second_half = seconds_stop_first_half
            seconds_stop_second_half = seconds_stop
            (
                own_buildup,
                own_counter,
                opp_buildup,
                opp_counter,
            ) = data.aggregate_phases(
                data_path=upload_path,
                filter_time=True,
                seconds_start=seconds_start_second_half,
                seconds_stop=seconds_stop_second_half,
                home_possession_name=home_possession_name,
                away_counter_name=away_counter_name,
                away_possession_name=away_possession_name,
                home_counter_name=home_counter_name,
                file_suffix=naming_suffix,
            )
            fig_second_half, ax = plot.make_phase_plot_for_dataset(
                own_buildup=own_buildup,
                own_counter=own_counter,
                opp_buildup=opp_buildup,
                opp_counter=opp_counter,
                ymin=ymin / 2,
                ymax=ymax / 2,
                home_team=team_home,
                away_team=team_away,
                result=result,
                match_meta=match_meta,
            )

            st.subheader("Graphs for both halftimes")
            st.info(
                f"1st half: {minute_start:02d}:{second_start:02d}"
                f" to {helpers.format_total_seconds(seconds_stop_first_half)}.\n"
                f"2nd half: {helpers.format_total_seconds(seconds_start_second_half)}"
                f" to {minute_stop:02d}:{second_stop:02d}"
            )
            st.markdown("#### First Half")
            st.pyplot(fig_first_half)

            st.markdown("#### Second Half")
            st.pyplot(fig_second_half)

        shutil.rmtree(upload_path)
