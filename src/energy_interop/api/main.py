from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = PACKAGE_ROOT / "api" / "static"
SAMPLE_MEASUREMENTS = REPO_ROOT / "examples" / "sample_output" / "canonical_measurements.csv"
SAMPLE_KPIS = REPO_ROOT / "examples" / "sample_output" / "kpi_summary.json"

app = FastAPI(title="Energy Interoperability MVP API", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/assets")
def list_assets(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)) -> dict:
    return {
        "items": [
            {
                "asset_id": "pv_demo_colombia",
                "plant_id": "plant_demo_colombia",
                "name": "PV Demo Colombia",
                "technology": "solar_pv",
                "timezone": "America/Bogota",
            }
        ][offset : offset + limit],
        "limit": limit,
        "offset": offset,
        "next_offset": None,
    }


@app.get("/assets/{asset_id}/operational-measurements")
def operational_measurements(
    asset_id: str,
    start: datetime,
    end: datetime,
    limit: int = Query(1000, le=10000),
) -> dict:
    rows = _read_sample_measurements()
    filtered = [
        row
        for row in rows
        if row["asset_id"] == asset_id
        and start.isoformat() <= row["timestamp_utc"].replace("Z", "+00:00") <= end.isoformat()
    ]
    return {"asset_id": asset_id, "start": start, "end": end, "items": filtered[:limit], "limit": limit}


@app.get("/api/sample/measurements")
def sample_measurements(
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
) -> dict:
    rows = _read_sample_measurements()
    page = rows[offset : offset + limit]
    next_offset = offset + limit if offset + limit < len(rows) else None
    return {"items": page, "limit": limit, "offset": offset, "next_offset": next_offset}


@app.get("/api/sample/kpis")
def sample_kpis() -> dict:
    return json.loads(SAMPLE_KPIS.read_text(encoding="utf-8"))


def _read_sample_measurements() -> list[dict[str, str | float]]:
    with SAMPLE_MEASUREMENTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    numeric_columns = {
        "ghi_w_m2",
        "actual_power_kw",
        "expected_power_kw",
        "residual_kw",
        "energy_kwh_net",
    }
    for row in rows:
        for column in numeric_columns:
            row[column] = float(row[column])
    return rows
