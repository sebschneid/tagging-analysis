from typing import Dict, List, Optional
import pathlib

import pydantic
import pandas as pd

import tagging.data
import tagging.helpers


class ExtractionConfig(pydantic.BaseModel):
    opponent: str
    matchday: int
    data_path: pathlib.Path
    file_suffix: str
    start: Optional[int] = 0  # "00:00"
    stop: Optional[int] = 7200  # "120:00"
    halftime: Optional[int] = 3600  # "60:00"
    home_possession_name: Optional[str] = "possesion"
    away_counter_name: Optional[str] = "negative_transition"
    away_possession_name: Optional[str] = "pressing"
    home_counter_name: Optional[str] = "positive_transition"

    @classmethod
    def parse_obj(cls, obj):
        time_keys = ["start", "stop", "halftime"]
        return cls(
            **dict(
                obj,
                **{
                    time_key: tagging.helpers.string_time_to_seconds(
                        obj[time_key]
                    )
                    for time_key in time_keys
                },
            )
        )


class PackingCount(pydantic.BaseModel):
    count_to_value: Dict[int, int]

    @pydantic.validator("count_to_value", allow_reuse=True)
    def all_zones_available(cls, v):
        count_not_in_keys = [count not in v.keys() for count in range(0, 12)]
        if sum(count_not_in_keys) > 0:
            raise pydantic.ValidationError(
                "Values for some packing counts are missing."
            )
        return v


class Attacks(pydantic.BaseModel):
    possession: int
    counter: int


class Counterpressing(pydantic.BaseModel):
    successful: int
    unsuccessful: int


class SetPieces(pydantic.BaseModel):
    free_kick: int
    half_distance: int
    corner: int
    throw_in: int


PACKING_ATTRIBUTES = [
    "own_packing_peak_total",
    "own_packing_peak_buildup",
    "own_packing_peak_counter",
    "opp_packing_peak_total",
    "opp_packing_peak_buildup",
    "opp_packing_peak_counter",
    "own_packing_peak_total_1st_half",
    "own_packing_peak_buildup_1st_half",
    "own_packing_peak_counter_1st_half",
    "opp_packing_peak_total_1st_half",
    "opp_packing_peak_buildup_1st_half",
    "opp_packing_peak_counter_1st_half",
    "own_packing_peak_total_2nd_half",
    "own_packing_peak_buildup_2nd_half",
    "own_packing_peak_counter_2nd_half",
    "opp_packing_peak_total_2nd_half",
    "opp_packing_peak_buildup_2nd_half",
    "opp_packing_peak_counter_2nd_half",
]

SET_PIECE_ATTRIBUES = [
    "own_setpieces",
    "opp_setpieces",
    "own_setpieces_1st_half",
    "opp_setpieces_1st_half",
    "own_setpieces_2nd_half",
    "opp_setpieces_2nd_half",
]

ATTACKS_ATTRIBUTES = [
    "own_attacks",
    "opp_attacks",
    "own_attacks_1st_half",
    "opp_attacks_1st_half",
    "own_attacks_2nd_half",
    "opp_attacks_2nd_half",
]


