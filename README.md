# N-BaIoT

Tools and notes for working with the N-BaIoT IoT botnet dataset.

The raw dataset is intentionally not included in Git. Place a local copy in
`data/` before running the tests or reports.

## Setup

```bash
pip install pandas numpy matplotlib pytest
```

## Use

Run the checks:

```bash
python -m pytest -v tests
```

Build the EDA reports:

```bash
python scripts/generate_eda_report.py
```

This creates the Markdown and JSON reports plus offline PNG figures under
`reports/figures/`. To regenerate only the figures from an existing JSON
summary:

```bash
python scripts/generate_eda_visuals.py
```

## Folders

- `data/` — local dataset files, not tracked
- `docs/` — paper and dataset references
- `reports/` — EDA output, including `eda_report.md`, `eda_summary.json`, and `figures/`
- `scripts/` — data and report tools
- `tests/` — dataset checks

The feature names are in [`demonstrate_structure.csv`](demonstrate_structure.csv).

Dataset paper: [N-BaIoT](docs/references/1805.03409v1%20(1).pdf).

Contributor: KC-Marcotte