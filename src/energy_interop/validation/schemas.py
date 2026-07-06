from __future__ import annotations

import pandera.pandas as pa
from pandera.typing import Series


class OperationalMeasurementSchema(pa.DataFrameModel):
    asset_id: Series[str]
    source: Series[str]
    timestamp_utc: Series[pa.DateTime]
    timestamp_local: Series[pa.DateTime]
    variable: Series[str]
    value: Series[float] = pa.Field(nullable=False)
    unit: Series[str]

    class Config:
        coerce = True
        strict = False
