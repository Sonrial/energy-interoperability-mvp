from __future__ import annotations

import pandas as pd


def calculate_energy_kwh(frame: pd.DataFrame, power_col: str, interval_minutes: float) -> pd.Series:
    return frame[power_col].astype(float) * interval_minutes / 60.0


def calculate_residual(actual_kw: pd.Series, expected_kw: pd.Series) -> pd.Series:
    return actual_kw.astype(float) - expected_kw.astype(float)


def simple_expected_power_pv(ghi_w_m2: pd.Series, capacity_kw_ac: float, reference_ghi: float = 1000.0) -> pd.Series:
    return (ghi_w_m2.clip(lower=0) / reference_ghi * capacity_kw_ac).clip(upper=capacity_kw_ac)
