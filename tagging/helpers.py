from typing import List

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
