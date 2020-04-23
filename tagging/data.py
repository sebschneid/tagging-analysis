import pathlib
import os
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

from tagging import helpers

ZONES_STR = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
ZONES = list(range(12))


def extract_single_csv(input_file, output_path: pathlib.Path, dataset_name: str, file_from_disk=True):
    if file_from_disk:
        with open(input_file) as file:
            content = np.array(file.readlines())
    else:
        content = np.array(input_file.readlines())

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    output_folder = output_path / dataset_name
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
        
    category_starts = np.argwhere(["CATEGORY" in line for line in content]).flatten()

    category_ends = category_starts[1:] - 1
    category_ends = np.concatenate([category_ends, np.array([len(content)])])
    
    for start, end in zip(category_starts, category_ends):
        category = content[start].split(";")[0].lower().replace("category: ", "").strip().replace(" ", "_")
        output_filepath = output_folder / f"{category}.csv"
        with open(output_filepath, "w") as file:
            file.writelines(content[start:end])
        print(f"Wrote {category} to {output_filepath}.")


def get_dataframes_for_phases(
    file_path: pathlib.Path, suffix: str = ""
) -> Dict[str, pd.DataFrame]:
    # file_path = data_path / filename
    # files = os.listdir(path)

    file_pressing = f"pressing{suffix}.csv"
    file_possession = f"possesion{suffix}.csv"
    file_pos_transition = f"positive_transition{suffix}.csv"
    file_neg_transition = f"negative_transition{suffix}.csv"

    df_pressing = preprocess_data(file_path, file_pressing)
    df_possession = preprocess_data(file_path, file_possession)
    df_neg_transition = preprocess_data(file_path, file_neg_transition)
    df_pos_transition = preprocess_data(file_path, file_pos_transition)

    return {
        "possession": df_possession,
        "pressing": df_pressing,
        "pos_transition": df_pos_transition,
        "neg_transition": df_neg_transition,
    }


def preprocess_data(
    file_path: pathlib.Path, filename: str, time_columns: List[str] = ["time", "start", "stop"]
) -> pd.DataFrame:
    df = pd.read_csv(file_path / filename, skiprows=1, header=0, sep=";")
    df = df.rename(helpers.normalize_column_name, axis="columns")
    for column in time_columns:
        df = df.assign(
            **{
                f"{column}_seconds": df[column]
                .str.split(":")
                .apply(helpers.get_total_seconds)
            }
        )

    df = df.assign(duration_seconds=df["stop_seconds"] - df["start_seconds"])
    df = df.rename(columns={column: int(column) for column in ZONES_STR})
    return df



def get_phase_peak_sums(
    dfs: Dict[str, pd.DataFrame]
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    own_buildup = dfs["possession"][ZONES].sum().reindex_like(pd.Series(ZONES))
    own_counter = (
        dfs["pos_transition"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )
    opp_buildup = dfs["pressing"][ZONES].sum().reindex_like(pd.Series(ZONES))
    opp_counter = (
        dfs["neg_transition"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )

    return own_buildup, own_counter, opp_buildup, opp_counter


def export_phases_df(dataset: pd.DataFrame, suffix: str = ""):
    dfs = get_dataframes_for_phases(dataset, suffix)
    own_buildup, own_counter, opp_buildup, opp_counter = get_phase_peak_sums(
        dfs
    )
    df_phases = pd.concat(
        [own_buildup, own_counter, opp_buildup, opp_counter], axis=1,
    )
    df_phases.columns = [
        "own_buildup",
        "own_counter",
        "opp_buildup",
        "opp_counter",
    ]
    df_phases.to_csv(f"../data/{dataset}_phases.csv")


def duration_overview(
    dataset: str, file_suffix: str = "", dur_column: str = "duration_seconds"
) -> None:
    dfs = get_dataframes_for_phases(dataset, file_suffix)
    for name, df in dfs.items():
        print(
            f"{name:>15}: duration_sum={df[dur_column].sum() / 60:<5.2f} min; duration_mean={df[dur_column].mean():<5.2f} s"
        )
