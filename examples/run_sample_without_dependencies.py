"""Run an end-to-end sample pipeline using only the Python standard library.

This script exists so reviewers can inspect concrete MVP outputs even in restricted
execution environments where pandas, pandera or pyarrow are not installed. The
production-oriented pipeline remains `examples/run_sam_pipeline.py`.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("America/Bogota")
CAPACITY_KW_AC = 1_000.0
INTERVAL_HOURS = 1.0


@dataclass(frozen=True)
class SampleRow:
    asset_id: str
    source: str
    timestamp_local: str
    timestamp_utc: str
    ghi_w_m2: float
    actual_power_kw: float
    expected_power_kw: float
    residual_kw: float
    energy_kwh_net: float
    quality_flag: str


def _parse_local_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M").replace(tzinfo=LOCAL_TZ)


def _expected_power_kw(ghi_w_m2: float) -> float:
    return min(max(ghi_w_m2, 0.0) / 1_000.0 * CAPACITY_KW_AC, CAPACITY_KW_AC)


def _quality_flag(ghi_w_m2: float, actual_power_kw: float) -> str:
    if ghi_w_m2 < 0:
        return "physical_range_violation"
    if actual_power_kw < 0:
        return "negative_power_impossible"
    if actual_power_kw > CAPACITY_KW_AC * 1.10:
        return "power_above_physical_limit"
    if ghi_w_m2 > 20 and actual_power_kw == 0:
        return "possible_outage_or_curtailment"
    return "ok"


def run(input_csv: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[SampleRow] = []

    with input_csv.open(newline="", encoding="utf-8") as handle:
        for record in csv.DictReader(handle):
            local_dt = _parse_local_timestamp(record["timestamp"])
            utc_dt = local_dt.astimezone(timezone.utc)
            ghi = float(record["GHI"])
            actual = float(record["power_ac_kw"])
            expected = _expected_power_kw(ghi)
            rows.append(
                SampleRow(
                    asset_id="pv_demo_colombia",
                    source="sam_csv_sample",
                    timestamp_local=local_dt.isoformat(),
                    timestamp_utc=utc_dt.isoformat().replace("+00:00", "Z"),
                    ghi_w_m2=ghi,
                    actual_power_kw=actual,
                    expected_power_kw=round(expected, 3),
                    residual_kw=round(actual - expected, 3),
                    energy_kwh_net=round(actual * INTERVAL_HOURS, 3),
                    quality_flag=_quality_flag(ghi, actual),
                )
            )

    canonical_csv = output_dir / "canonical_measurements.csv"
    with canonical_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)

    kpi_summary = {
        "asset_id": "pv_demo_colombia",
        "period_start_utc": rows[0].timestamp_utc,
        "period_end_utc": rows[-1].timestamp_utc,
        "records": len(rows),
        "energy_kwh_net": round(sum(row.energy_kwh_net for row in rows), 3),
        "expected_energy_kwh": round(sum(row.expected_power_kw * INTERVAL_HOURS for row in rows), 3),
        "mean_residual_kw": round(mean(row.residual_kw for row in rows), 3),
        "quality_flag_counts": {flag: sum(row.quality_flag == flag for row in rows) for flag in sorted({row.quality_flag for row in rows})},
    }
    summary_json = output_dir / "kpi_summary.json"
    summary_json.write_text(json.dumps(kpi_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {"canonical_csv": str(canonical_csv), "summary_json": str(summary_json), "summary": kpi_summary}


if __name__ == "__main__":
    result = run(Path("examples/sample_data/sam_weather_sample.csv"), Path("examples/sample_output"))
    print(json.dumps(result, indent=2, ensure_ascii=False))
