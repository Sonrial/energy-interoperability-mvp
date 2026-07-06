# Energy Interoperability MVP

MVP en Python para interoperabilidad de datos energéticos: ingesta de clima, mercado, simulación y operación; normalización canónica; validación de calidad; cálculo de KPIs; persistencia en Parquet/DuckDB; y API interna FastAPI.

## Revisión rápida sin dependencias externas

Este repositorio incluye una ejecución de ejemplo que usa únicamente la librería estándar de Python para que el resultado pueda revisarse incluso en entornos sin acceso a PyPI:

```bash
python examples/run_sample_without_dependencies.py
```

Entrada de ejemplo:

- `examples/sample_data/sam_weather_sample.csv`

Salidas generadas y versionadas para revisión:

- `examples/sample_output/canonical_measurements.csv`
- `examples/sample_output/kpi_summary.json`

La salida canónica muestra timestamps locales `America/Bogota`, timestamps UTC, GHI, potencia real, potencia esperada, residual, energía neta y flags de calidad. El resumen KPI agrega energía neta, energía esperada, residual medio y conteo de flags.

## Inicio rápido con stack completo

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
