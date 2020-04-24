import pathlib
import shutil

import streamlit as st

from tagging import data, plot


# data_path = pathlib.Path("../data")
# output_path = pathlib.Path("./test_output")
# dataset = "solin"
# data_file = "solin.csv"

data_path = pathlib.Path("/tmp")
upload_folder_name = "upload"

dataset_name = st.text_input("Enter the name of your dataset", value="Test")
naming_scheme = st.radio("Naming Scheme for phases", ["old", "new"])
naming_suffix = st.text_input("Suffix for relevant phase names", value="_peak")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
ymin = st.slider("Minimal value on y axis", min_value=-50, max_value=0, value=-35, step=1)
ymax = st.slider("Maximal value on y axis", min_value=0, max_value=50, value=35, step=1)

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
            data_path,
            upload_folder_name,
            home_possession_name,
            away_counter_name,
            away_possession_name,
            home_counter_name,
            title=dataset_name,
            file_suffix=naming_suffix,
            ymin=ymin,
            ymax=ymax,
        )

        shutil.rmtree(data_path / upload_folder_name)
        st.pyplot(fig)
