import pandas as pd

from energy_interop.analytics.kpis import calculate_energy_kwh, calculate_residual, simple_expected_power_pv
from energy_interop.transformations.time import attach_local_and_utc


def test_attach_local_and_utc_colombia_no_dst():
    frame = pd.DataFrame({"ts": ["2026-01-01 00:00:00"]})
    result = attach_local_and_utc(frame, "ts", "America/Bogota")
    assert str(result.loc[0, "timestamp_utc"]) == "2026-01-01 05:00:00+00:00"


def test_energy_from_average_power():
    frame = pd.DataFrame({"power_kw": [60.0, 30.0]})
    assert calculate_energy_kwh(frame, "power_kw", 15).tolist() == [15.0, 7.5]


def test_expected_power_and_residual():
    expected = simple_expected_power_pv(pd.Series([0, 500, 1200]), capacity_kw_ac=100)
    assert expected.tolist() == [0.0, 50.0, 100.0]
    residual = calculate_residual(pd.Series([10, 45]), pd.Series([8, 50]))
    assert residual.tolist() == [2.0, -5.0]
