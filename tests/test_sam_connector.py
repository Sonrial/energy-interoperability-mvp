from pathlib import Path

import pandas as pd

from energy_interop.connectors.base import ConnectorContext
from energy_interop.connectors.sam_csv import SamCsvConnector


def test_sam_connector_normalizes_and_validates(tmp_path: Path):
    csv_path = tmp_path / "sam.csv"
    pd.DataFrame({"timestamp": ["2026-01-01 12:00"], "GHI": [850]}).to_csv(csv_path, index=False)
    connector = SamCsvConnector(
        ConnectorContext(source="sam_csv", asset_id="asset_1", timezone="America/Bogota"), csv_path
    )
    frame = connector.validate(connector.normalize_time(connector.normalize_schema(connector.parse(connector.fetch_raw()))))
    assert frame.loc[0, "asset_id"] == "asset_1"
    assert frame.loc[0, "unit"] == "W/m2"
