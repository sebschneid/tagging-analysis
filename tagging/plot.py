import pathlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib import patches

from tagging import data

# plt.rcParams["font.family"] = "sans-serif"
# plt.rcParams["font.sans-serif"] = "Tahoma"
# plt.rcParams["font.serif"] = "Myriad Pro"
plt.rcParams["figure.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = "xx-large"
plt.rcParams["axes.facecolor"] = "white"


KPI_COLORS = {
    "all": "black",
    "own_buildup": "#a0d5afff",
    "own_counter": "#c7e8e0ff",
    "opp_buildup": "#c4acd1ff",
    "opp_counter": "#e9b9d7ff",
}


BORDER_COLOR = "dimgrey"

BUILDUP_HATCH = ""
COUNTER_HATCH = ""

ZONE_RANGES = {
    "safe": (0, 2),
    "neutral": (3, 4),
    "risk": (5, 6),
    "warning": (7, 8),
    "danger": (9, 11),
    "all": (0, 11),
}

ZONE_COLORS = {
    "safe": "lime",
    "neutral": "lightyellow",
    "risk": "yellow",
    "warning": "orange",
    "danger": "red",
    "all": "black",
}

DEFAULT_XMIN = -0.5
DEFAULT_XMAX = 12.5
XTICKS_MIN = 0
XTICKS_MAX = 11

DEFAULT_FIGSIZE = (12, 10)

TITLE_PARAMS = {
    "x": 0.5,
    "y": 1.07,
    "fontweight": "bold",
    "color": "#00212E",
    "ha": "center",
    "va": "bottom",
    "fontsize": 26,
}

LEGEND_PARAMS = {
    "fontsize": 13.3,
    "ncol": 4,
    "bbox_to_anchor": (-0.01, 1.07),
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

SUMMARY_BOX_HEIGHT = 5
SUMMARY_BOX_PARAMS = {
    "width": 1.45,
    "fill": True,
    "alpha": 0.6,
}

# 11.5 bis 13

SUMMARY_TEXT_PARAMS = {
    "x": 12.0,
    "fontsize": 24,
    #    "va": "bottom",
    "ha": "center",
}


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


def add_summary_text(kpi_name, kpi_sum, y, fw, text_va, box_height, ax):
    if kpi_name != "all":
        ax.add_patch(
            patches.Rectangle(
                xy=(11.55, y),
                height=box_height,
                fc=KPI_COLORS[kpi_name],
                **SUMMARY_BOX_PARAMS,
            )
        )
    ax.text(
        y=y + box_height / 2,
        s=f"{kpi_sum}",
        fontweight=fw,
        va="center",
        **SUMMARY_TEXT_PARAMS,
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
    filter_time: False,
    seconds_start: float = None,
    seconds_stop: float = None,
    home_possession_name="possesion",
    away_counter_name="negative_transition",
    away_possession_name="pressing",
    home_counter_name="positive_transition",
    file_suffix: str = "",
    ymin: float = -35,
    ymax: float = 35,
    home_team: str = "",
    away_team: str = "",
    result: str = "",
    match_meta: str = "",
):
    # GET AGGREGATED DATA
    dfs = data.get_dataframes_for_phases(
        data_path,
        file_suffix,
        home_possession_name,
        away_counter_name,
        away_possession_name,
        home_counter_name,
    )
    
    if filter_time:
        dfs = {key: data.filter_time(df, seconds_start, seconds_stop) for key, df in dfs.items()}
    
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
        color=KPI_COLORS["own_buildup"],
        hatch=BUILDUP_HATCH,
        label="own buildups",
        ec=BORDER_COLOR,
    )
    ax.bar(
        data.ZONES,
        own_counter,
        bottom=own_buildup,
        color=KPI_COLORS["own_counter"],
        hatch=COUNTER_HATCH,
        label="own counters",
        ec=BORDER_COLOR,
    )

    # opponent bars
    ax.bar(
        data.ZONES,
        -opp_buildup,
        color=KPI_COLORS["opp_buildup"],
        hatch=BUILDUP_HATCH,
        label="opponent buildups",
        ec=BORDER_COLOR,
    )
    ax.bar(
        data.ZONES,
        -opp_counter,
        bottom=-opp_buildup,
        color=KPI_COLORS["opp_counter"],
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

    own_kpi = own_sums["risk"] + own_sums["warning"] + own_sums["danger"]
    opp_kpi = opp_sums["risk"] + opp_sums["warning"] + opp_sums["danger"]

    ## ZONE TEXTS
    add_zone_text("risk", own_sums, ymax, ax)
    add_zone_text("risk", opp_sums, ymin, ax)
    add_zone_text("warning", own_sums, ymax, ax)
    add_zone_text("warning", opp_sums, ymin, ax)
    add_zone_text("danger", own_sums, ymax, ax)
    add_zone_text("danger", opp_sums, ymin, ax)

    ## SUMMARY TEXTS
    own_all = own_buildup + own_counter
    opp_all = opp_buildup + opp_counter

    INITIAL_HEIGHT = 0
    HEIGHT_MARGIN_PERCENT = 1.00
    y_top = np.array(
        [
            INITIAL_HEIGHT + i * SUMMARY_BOX_HEIGHT * HEIGHT_MARGIN_PERCENT
            for i in range(3)
        ]
    )
    # y_bot = [- INITIAL_HEIGHT - (i+1)*box_height*HEIGHT_MARGIN_PERCENT for i in range(3)]
    y_bot = -y_top
    # y_bot = - y_top - box_height + INITIAL_HEIGHT / 2

    add_summary_text(
        "all",
        own_all.sum(),
        y=y_top[0],
        text_va="bottom",
        box_height=SUMMARY_BOX_HEIGHT,
        fw="bold",
        ax=ax,
    )
    add_summary_text(
        "own_buildup",
        own_buildup.sum(),
        y=y_top[1],
        text_va="bottom",
        box_height=SUMMARY_BOX_HEIGHT,
        fw="normal",
        ax=ax,
    )
    add_summary_text(
        "own_counter",
        own_counter.sum(),
        y=y_top[2],
        text_va="bottom",
        box_height=SUMMARY_BOX_HEIGHT,
        fw="normal",
        ax=ax,
    )

    add_summary_text(
        "all",
        opp_all.sum(),
        y=y_bot[0],
        text_va="top",
        box_height=-SUMMARY_BOX_HEIGHT,
        fw="bold",
        ax=ax,
    )
    add_summary_text(
        "opp_buildup",
        opp_buildup.sum(),
        y=y_bot[1],
        text_va="top",
        box_height=-SUMMARY_BOX_HEIGHT,
        fw="normal",
        ax=ax,
    )
    add_summary_text(
        "opp_counter",
        opp_counter.sum(),
        y=y_bot[2],
        text_va="top",
        box_height=-SUMMARY_BOX_HEIGHT,
        fw="normal",
        ax=ax,
    )

    ## RECTANGLES FOR SUMMARIES
    X_MARGIN = 0.02
    Y_MARGIN_PERCENT = 0.995
    x_summary_rectangle = get_xrange_for_zone("danger")[1] + X_MARGIN
    ax.add_patch(
        patches.Rectangle(
            xy=(x_summary_rectangle, 0.0),
            height=ymax * Y_MARGIN_PERCENT,
            width=DEFAULT_XMAX - x_summary_rectangle - X_MARGIN,
            ec="black",
            fill=None,
            lw=1.5,
        )
    )

    ax.add_patch(
        patches.Rectangle(
            xy=(x_summary_rectangle, 0.0),
            height=ymin * Y_MARGIN_PERCENT,
            width=DEFAULT_XMAX - x_summary_rectangle - X_MARGIN,
            ec="black",
            fill=None,
            lw=1.5,
        )
    )

    ## RECTANGLES FOR ZONES
    X_MARGIN = 0.0
    for zone in ZONE_RANGES.keys():
        if zone == "all":
            continue
        x_range = get_xrange_for_zone(zone)
        ax.add_patch(
            patches.Rectangle(
                xy=(x_range[0] + X_MARGIN, 0.1),
                height=ymax - 0.2,
                width=x_range[1] - x_range[0],
                ec="black",
                fill=None,
                lw=0.5,
            )
        )
        ax.add_patch(
            patches.Rectangle(
                xy=(x_range[0] + X_MARGIN, -0.1),
                height=ymin + 0.2,
                width=x_range[1] - x_range[0],
                ec="black",
                fill=None,
                lw=0.5,
            )
        )

    ## OVERALL MEDIAN
    own_progression_kpi = np.mean(own_all.index.repeat(own_all.values))
    opp_progression_kpi = np.mean(opp_all.index.repeat(opp_all.values))

    ax.axvline(
        x=own_progression_kpi, ymin=0.5, ymax=1, ls="--", c="grey"
    )  # , label="median")
    ax.axvline(x=opp_progression_kpi, ymin=0, ymax=0.5, ls="--", c="grey")

    # STYLE AND INFORMATION
    ax.set(
        xlim=(DEFAULT_XMIN, DEFAULT_XMAX),
        ylim=(ymin, ymax),
        ylabel="Number of attacks",
        xlabel="Progression peak (most outplayed opponents during attack)",
    )
    ax.set_yticks(np.arange(ymin, ymax + 1, 1), minor=True)
    ax.set_yticks(np.arange(ymin, ymax + 1, 5))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(get_positive_yticks))
    ax.set_xticks(np.arange(XTICKS_MIN, XTICKS_MAX + 1, 1))
    ax.set_axisbelow(True)
    ax.grid(axis="y", which="major", alpha=0.5, zorder=0)
    ax.legend(**LEGEND_PARAMS)

    title = f"{match_meta} {home_team} - {away_team} ({result})"
    # dataset textbox
    ax.text(s=title, transform=ax.transAxes, **TITLE_PARAMS)

    return fig, ax


def four_tile_plot(dataset: str, file_suffix: str = "") -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 10))
    dfs = data.get_dataframes_for_phases(dataset, file_suffix)
    for (name, df), ax in zip(dfs.items(), axes.flatten()):
        df[zones].sum().plot.bar(title=name, ax=ax)
    for ax in axes.flatten():
        ax.set_ylim(0, 14)

    return fig, axes
