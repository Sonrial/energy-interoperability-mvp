from pathlib import Path
import logging

import pandas as pd

from energy_interop.analytics.kpis import simple_expected_power_pv
from energy_interop.connectors.base import ConnectorContext
from energy_interop.connectors.sam_csv import SamCsvConnector

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sam_pipeline")


def run(input_path: Path, output_path: Path) -> Path:
    context = ConnectorContext(source="sam_csv", plant_id="plant_demo", asset_id="pv_demo", timezone="America/Bogota")
    connector = SamCsvConnector(context, input_path)
    raw = connector.fetch_raw()
    parsed = connector.parse(raw)
    canonical = connector.normalize_schema(parsed)
    canonical = connector.normalize_time(canonical)
    canonical = connector.validate(canonical)
    canonical["expected_power_kw"] = simple_expected_power_pv(canonical["value"], capacity_kw_ac=1000)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_parquet(output_path, index=False)
    log.info("wrote_parquet", extra={"path": str(output_path), "rows": len(canonical)})
    return output_path


if __name__ == "__main__":
    sample = Path("data/sample_sam.csv")
    sample.parent.mkdir(exist_ok=True)
    if not sample.exists():
        pd.DataFrame({"timestamp": ["2026-01-01 12:00", "2026-01-01 13:00"], "GHI": [800, 900]}).to_csv(sample, index=False)
    run(sample, Path("data/gold/sample_sam.parquet"))
