# N-BaIoT

Tools and notes for working with the N-BaIoT IoT botnet dataset.

The raw dataset is not included in Git because it is large. Put it in `data/` before running the tests or reports.

## Setup

```bash
pip install pandas numpy pytest
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

## Folders

- `data/` — local dataset files, not tracked
- `docs/` — paper and dataset references
- `reports/` — EDA output
- `scripts/` — data and report tools
- `tests/` — dataset checks

The feature names are in [`demonstrate_structure.csv`](demonstrate_structure.csv).

Dataset paper: [N-BaIoT](docs/references/1805.03409v1%20(1).pdf).

Contributor: KC-Marcotte