from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Technology(StrEnum):
    solar_pv = "solar_pv"
    wind = "wind"
    battery = "battery"
    hydro = "hydro"


class Asset(BaseModel):
    asset_id: str
    plant_id: str
    asset_type: str
    name: str
    timezone: str = "America/Bogota"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Plant(BaseModel):
    plant_id: str
    name: str
    country: str
    timezone: str
    technology: Technology
    latitude: float | None = None
    longitude: float | None = None
    capacity_mw_ac: float | None = None
    capacity_mw_dc: float | None = None


class OperationalMeasurement(BaseModel):
    measurement_id: str
    asset_id: str
    source: str
    timestamp_utc: datetime
    timestamp_local: datetime
    variable: str
    value: float
    unit: str
    quality_flag: str = "unchecked"
    ingestion_run_id: str | None = None
