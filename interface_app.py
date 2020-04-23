import pathlib

import streamlit as st

from tagging import data, plot


#data_path = pathlib.Path("../data")
#output_path = pathlib.Path("./test_output")
#dataset = "solin"
#data_file = "solin.csv"

data_path = pathlib.Path("/tmp")
dataset_name = st.text_input("Enter the name of your dataset", value="Test")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
if uploaded_file is not None:
    data.extract_single_csv(uploaded_file, data_path, dataset_name, file_from_disk=False)    
    fig, ax = plot.make_phase_plot_for_dataset(data_path, dataset_name, file_suffix="_peak")
    st.pyplot(fig)