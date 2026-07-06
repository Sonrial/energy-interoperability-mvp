from __future__ import annotations

from pathlib import Path

import pandas as pd

from energy_interop.connectors.base import ConnectorContext, DataConnector
from energy_interop.transformations.time import attach_local_and_utc
from energy_interop.validation.schemas import OperationalMeasurementSchema


class SamCsvConnector(DataConnector):
    def __init__(self, context: ConnectorContext, file_path: Path) -> None:
        super().__init__(context)
        self.file_path = file_path

    def fetch_raw(self) -> Path:
        if not self.file_path.exists():
            raise FileNotFoundError(self.file_path)
        return self.file_path

    def parse(self, raw: bytes | str | Path) -> pd.DataFrame:
        path = Path(raw)
        # SAM weather CSV normally has metadata rows followed by headers. For the MVP we support
        # a normalized CSV fixture and keep this parser replaceable for full SAM variants.
        return pd.read_csv(path)

    def normalize_schema(self, frame: pd.DataFrame) -> pd.DataFrame:
        column_map = {"Timestamp": "timestamp", "timestamp": "timestamp", "GHI": "ghi_w_m2", "ghi": "ghi_w_m2"}
        normalized = frame.rename(columns={k: v for k, v in column_map.items() if k in frame.columns}).copy()
        if "ghi_w_m2" not in normalized.columns:
            raise ValueError("SAM CSV requires a GHI/ghi column for this MVP connector")
        return pd.DataFrame(
            {
                "asset_id": self.context.asset_id or "unknown_asset",
                "source": self.context.source,
                "timestamp": normalized["timestamp"],
                "variable": "ghi",
                "value": normalized["ghi_w_m2"].astype(float),
                "unit": "W/m2",
            }
        )

    def normalize_time(self, frame: pd.DataFrame) -> pd.DataFrame:
        return attach_local_and_utc(frame, "timestamp", self.context.timezone, self.context.timezone)

    def validate(self, frame: pd.DataFrame) -> pd.DataFrame:
        validated = OperationalMeasurementSchema.validate(frame)
        invalid = validated[validated["value"] < 0]
        if not invalid.empty:
            raise ValueError("GHI cannot be negative")
        return validated
