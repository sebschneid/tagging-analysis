from typing import List
import base64

import pandas as pd

SECONDS_FOR_UNIT = {
    "hour": 3600,
    "minute": 60,
    "second": 1,
    "millisecond": 0.001,
}


def normalize_column_name(column: str) -> str:
    return column.replace(" ", "_").lower().strip()


def get_total_seconds(time_split: List[str]) -> float:
    # time from format {HH:}MM:SS,ms (hours optional)
    # split into single entries and calculate seconds per unit

    seconds_split = time_split[-1].split(",")
    time_split = time_split[:-1] + seconds_split
    units = list(SECONDS_FOR_UNIT.keys())
    used_units = units[4 - len(time_split) :]
    return sum(
        int(time_entry) * SECONDS_FOR_UNIT[unit]
        for time_entry, unit in zip(time_split, used_units)
    )


def format_total_seconds(total_seconds: int) -> str:
    # output "MM:SS"
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds - minutes * 60)
    return f"{minutes:02d}:{seconds:02d}"


def string_time_to_seconds(time: str) -> int:
    minute, second = time.split(":")
    return int(int(minute) * 60 + int(second))


def download_link(
    object_to_download,
    download_filename: str,
    download_link_text: str,
    index: bool,
):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=index)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode("utf-8")).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'