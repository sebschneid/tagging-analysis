import pathlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

from tagging import data


plt.rcParams["figure.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = "xx-large"
plt.rcParams["axes.facecolor"] = "white"

OWN_COLOR_BUILDUP = "#a0d5afff"
OWN_COLOR_COUNTER = "#c7e8e0ff"
OPP_COLOR_BUILDUP = "#c4acd1ff"
OPP_COLOR_COUNTER = "#e9b9d7ff"
BORDER_COLOR = "dimgrey"

BUILDUP_HATCH = ""
COUNTER_HATCH = ""

ZONE_RANGES = {
    "safe": (0, 2),
    "neutral": (3, 4),
    "risk": (5, 6),
    "warning": (7, 8),
    "danger": (9, 11),
}

ZONE_COLORS = {
    "safe": "lime",
    "neutral": "lightyellow",
    "risk": "yellow",
    "warning": "orange",
    "danger": "red",
}

DEFAULT_FIGSIZE = (12, 10)
TITLE_HEIGHT = 1.05
TITLE_X = 0.95
LEGEND_PARAMS = {
    "fontsize": 18,
    "ncol": 2,
    "bbox_to_anchor": (0.0, 1.15),
    "loc": "upper left",
}

TEXT_Y_MARGIN = 0.85

ZONE_TEXT_PARAMS = {
    "fontsize": 24,
    "va": "center",
    "ha": "center",
    "color": "black",
    "fontweight": "bold",
}

SUM_TEXT_PARAMS = {"x": 0.85, **ZONE_TEXT_PARAMS}
PERCENTAGE_TEXT_PARAMS = {
    "fontsize": 20,
    "va": "center",
    "ha": "center",
    "bbox": {"boxstyle": "round", "facecolor": "aliceblue", "alpha": 0.8,},
}


def get_sums_in_zones(buildup: pd.Series, counter: pd.Series):
    overall = buildup + counter
    return {
        zone: overall.loc[start:end].sum()
        for zone, (start, end) in ZONE_RANGES.items()
    }


def get_percentages_in_zones(buildup: pd.Series, counter: pd.Series):
    overall = buildup + counter
    overall_sum = overall.sum()
    return {
        zone: overall.loc[start:end].sum() / overall_sum
        for zone, (start, end) in ZONE_RANGES.items()
    }


def get_xrange_for_zone(zone: str):
    return [ZONE_RANGES[zone][0] - 0.49, ZONE_RANGES[zone][1] + 0.49]


def get_mid_of_zone(zone: str) -> float:
    return (ZONE_RANGES[zone][0] + ZONE_RANGES[zone][1]) / 2


def get_positive_yticks(x, pos):
    return f"{abs(x)}"


def add_zone_text(zone: str, team_sums, y, ax):
    ax.text(
        x=get_mid_of_zone(zone),
        y=0.6 * y,
        s=f"{team_sums[zone]}",
        **ZONE_TEXT_PARAMS,
    )


def add_zone_percentage(percentages, zone, y, name, ax):
    x_position = get_mid_of_zone(zone)
    ax.text(
        x=x_position,
        y=y,
        s=f"{name}{percentages[zone]:.1%}",
        **PERCENTAGE_TEXT_PARAMS,
    )


def make_phase_plot_for_dataset(
    data_path: pathlib.Path,
    dataset_name: str,
    home_possession_name="possesion",
    away_counter_name="negative_transition",
    away_possession_name="pressing",
    home_counter_name="positive_transition",
    file_suffix: str = "",
    title: str = "",
    ymin: float = -35,
    ymax: float = 35,
    xmin: float = 0,
    xmax: float = 11,
):
    # GET AGGREGATED DATA
    dfs = data.get_dataframes_for_phases(
        data_path / dataset_name,
        file_suffix,
        home_possession_name,
        away_counter_name,
        away_possession_name,
        home_counter_name,
    )

    (
        own_buildup,
        own_counter,
        opp_buildup,
        opp_counter,
    ) = data.get_phase_peak_sums(dfs)

    # CREATE PLOT
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    # BAR PLOTS
    # own bars
    ax.bar(
        data.ZONES,
        own_buildup,
        color=OWN_COLOR_BUILDUP,
        hatch=BUILDUP_HATCH,
        label="own buildups",
        ec=BORDER_COLOR,
    )
    ax.bar(
        data.ZONES,
        own_counter,
        bottom=own_buildup,
        color=OWN_COLOR_COUNTER,
        hatch=COUNTER_HATCH,
        label="own counters",
        ec=BORDER_COLOR,
    )

    # opponent bars
    ax.bar(
        data.ZONES,
        -opp_buildup,
        color=OPP_COLOR_BUILDUP,
        hatch=BUILDUP_HATCH,
        label="opponent buildups",
        ec=BORDER_COLOR,
    )
    ax.bar(
        data.ZONES,
        -opp_counter,
        bottom=-opp_buildup,
        color=OPP_COLOR_COUNTER,
        hatch=COUNTER_HATCH,
        label="oppenent counters",
        ec=BORDER_COLOR,
    )

    # zeroline
    ax.axhline(lw=2, ls="-", color="black")

    # ZONE FILLS
    ax.fill_between(
        x=get_xrange_for_zone("safe"),
        y1=ymin,
        y2=ymax,
        color=ZONE_COLORS["safe"],
        alpha=0.15,
    )
    ax.fill_between(
        x=get_xrange_for_zone("neutral"),
        y1=ymin,
        y2=ymax,
        color=ZONE_COLORS["neutral"],
        alpha=0.2,
    )
    ax.fill_between(
        x=get_xrange_for_zone("risk"),
        y1=ymin,
        y2=ymax,
        color=ZONE_COLORS["risk"],
        alpha=0.25,
    )
    ax.fill_between(
        x=get_xrange_for_zone("warning"),
        y1=ymin,
        y2=ymax,
        color=ZONE_COLORS["warning"],
        alpha=0.25,
    )
    ax.fill_between(
        x=get_xrange_for_zone("danger"),
        y1=ymin,
        y2=ymax,
        color=ZONE_COLORS["danger"],
        alpha=0.25,
    )

    ## ZONE PERCENTAGES
    own_percentages = get_percentages_in_zones(own_buildup, own_counter)
    opp_percentages = get_percentages_in_zones(opp_buildup, opp_counter)

    # safe
    add_zone_percentage(own_percentages, "safe", ymax * TEXT_Y_MARGIN, "", ax)
    add_zone_percentage(opp_percentages, "safe", ymin * TEXT_Y_MARGIN, "", ax)

    # neutral
    add_zone_percentage(
        own_percentages, "neutral", ymax * TEXT_Y_MARGIN, "", ax
    )
    add_zone_percentage(
        opp_percentages, "neutral", ymin * TEXT_Y_MARGIN, "", ax
    )

    # risk
    add_zone_percentage(own_percentages, "risk", ymax * TEXT_Y_MARGIN, "", ax)
    add_zone_percentage(opp_percentages, "risk", ymin * TEXT_Y_MARGIN, "", ax)

    # warning and danger
    own_warning_and_danger = (
        own_percentages["danger"] + own_percentages["warning"]
    )
    opp_warning_and_danger = (
        opp_percentages["danger"] + opp_percentages["warning"]
    )
    warning_danger_pos = (
        ZONE_RANGES["warning"][1] + ZONE_RANGES["danger"][0]
    ) / 2
    ax.text(
        x=warning_danger_pos,
        y=ymax * TEXT_Y_MARGIN,
        s=f"{own_warning_and_danger:.1%}",
        **PERCENTAGE_TEXT_PARAMS,
    )
    ax.text(
        x=warning_danger_pos,
        y=ymin * TEXT_Y_MARGIN,
        s=f"{opp_warning_and_danger:.1%}",
        **PERCENTAGE_TEXT_PARAMS,
    )

    ## SUM OF ALL ATTACKS
    own_sums = get_sums_in_zones(own_buildup, own_counter)
    opp_sums = get_sums_in_zones(opp_buildup, opp_counter)

    # own_kpi = own_sums["risk"] + own_sums["warning"] + own_sums["danger"]
    # opp_kpi = opp_sums["risk"] + opp_sums["warning"] + opp_sums["danger"]

    # ax.text(y=0.75, s=f"{own_kpi}", transform=ax.transAxes, **SUM_TEXT_PARAMS)
    # ax.text(y=0.25, s=f"{opp_kpi}", transform=ax.transAxes, **SUM_TEXT_PARAMS)
    add_zone_text("risk", own_sums, ymax, ax)
    add_zone_text("risk", opp_sums, ymin, ax)
    add_zone_text("warning", own_sums, ymax, ax)
    add_zone_text("warning", opp_sums, ymin, ax)
    add_zone_text("danger", own_sums, ymax, ax)
    add_zone_text("danger", opp_sums, ymin, ax)

    ## OVERALL MEDIAN
    own_all = own_buildup + own_counter
    opp_all = opp_buildup + opp_counter
    own_progression_kpi = np.mean(own_all.index.repeat(own_all.values))
    opp_progression_kpi = np.mean(opp_all.index.repeat(opp_all.values))
    print(own_progression_kpi)
    print(opp_progression_kpi)
    ax.axvline(
        x=own_progression_kpi, ymin=0.5, ymax=1, ls="--", c="grey"
    )  # , label="median")
    ax.axvline(x=opp_progression_kpi, ymin=0, ymax=0.5, ls="--", c="grey")

    # STYLE AND INFORMATION
    ax.set(
        xlim=(xmin - 1, xmax + 1),
        ylim=(ymin, ymax),
        ylabel="Number of attacks",
        xlabel="Progression peak (most outplayed opponents during attack)",
    )
    ax.set_yticks(np.arange(ymin, ymax + 1, 1), minor=True)
    ax.set_yticks(np.arange(ymin, ymax + 1, 5))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(get_positive_yticks))
    ax.set_xticks(np.arange(xmin, xmax + 1, 1))
    ax.set_axisbelow(True)
    ax.grid(axis="y", which="major", alpha=0.5, zorder=0)
    ax.legend(**LEGEND_PARAMS)

    # dataset textbox
    ax.text(
        TITLE_X,
        TITLE_HEIGHT,
        title,
        transform=ax.transAxes,
        fontsize=26,
        fontweight="bold",
        color="C5",
        ha="right",
        va="bottom",
    )

    return fig, ax


def four_tile_plot(dataset: str, file_suffix: str = "") -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 10))
    dfs = data.get_dataframes_for_phases(dataset, file_suffix)
    for (name, df), ax in zip(dfs.items(), axes.flatten()):
        df[zones].sum().plot.bar(title=name, ax=ax)
    for ax in axes.flatten():
        ax.set_ylim(0, 14)

    return fig, axes
