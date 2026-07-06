# Energy Interoperability MVP

MVP en Python para interoperabilidad de datos energéticos: ingesta de clima, mercado, simulación y operación; normalización canónica; validación de calidad; cálculo de KPIs; persistencia en Parquet/DuckDB; y API interna FastAPI.

## Inicio rápido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python examples/run_sam_pipeline.py
uvicorn energy_interop.api.main:app --reload
```

## Alcance MVP

1. Conectores base extensibles.
2. Conector conceptual XM/Sinergox/SIMEM sin endpoints hardcodeados.
3. Conector SAM CSV ejecutable para archivos locales.
4. Normalización temporal UTC/local.
5. Validación con Pandera.
6. KPI simple y escritura Parquet.

La arquitectura completa, roadmap, modelo canónico, backlog y decisiones técnicas están en [`docs/architecture.md`](docs/architecture.md).
