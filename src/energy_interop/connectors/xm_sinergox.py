from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
import pandas as pd

from energy_interop.connectors.base import ConnectorContext, DataConnector
from energy_interop.transformations.time import attach_local_and_utc


@dataclass(frozen=True)
class XmQuery:
    dataset: str
    params: dict[str, Any]


class XmSinergoxConnector(DataConnector):
    """Conceptual XM/Sinergox/SIMEM connector.

    The base URL, resource names and parameters must be configured from official XM/SIMEM
    documentation for the target dataset. This class intentionally avoids inventing endpoints.
    """

    def __init__(self, context: ConnectorContext, base_url: str, query: XmQuery, token: str | None = None) -> None:
        super().__init__(context)
        self.base_url = base_url.rstrip("/")
        self.query = query
        self.token = token

    def fetch_raw(self) -> str:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = f"{self.base_url}/{self.query.dataset}"
        with httpx.Client(timeout=30) as client:
            response = client.get(url, params=self.query.params, headers=headers)
            response.raise_for_status()
            return response.text

    def parse(self, raw: bytes | str | Any) -> pd.DataFrame:
        payload = json.loads(raw if isinstance(raw, str) else raw.decode("utf-8"))
        records = payload.get("data", payload if isinstance(payload, list) else [])
        return pd.DataFrame.from_records(records)

    def normalize_schema(self, frame: pd.DataFrame) -> pd.DataFrame:
        required = {"timestamp", "value", "variable", "unit"}
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"XM dataset mapping must provide canonical fields; missing={sorted(missing)}")
        result = frame.copy()
        result["asset_id"] = self.context.asset_id or result.get("asset_id", "market_colombia")
        result["source"] = self.context.source
        return result[["asset_id", "source", "timestamp", "variable", "value", "unit"]]

    def normalize_time(self, frame: pd.DataFrame) -> pd.DataFrame:
        return attach_local_and_utc(frame, "timestamp", self.context.timezone, self.context.timezone)