class AggregationRow(pydantic.BaseModel):
    matchday: int
    opponent: str

    # PACKING
    # totals
    own_packing_peak_total: PackingCount
    own_packing_peak_buildup: PackingCount
    own_packing_peak_counter: PackingCount
    opp_packing_peak_total: PackingCount
    opp_packing_peak_buildup: PackingCount
    opp_packing_peak_counter: PackingCount

    # 1st half
    own_packing_peak_total_1st_half: PackingCount
    own_packing_peak_buildup_1st_half: PackingCount
    own_packing_peak_counter_1st_half: PackingCount
    opp_packing_peak_total_1st_half: PackingCount
    opp_packing_peak_buildup_1st_half: PackingCount
    opp_packing_peak_counter_1st_half: PackingCount

    # 2nd half
    own_packing_peak_total_2nd_half: PackingCount
    own_packing_peak_buildup_2nd_half: PackingCount
    own_packing_peak_counter_2nd_half: PackingCount
    opp_packing_peak_total_2nd_half: PackingCount
    opp_packing_peak_buildup_2nd_half: PackingCount
    opp_packing_peak_counter_2nd_half: PackingCount

    # # ATTACKS
    own_attacks: Attacks
    opp_attacks: Attacks
    own_attacks_1st_half: Attacks
    opp_attacks_1st_half: Attacks
    own_attacks_2nd_half: Attacks
    opp_attacks_2nd_half: Attacks

    # # SHOTS
    # own_shots: int
    # opp_shots: int

    # # COUNTERPRESSING
    # Counterpressing: Counterpressing

    # # SET PIECES
    own_setpieces: SetPieces
    opp_setpieces: SetPieces
    own_setpieces_1st_half: SetPieces
    opp_setpieces_1st_half: SetPieces
    own_setpieces_2nd_half: SetPieces
    opp_setpieces_2nd_half: SetPieces

    @classmethod
    def create_from_config(cls, extraction_config: ExtractionConfig):
        aggregation_dict = dict(
            opponent=extraction_config.opponent,
            matchday=extraction_config.matchday,
        )
        # PACKING
        # totals
        (
            own_buildup,
            own_counter,
            opp_buildup,
            opp_counter,
        ) = tagging.data.aggregate_phases(
            data_path=extraction_config.data_path,
            file_suffix=extraction_config.file_suffix,
            home_possession_name=extraction_config.home_possession_name,
            away_counter_name=extraction_config.away_counter_name,
            away_possession_name=extraction_config.away_possession_name,
            home_counter_name=extraction_config.home_counter_name,
            filter_time=True,
            seconds_start=extraction_config.start,
            seconds_stop=extraction_config.stop,
        )
        aggregation_dict.update(
            dict(
                own_attacks=Attacks(
                    possession=own_buildup.sum(), counter=own_counter.sum()
                ),
                opp_attacks=Attacks(
                    possession=opp_buildup.sum(), counter=opp_counter.sum()
                ),
                own_packing_peak_total=PackingCount(
                    count_to_value=(own_buildup + own_counter).to_dict()
                ),
                own_packing_peak_buildup=PackingCount(
                    count_to_value=(own_buildup).to_dict()
                ),
                own_packing_peak_counter=PackingCount(
                    count_to_value=(own_counter).to_dict()
                ),
                opp_packing_peak_total=PackingCount(
                    count_to_value=(opp_buildup + opp_counter).to_dict()
                ),
                opp_packing_peak_buildup=PackingCount(
                    count_to_value=(opp_buildup).to_dict()
                ),
                opp_packing_peak_counter=PackingCount(
                    count_to_value=(opp_counter).to_dict()
                ),
            )
        )

        # 1st half
        (
            own_buildup,
            own_counter,
            opp_buildup,
            opp_counter,
        ) = tagging.data.aggregate_phases(
            data_path=extraction_config.data_path,
            file_suffix=extraction_config.file_suffix,
            home_possession_name=extraction_config.home_possession_name,
            away_counter_name=extraction_config.away_counter_name,
            away_possession_name=extraction_config.away_possession_name,
            home_counter_name=extraction_config.home_counter_name,
            filter_time=True,
            seconds_start=extraction_config.start,
            seconds_stop=extraction_config.halftime,
        )
        aggregation_dict.update(
            dict(
                own_attacks_1st_half=Attacks(
                    possession=own_buildup.sum(), counter=own_counter.sum()
                ),
                opp_attacks_1st_half=Attacks(
                    possession=opp_buildup.sum(), counter=opp_counter.sum()
                ),
                own_packing_peak_total_1st_half=PackingCount(
                    count_to_value=(own_buildup + own_counter).to_dict()
                ),
                own_packing_peak_buildup_1st_half=PackingCount(
                    count_to_value=(own_buildup).to_dict()
                ),
                own_packing_peak_counter_1st_half=PackingCount(
                    count_to_value=(own_counter).to_dict()
                ),
                opp_packing_peak_total_1st_half=PackingCount(
                    count_to_value=(opp_buildup + opp_counter).to_dict()
                ),
                opp_packing_peak_buildup_1st_half=PackingCount(
                    count_to_value=(opp_buildup).to_dict()
                ),
                opp_packing_peak_counter_1st_half=PackingCount(
                    count_to_value=(opp_counter).to_dict()
                ),
            )
        )

        # 2nd half
        (
            own_buildup,
            own_counter,
            opp_buildup,
            opp_counter,
        ) = tagging.data.aggregate_phases(
            data_path=extraction_config.data_path,
            file_suffix=extraction_config.file_suffix,
            home_possession_name=extraction_config.home_possession_name,
            away_counter_name=extraction_config.away_counter_name,
            away_possession_name=extraction_config.away_possession_name,
            home_counter_name=extraction_config.home_counter_name,
            filter_time=True,
            seconds_start=extraction_config.halftime,
            seconds_stop=extraction_config.stop,
        )
        aggregation_dict.update(
            dict(
                own_attacks_2nd_half=Attacks(
                    possession=own_buildup.sum(), counter=own_counter.sum()
                ),
                opp_attacks_2nd_half=Attacks(
                    possession=opp_buildup.sum(), counter=opp_counter.sum()
                ),
                own_packing_peak_total_2nd_half=PackingCount(
                    count_to_value=(own_buildup + own_counter).to_dict()
                ),
                own_packing_peak_buildup_2nd_half=PackingCount(
                    count_to_value=(own_buildup).to_dict()
                ),
                own_packing_peak_counter_2nd_half=PackingCount(
                    count_to_value=(own_counter).to_dict()
                ),
                opp_packing_peak_total_2nd_half=PackingCount(
                    count_to_value=(opp_buildup + opp_counter).to_dict()
                ),
                opp_packing_peak_buildup_2nd_half=PackingCount(
                    count_to_value=(opp_buildup).to_dict()
                ),
                opp_packing_peak_counter_2nd_half=PackingCount(
                    count_to_value=(opp_counter).to_dict()
                ),
            )
        )

        # SET PIECES
        # full time
        own_setpieces, opp_setpieces = tagging.data.aggregate_set_pieces(
            data_path=extraction_config.data_path,
            filter_time=True,
            seconds_start=extraction_config.start,
            seconds_stop=extraction_config.stop,
        )

        aggregation_dict.update(
            dict(
                own_setpieces=SetPieces.parse_obj(own_setpieces),
                opp_setpieces=SetPieces.parse_obj(opp_setpieces),
            )
        )

        # 1st half
        own_setpieces, opp_setpieces = tagging.data.aggregate_set_pieces(
            data_path=extraction_config.data_path,
            filter_time=True,
            seconds_start=extraction_config.start,
            seconds_stop=extraction_config.halftime,
        )

        aggregation_dict.update(
            dict(
                own_setpieces_1st_half=SetPieces.parse_obj(own_setpieces),
                opp_setpieces_1st_half=SetPieces.parse_obj(opp_setpieces),
            )
        )

        # 2nd half
        own_setpieces, opp_setpieces = tagging.data.aggregate_set_pieces(
            data_path=extraction_config.data_path,
            filter_time=True,
            seconds_start=extraction_config.halftime,
            seconds_stop=extraction_config.stop,
        )

        aggregation_dict.update(
            dict(
                own_setpieces_2nd_half=SetPieces.parse_obj(own_setpieces),
                opp_setpieces_2nd_half=SetPieces.parse_obj(opp_setpieces),
            )
        )

        return cls.parse_obj(aggregation_dict)


