from __future__ import annotations

import pandas as pd


def attach_local_and_utc(
    frame: pd.DataFrame,
    timestamp_col: str,
    source_timezone: str,
    output_local_timezone: str | None = None,
) -> pd.DataFrame:
    result = frame.copy()
    ts = pd.to_datetime(result[timestamp_col], errors="raise")
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize(source_timezone, ambiguous="infer", nonexistent="shift_forward")
    result["timestamp_utc"] = ts.dt.tz_convert("UTC")
    result["timestamp_local"] = ts.dt.tz_convert(output_local_timezone or source_timezone)
    return result


def energy_from_average_power(power_kw: pd.Series, interval_minutes: float) -> pd.Series:
    return power_kw * (interval_minutes / 60.0)
