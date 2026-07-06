from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, Query

app = FastAPI(title="Energy Interoperability MVP API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/assets")
def list_assets(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)) -> dict:
    return {"items": [], "limit": limit, "offset": offset, "next_offset": None}


@app.get("/assets/{asset_id}/operational-measurements")
def operational_measurements(asset_id: str, start: datetime, end: datetime, limit: int = Query(1000, le=10000)) -> dict:
    return {"asset_id": asset_id, "start": start, "end": end, "items": [], "limit": limit}