def get_packing_series(row: AggregationRow) -> pd.Series:
    packing_series = []
    for attr in PACKING_ATTRIBUTES:
        packing_series.append(
            pd.Series(
                {
                    (attr, key): value
                    for key, value in getattr(row, attr).count_to_value.items()
                },
                name=(row.matchday, row.opponent),
            )
        )

    return pd.concat(packing_series)


def get_set_piece_series(row: AggregationRow):
    set_piece_series = []
    for attr in SET_PIECE_ATTRIBUES:
        set_piece_series.append(
            pd.Series(
                {
                    (attr, key): value
                    for key, value in getattr(row, attr).dict().items()
                },
                name=(row.matchday, row.opponent),
            )
        )

    return pd.concat(set_piece_series)


def get_attacks_series(row: AggregationRow):
    attacks_series = []
    for attr in ATTACKS_ATTRIBUTES:
        attacks_series.append(
            pd.Series(
                {
                    (attr, key): value
                    for key, value in getattr(row, attr).dict().items()
                },
                name=(row.matchday, row.opponent),
            )
        )

    return pd.concat(attacks_series)


def extract_rows(aggregation_rows: List[AggregationRow]) -> pd.DataFrame:
    aggregation_series = []
    for row in aggregation_rows:
        packing_series = get_packing_series(row)
        set_piece_series = get_set_piece_series(row)
        attacks_series = get_attacks_series(row)
        aggregation_series.append(
            pd.concat([packing_series, set_piece_series, attacks_series])
        )

    df_extract = pd.DataFrame(aggregation_series)
    return df_extract
