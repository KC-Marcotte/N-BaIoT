#!/usr/bin/env python3
"""Generate offline static visualizations for the N-BaIoT EDA report.

The visualizations intentionally consume the per-file aggregate metrics from
``eda_summary.json``. They do not load the multi-gigabyte CSV collection and
therefore remain fast, deterministic, and suitable for a local/offline report.
"""

import json
import os
import sys
from typing import Any, Dict, Iterable, List


TRAFFIC_FAMILIES = ["benign", "gafgyt", "mirai"]
FAMILY_COLORS = {
    "benign": "#2a9d8f",
    "gafgyt": "#e9c46a",
    "mirai": "#e76f51",
}


def _load_matplotlib():
    """Load Matplotlib lazily so report aggregation remains usable without it."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import LogNorm

        return plt, LogNorm
    except ImportError as exc:
        raise ImportError(
            "Matplotlib is required for static EDA figures. Install it with "
            "`pip install matplotlib`."
        ) from exc


def _save(fig: Any, path: str) -> None:
    fig.savefig(path, dpi=150, bbox_inches="tight")
    fig.clf()


def _datasets_frame(metrics: Iterable[Any]) -> List[Dict[str, Any]]:
    return [
        {
            "device_name": item.device_name,
            "device_category": item.device_category,
            "attack_family": item.attack_family,
            "attack_name": item.attack_name,
            "row_count": item.row_count,
            "file_size_mb": item.file_size_mb,
            "selected_feature_means": item.selected_feature_means,
        }
        for item in metrics
    ]


def _plot_class_distribution(summary: Dict[str, Any], path: str) -> None:
    plt, _ = _load_matplotlib()
    devices = sorted(summary["device_summary"])
    fig, ax = plt.subplots(figsize=(12, max(5, len(devices) * 0.45)))
    left = [0] * len(devices)
    for family in TRAFFIC_FAMILIES:
        values = [summary["device_summary"][d]["family_counts"][family] for d in devices]
        ax.barh(devices, values, left=left, label=family.upper(), color=FAMILY_COLORS[family])
        left = [a + b for a, b in zip(left, values)]
    ax.set_title("Traffic records by device and class")
    ax.set_xlabel("Records")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    _save(fig, path)


def _plot_class_balance(summary: Dict[str, Any], path: str) -> None:
    plt, _ = _load_matplotlib()
    devices = sorted(summary["device_summary"])
    fig, ax = plt.subplots(figsize=(12, max(5, len(devices) * 0.45)))
    left = [0.0] * len(devices)
    for family in TRAFFIC_FAMILIES:
        values = [summary["device_summary"][d]["family_percentages"][family] for d in devices]
        ax.barh(devices, values, left=left, label=family.upper(), color=FAMILY_COLORS[family])
        left = [a + b for a, b in zip(left, values)]
    ax.set_xlim(0, 100)
    ax.set_title("Traffic class balance by device")
    ax.set_xlabel("Share of device records (%)")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    _save(fig, path)


def _plot_attack_vectors(summary: Dict[str, Any], path: str) -> None:
    plt, _ = _load_matplotlib()
    items = sorted(
        summary["attack_vectors"].items(),
        key=lambda pair: pair[1]["record_count"],
    )
    labels = [key for key, _ in items]
    values = [item["record_count"] for _, item in items]
    colors = [FAMILY_COLORS[item["attack_family"]] for _, item in items]
    fig, ax = plt.subplots(figsize=(10, max(5, len(labels) * 0.35)))
    ax.barh(labels, values, color=colors)
    ax.set_title("Attack-vector record distribution")
    ax.set_xlabel("Records")
    ax.grid(axis="x", alpha=0.25)
    _save(fig, path)


def _plot_coverage(summary: Dict[str, Any], path: str) -> None:
    plt, _ = _load_matplotlib()
    devices = sorted(summary["device_class_coverage"])
    fig, ax = plt.subplots(figsize=(7, max(5, len(devices) * 0.45)))
    values = [
        [1 if summary["device_class_coverage"][device][family] else 0 for family in TRAFFIC_FAMILIES]
        for device in devices
    ]
    image = ax.imshow(values, cmap="YlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(TRAFFIC_FAMILIES)), [family.upper() for family in TRAFFIC_FAMILIES])
    ax.set_yticks(range(len(devices)), devices)
    ax.set_title("Device/class coverage")
    for row_index, row in enumerate(values):
        for col_index, value in enumerate(row):
            ax.text(col_index, row_index, "Yes" if value else "No", ha="center", va="center")
    fig.colorbar(image, ax=ax, ticks=[0, 1], label="Class present")
    _save(fig, path)


def _plot_category_composition(summary: Dict[str, Any], path: str) -> None:
    plt, _ = _load_matplotlib()
    categories = sorted(summary["category_summary"])
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bottom = [0] * len(categories)
    for family in TRAFFIC_FAMILIES:
        values = [summary["category_summary"][c]["family_counts"][family] for c in categories]
        ax.bar(categories, values, bottom=bottom, label=family.upper(), color=FAMILY_COLORS[family])
        bottom = [a + b for a, b in zip(bottom, values)]
    ax.set_title("Traffic composition by device category")
    ax.set_ylabel("Records")
    ax.tick_params(axis="x", rotation=25)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, path)


def _plot_dataset_sizes(metrics: Iterable[Any], path: str) -> None:
    plt, _ = _load_matplotlib()
    rows = sorted(_datasets_frame(metrics), key=lambda row: row["row_count"])
    labels = [f"{row['device_name']} / {row['attack_family']}/{row['attack_name']}" for row in rows]
    values = [row["row_count"] for row in rows]
    colors = [FAMILY_COLORS.get(row["attack_family"], "#457b9d") for row in rows]
    fig, ax = plt.subplots(figsize=(12, max(6, len(labels) * 0.18)))
    ax.barh(labels, values, color=colors)
    ax.set_xscale("log")
    ax.set_title("CSV dataset record counts")
    ax.set_xlabel("Records (log scale)")
    ax.grid(axis="x", alpha=0.25)
    _save(fig, path)


def _plot_feature_heatmap(summary: Dict[str, Any], path: str) -> None:
    plt, LogNorm = _load_matplotlib()
    families = [family for family in TRAFFIC_FAMILIES if family in summary["feature_profiles"]]
    features = list(next(iter(summary["feature_profiles"].values())).keys()) if families else []
    matrix = [
        [summary["feature_profiles"][family][feature]["mean"] for feature in features]
        for family in families
    ]
    fig, ax = plt.subplots(figsize=(14, max(3.5, len(families) * 1.1)))
    positive_values = [value for row in matrix for value in row if value > 0]
    if positive_values:
        image = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", norm=LogNorm(vmin=min(positive_values), vmax=max(positive_values)))
    else:
        image = ax.imshow(matrix, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(features)), features, rotation=45, ha="right")
    ax.set_yticks(range(len(families)), [family.upper() for family in families])
    ax.set_title("Selected feature means by traffic class")
    fig.colorbar(image, ax=ax, label="Mean value")
    _save(fig, path)


def generate_visualizations(summary: Dict[str, Any], metrics: Iterable[Any], output_dir: str) -> List[str]:
    """Generate the aggregate figure set and return the created paths."""
    os.makedirs(output_dir, exist_ok=True)
    metric_list = list(metrics)
    plots = [
        (_plot_class_distribution, "01_class_distribution_by_device.png"),
        (_plot_class_balance, "02_class_balance_percent_by_device.png"),
        (_plot_attack_vectors, "03_attack_vector_distribution.png"),
        (_plot_coverage, "04_device_class_heatmap.png"),
        (_plot_category_composition, "05_category_composition.png"),
        (lambda _summary, path: _plot_dataset_sizes(metric_list, path), "06_dataset_size_distribution.png"),
        (_plot_feature_heatmap, "07_feature_mean_heatmap.png"),
    ]
    created = []
    for plotter, filename in plots:
        path = os.path.join(output_dir, filename)
        plotter(summary, path)
        created.append(path)
    return created


def main() -> None:
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    summary_path = os.path.join(workspace_root, "reports", "eda_summary.json")
    figures_dir = os.path.join(workspace_root, "reports", "figures")
    with open(summary_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    # Standalone regeneration uses lightweight objects with the attributes
    # required by the dataset-size chart.
    from types import SimpleNamespace

    metrics = [SimpleNamespace(**item) for item in payload.get("datasets", [])]
    generate_visualizations(payload["summary"], metrics, figures_dir)
    print(f"Saved visualizations to {figures_dir}")


if __name__ == "__main__":
    main()