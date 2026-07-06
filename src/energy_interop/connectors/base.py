from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ConnectorContext:
    source: str
    plant_id: str | None = None
    asset_id: str | None = None
    timezone: str = "America/Bogota"
    raw_path: Path | None = None
    canonical_path: Path | None = None


class DataConnector(ABC):
    def __init__(self, context: ConnectorContext) -> None:
        self.context = context

    @abstractmethod
    def fetch_raw(self) -> bytes | str | Path:
        """Fetch raw payload from an API or local file without semantic mutation."""

    @abstractmethod
    def parse(self, raw: bytes | str | Path) -> pd.DataFrame:
        """Parse raw payload into a tabular frame preserving source columns when possible."""

    @abstractmethod
    def normalize_schema(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Map source-specific fields to canonical column names and units."""

    @abstractmethod
    def normalize_time(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Add timestamp_utc and timestamp_local columns with timezone-safe semantics."""

    def validate(self, frame: pd.DataFrame) -> pd.DataFrame:
        return frame

    def write_raw(self, raw: bytes | str | Path, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(raw, Path):
            destination.write_bytes(raw.read_bytes())
        elif isinstance(raw, bytes):
            destination.write_bytes(raw)
        else:
            destination.write_text(str(raw), encoding="utf-8")
        return destination

    def write_canonical(self, frame: pd.DataFrame, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(destination, index=False)
        return destination
