import os
import pathlib
import string
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
from slugify import slugify
import io

from tagging import helpers

ZONES_STR = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
ZONES = list(range(12))


def extract_single_csv(
    input_file: pathlib.Path,
    output_path: pathlib.Path,
    file_from_disk=True,
    dataset_name="upload",
):
    if file_from_disk:
        with open(input_file) as file:
            content = np.array(file.readlines())
            dataset_name = input_file.name.rstrip(".csv")
    else:
        content = input_file.read().decode("utf-8").split("\n")

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    output_folder = output_path / dataset_name
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    category_starts = np.argwhere(
        ["CATEGORY" in line for line in content]
    ).flatten()

    category_ends = category_starts[1:] - 1
    category_ends = np.concatenate([category_ends, np.array([len(content)])])

    for start, end in zip(category_starts, category_ends):
        category_string = content[start].split(";")[0]
        category_regex_pattern = r"[^-a-z_]+"

        category_slug = slugify(
            category_string, separator="_", regex_pattern=category_regex_pattern
        )
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
    filter_time: bool,
    seconds_start: int,
    seconds_stop: int,
) -> Dict[str, pd.DataFrame]:
    file_home_possession = f"{home_possession_name}{suffix}.csv"
    file_away_possession = f"{away_possession_name}{suffix}.csv"
    file_home_counter = f"{home_counter_name}{suffix}.csv"
    file_away_counter = f"{away_counter_name}{suffix}.csv"

    filenames = [
        file_home_possession,
        file_away_possession,
        file_home_counter,
        file_away_counter,
    ]

    keys = [
        "home_possession",
        "away_possession",
        "home_counter",
        "away_counter",
    ]

    return {
        key: preprocess_data(
            file_path,
            file_name,
            filter_time,
            seconds_start,
            seconds_stop,
            skiprows=1,
            header=0,
            sep=";",
        )
        for key, file_name in zip(keys, filenames)
    }


def preprocess_data(
    file_path: pathlib.Path,
    filename: str,
    filter_time: bool,
    seconds_start: int,
    seconds_stop: int,
    time_columns: List[str] = ["time", "start", "stop"],
    rename_zones: bool = True,
    **read_csv_kwargs,
) -> pd.DataFrame:
    print(f"Reading {file_path / filename}")
    print(f"arguments: {read_csv_kwargs}")
    df = pd.read_csv(
        file_path / filename,
        engine="python",
        **read_csv_kwargs,
    )

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

    if rename_zones:
        df = df.rename(columns={column: int(column) for column in ZONES_STR})

    if filter_time:
        df = df.loc[
            (df["start_seconds"] >= seconds_start)
            & (df["start_seconds"] <= seconds_stop)
        ]

    return df


def get_phase_peak_sums(
    dfs: Dict[str, pd.DataFrame]
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    own_buildup = (
        dfs["home_possession"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )
    own_counter = (
        dfs["home_counter"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )
    opp_buildup = (
        dfs["away_possession"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )
    opp_counter = (
        dfs["away_counter"][ZONES].sum().reindex_like(pd.Series(ZONES))
    )

    return own_buildup, own_counter, opp_buildup, opp_counter


def export_phases_df(
    data_path: pathlib.Path,
    file_suffix: str,
    home_possession_name: str,
    away_counter_name: str,
    away_possession_name: str,
    home_counter_name: str,
) -> None:
    dfs = get_dataframes_for_phases(
        data_path,
        file_suffix,
        home_possession_name,
        away_counter_name,
        away_possession_name,
        home_counter_name,
        filter_time=False,
        seconds_start=None,
        seconds_stop=None,
    )
    own_buildup, own_counter, opp_buildup, opp_counter = get_phase_peak_sums(
        dfs
    )
    df_phases = pd.concat(
        [own_buildup, own_counter, opp_buildup, opp_counter],
        axis=1,
    )
    df_phases.columns = [
        "own_buildup",
        "own_counter",
        "opp_buildup",
        "opp_counter",
    ]
    # df_phases.to_csv(f"{data_path}_phases.csv")
    return df_phases


def duration_overview(
    dataset: str, file_suffix: str = "", dur_column: str = "duration_seconds"
) -> None:
    dfs = get_dataframes_for_phases(dataset, file_suffix)
    for name, df in dfs.items():
        print(
            f"{name:>15}: duration_sum={df[dur_column].sum() / 60:<5.2f} min; duration_mean={df[dur_column].mean():<5.2f} s"
        )


def aggregate_phases(
    data_path: pathlib.Path,
    filter_time: bool = False,
    seconds_start: float = None,
    seconds_stop: float = None,
    file_suffix: str = "",
    home_possession_name="possesion",
    away_counter_name="negative_transition",
    away_possession_name="pressing",
    home_counter_name="positive_transition",
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    # GET AGGREGATED DATA
    dfs = get_dataframes_for_phases(
        data_path,
        file_suffix,
        home_possession_name,
        away_counter_name,
        away_possession_name,
        home_counter_name,
        filter_time,
        seconds_start,
        seconds_stop,
    )
    (
        own_buildup,
        own_counter,
        opp_buildup,
        opp_counter,
    ) = get_phase_peak_sums(dfs)

    return own_buildup, own_counter, opp_buildup, opp_counter


def aggregate_set_pieces(
    data_path: pathlib.Path,
    filter_time: bool = False,
    seconds_start: int = None,
    seconds_stop: int = None,
) -> Tuple[pd.Series, pd.Series]:
    SET_PIECE_COLUMNS = [
        "corner",
        "free_kick",
        "half_distance",
        "throw_in",
    ]
    rename_columns = {
        col: col.lower().replace(" ", "_") for col in SET_PIECE_COLUMNS
    }

    FILES = ["attacking_set_pieces.csv", "deffending_set_pieces.csv"]

    test = preprocess_data(
        data_path,
        FILES[0],
        filter_time,
        seconds_start,
        seconds_stop,
        rename_zones=False,
        sep=";",
        header=1,
    )

    own_set_pieces, opp_set_pieces = (
        preprocess_data(
            data_path,
            filename,
            filter_time,
            seconds_start,
            seconds_stop,
            rename_zones=False,
            sep=";",
            header=1,
        )
        .sum()[SET_PIECE_COLUMNS]
        .rename(index=rename_columns)
        for filename in FILES
    )

    return own_set_pieces, opp_set_pieces
