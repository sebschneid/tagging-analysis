import os
import pathlib
import string
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
from slugify import slugify

from tagging import helpers

ZONES_STR = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
ZONES = list(range(12))


def extract_single_csv(input_file: pathlib.Path, output_path: pathlib.Path, file_from_disk=True):
    if file_from_disk:
        with open(input_file) as file:
            content = np.array(file.readlines())
            dataset_name = input_file.name.rstrip(".csv")
    else:
        content = np.array(input_file.readlines())
        dataset_name = "upload"

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    output_folder = output_path / dataset_name
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
        
    category_starts = np.argwhere(["CATEGORY" in line for line in content]).flatten()

    category_ends = category_starts[1:] - 1
    category_ends = np.concatenate([category_ends, np.array([len(content)])])
    
    for start, end in zip(category_starts, category_ends):
        category_string = content[start].split(";")[0]
        category_regex_pattern = r'[^-a-z_]+'
        
        category_slug = slugify(category_string, separator='_', regex_pattern=category_regex_pattern)
        category = category_slug.replace("category_", "")
        
        output_filepath = output_folder / f"{category}.csv"
        with open(output_filepath, "w") as file:
            file.writelines(content[start:end])
        print(f"Wrote {category} to {output_filepath}")


def get_dataframes_for_phases(
    file_path: pathlib.Path, 
    suffix: str,    
    home_possession_name: str,
    away_counter_name: str,
    away_possession_name: str,
    home_counter_name: str,
) -> Dict[str, pd.DataFrame]:
    file_home_possession = f"{home_possession_name}{suffix}.csv"
    file_away_possession = f"{away_possession_name}{suffix}.csv"
    file_home_counter = f"{home_counter_name}{suffix}.csv"
    file_away_counter = f"{away_counter_name}{suffix}.csv"

    df_home_possession = preprocess_data(file_path, file_home_possession)
    df_away_possession = preprocess_data(file_path, file_away_possession)
    df_home_counter = preprocess_data(file_path, file_home_counter)
    df_away_counter = preprocess_data(file_path, file_away_counter)

    return {
        "home_possession": df_home_possession,
        "away_possession": df_away_possession,
        "home_counter": df_home_counter,
        "away_counter": df_away_counter,
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
    own_buildup = dfs["home_possession"][ZONES].sum().reindex_like(pd.Series(ZONES))
    own_counter = (
        dfs["home_counter"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )
    opp_buildup = dfs["away_possession"][ZONES].sum().reindex_like(pd.Series(ZONES))
    opp_counter = (
        dfs["away_counter"][ZONES].sum().reindex_like(pd.Series(ZONES))
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
