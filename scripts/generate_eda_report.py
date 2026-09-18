#!/usr/bin/env python3
"""
N-BaIoT Exploratory Data Analysis & Statistical Report Generator.
Follows pandas & numpy streaming best practices for large dataset processing:
- Memory-efficient chunked CSV streaming (chunksize=25000)
- Online running moments (for mean, variance, std)
- Approximate sample quantiles
- Generates reports/eda_report.md and reports/eda_summary.json
"""

import os
import sys
import json
import time
import glob
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


@dataclass
class DatasetMetrics:
    file_path: str
    device_category: str
    device_name: str
    attack_family: str
    attack_name: str
    row_count: int
    column_count: int
    file_size_mb: float
    null_count: int
    selected_feature_counts: Dict[str, int] = field(default_factory=dict)
    selected_feature_means: Dict[str, float] = field(default_factory=dict)
    selected_feature_stds: Dict[str, float] = field(default_factory=dict)
    selected_feature_q25: Dict[str, float] = field(default_factory=dict)
    selected_feature_median: Dict[str, float] = field(default_factory=dict)
    selected_feature_q75: Dict[str, float] = field(default_factory=dict)


KEY_FEATURES = [
    "MI_dir_L5_weight",
    "MI_dir_L5_mean",
    "MI_dir_L0.1_weight",
    "H_L5_weight",
    "H_L5_mean",
    "HH_L5_magnitude",
    "HH_jit_L5_mean",
    "HpHp_L5_magnitude",
]


def analyze_single_csv(csv_path: str, chunksize: int = 25000, workspace_root: str = "") -> DatasetMetrics:
    parts = os.path.normpath(csv_path).split(os.sep)
    try:
        data_idx = parts.index("data")
        category = parts[data_idx + 1]
        device = parts[data_idx + 2]
        family = parts[data_idx + 3]
    except Exception:
        category, device, family = "unknown", "unknown", "unknown"
    attack_name = os.path.splitext(os.path.basename(csv_path))[0]

    file_size_mb = os.path.getsize(csv_path) / (1024 * 1024)

    total_rows = 0
    total_nulls = 0
    col_count = 0

    sample_pool = {feat: [] for feat in KEY_FEATURES}
    feature_sums = {feat: 0.0 for feat in KEY_FEATURES}
    feature_sq_sums = {feat: 0.0 for feat in KEY_FEATURES}
    feature_counts = {feat: 0 for feat in KEY_FEATURES}

    for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=False):
        if col_count == 0:
            col_count = chunk.shape[1]
        chunk_rows = len(chunk)
        total_rows += chunk_rows
        total_nulls += int(chunk.isnull().sum().sum())

        for feat in KEY_FEATURES:
            if feat in chunk.columns:
                series = chunk[feat].dropna().to_numpy()
                cnt = len(series)
                if cnt > 0:
                    feature_counts[feat] += cnt
                    feature_sums[feat] += float(np.sum(series))
                    feature_sq_sums[feat] += float(np.sum(series ** 2))
                    if len(sample_pool[feat]) < 2000:
                        sample_pool[feat].extend(series[: min(cnt, 2000 - len(sample_pool[feat]))])

    means = {}
    stds = {}
    q25s = {}
    medians = {}
    q75s = {}

    for feat in KEY_FEATURES:
        n = feature_counts[feat]
        if n > 0:
            m = feature_sums[feat] / n
            var = max(0.0, (feature_sq_sums[feat] / n) - (m ** 2))
            means[feat] = round(m, 4)
            stds[feat] = round(float(np.sqrt(var)), 4)
        else:
            means[feat] = 0.0
            stds[feat] = 0.0

        if len(sample_pool[feat]) > 0:
            arr = np.array(sample_pool[feat])
            q25s[feat] = round(float(np.percentile(arr, 25)), 4)
            medians[feat] = round(float(np.percentile(arr, 50)), 4)
            q75s[feat] = round(float(np.percentile(arr, 75)), 4)
        else:
            q25s[feat] = 0.0
            medians[feat] = 0.0
            q75s[feat] = 0.0

    file_path = (
        os.path.relpath(csv_path, workspace_root).replace("\\", "/")
        if workspace_root
        else os.path.normpath(csv_path).replace("\\", "/")
    )

    return DatasetMetrics(
        file_path=file_path,
        device_category=category,
        device_name=device,
        attack_family=family,
        attack_name=attack_name,
        row_count=total_rows,
        column_count=col_count,
        file_size_mb=round(file_size_mb, 2),
        null_count=total_nulls,
        selected_feature_counts=feature_counts,
        selected_feature_means=means,
        selected_feature_stds=stds,
        selected_feature_q25=q25s,
        selected_feature_median=medians,
        selected_feature_q75=q75s,
    )


def generate_markdown_legacy(metrics: List[DatasetMetrics], elapsed_sec: float) -> str:
    total_files = len(metrics)
    total_records = sum(m.row_count for m in metrics)
    total_size_mb = sum(m.file_size_mb for m in metrics)
    total_nulls = sum(m.null_count for m in metrics)

    categories = sorted(list(set(m.device_category for m in metrics)))
    devices = sorted(list(set(m.device_name for m in metrics)))

    md = []
    md.append("# N-BaIoT Dataset Exploratory Data Analysis (EDA) Report\n")
    md.append(f"**Generated**: Automated Streaming Analysis Engine  ")
    md.append(f"**Total Execution Time**: {elapsed_sec:.2f} seconds  ")
    md.append(f"**Total CSV Datasets**: {total_files} files  ")
    md.append(f"**Total Network Traffic Records**: {total_records:,} packets  ")
    md.append(f"**Total Dataset Storage Volume**: {total_size_mb / 1024:.2f} GB ({total_size_mb:,.1f} MB)  ")
    md.append(f"**Feature Columns per Dataset**: 115 continuous features  ")
    md.append(f"**Dataset Cleanliness**: {total_nulls} missing/null values (100% complete)\n")

    md.append("---\n")
    md.append("## 1. Executive Summary & Taxonomy\n")
    md.append("The N-BaIoT dataset captures real-world network traffic from 9 commercial IoT devices across 4 hardware categories infected with two botnets (**Mirai** and **BASHLITE / GAFGYT**).\n")

    md.append("### Summary by Device Category\n")
    md.append("| Category | Devices | Total CSVs | Total Records | Size (MB) | Benign Pkts | GAFGYT Pkts | Mirai Pkts |")
    md.append("|---|---|---|---|---|---|---|---|")

    for cat in categories:
        cat_metrics = [m for m in metrics if m.device_category == cat]
        cat_devs = len(set(m.device_name for m in cat_metrics))
        cat_csvs = len(cat_metrics)
        cat_rows = sum(m.row_count for m in cat_metrics)
        cat_size = sum(m.file_size_mb for m in cat_metrics)
        benign_pkts = sum(m.row_count for m in cat_metrics if m.attack_family == "benign")
        gafgyt_pkts = sum(m.row_count for m in cat_metrics if m.attack_family == "gafgyt")
        mirai_pkts = sum(m.row_count for m in cat_metrics if m.attack_family == "mirai")

        md.append(f"| `{cat}` | {cat_devs} | {cat_csvs} | {cat_rows:,} | {cat_size:,.1f} MB | {benign_pkts:,} | {gafgyt_pkts:,} | {mirai_pkts:,} |")

    md.append("\n---\n")
    md.append("## 2. Granular Breakdown by IoT Device\n")
    md.append("| Device Name | Category | Total CSVs | Benign Rows | GAFGYT Rows | Mirai Rows | Total Rows | Total Size (MB) |")
    md.append("|---|---|---|---|---|---|---|---|")

    for dev in devices:
        dev_m = [m for m in metrics if m.device_name == dev]
        cat = dev_m[0].device_category
        csv_count = len(dev_m)
        benign_r = sum(m.row_count for m in dev_m if m.attack_family == "benign")
        gafgyt_r = sum(m.row_count for m in dev_m if m.attack_family == "gafgyt")
        mirai_r = sum(m.row_count for m in dev_m if m.attack_family == "mirai")
        total_r = sum(m.row_count for m in dev_m)
        total_s = sum(m.file_size_mb for m in dev_m)
        md.append(f"| **{dev}** | `{cat}` | {csv_count} | {benign_r:,} | {gafgyt_r:,} | {mirai_r:,} | **{total_r:,}** | {total_s:,.1f} MB |")

    md.append("\n---\n")
    md.append("## 3. Attack Family & Vector Distribution\n")
    md.append("### Mirai Botnet Attack Vectors (5 Classes)\n")
    md.append("| Attack Vector | Description | Dataset Count | Total Packets | Avg Pkts / Attack |")
    md.append("|---|---|---|---|---|")
    mirai_attacks = ["ack", "scan", "syn", "udp", "udpplain"]
    for att in mirai_attacks:
        att_m = [m for m in metrics if m.attack_family == "mirai" and m.attack_name == att]
        p_count = sum(m.row_count for m in att_m)
        d_count = len(att_m)
        avg_p = p_count // d_count if d_count else 0
        md.append(f"| `mirai/{att}` | Mirai {att.upper()} flood/probe | {d_count} | {p_count:,} | {avg_p:,} |")

    md.append("\n### GAFGYT / BASHLITE Botnet Attack Vectors (5 Classes)\n")
    md.append("| Attack Vector | Description | Dataset Count | Total Packets | Avg Pkts / Attack |")
    md.append("|---|---|---|---|---|")
    gafgyt_attacks = ["combo", "junk", "scan", "tcp", "udp"]
    for att in gafgyt_attacks:
        att_m = [m for m in metrics if m.attack_family == "gafgyt" and m.attack_name == att]
        p_count = sum(m.row_count for m in att_m)
        d_count = len(att_m)
        avg_p = p_count // d_count if d_count else 0
        md.append(f"| `gafgyt/{att}` | GAFGYT {att.upper()} flood/anomaly | {d_count} | {p_count:,} | {avg_p:,} |")

    md.append("\n---\n")
    md.append("## 4. Key Feature Statistical Profiles (Benign vs Attacks)\n")
    md.append("Comparison of traffic dynamics using 100-packet damp window (`L5` decay factor $\\lambda=0.01$):\n\n")
    md.append("| Traffic Class | MI_dir_L5_weight (mean ± std) | MI_dir_L5_mean (pkt size) | H_L5_weight (host rate) | HH_jit_L5_mean (jitter) |")
    md.append("|---|---|---|---|---|")

    for fam in ["benign", "gafgyt", "mirai"]:
        fam_m = [m for m in metrics if m.attack_family == fam]
        if not fam_m:
            continue
        w_mean = float(np.mean([m.selected_feature_means.get("MI_dir_L5_weight", 0) for m in fam_m]))
        w_std = float(np.mean([m.selected_feature_stds.get("MI_dir_L5_weight", 0) for m in fam_m]))
        s_mean = float(np.mean([m.selected_feature_means.get("MI_dir_L5_mean", 0) for m in fam_m]))
        h_mean = float(np.mean([m.selected_feature_means.get("H_L5_weight", 0) for m in fam_m]))
        j_mean = float(np.mean([m.selected_feature_means.get("HH_jit_L5_mean", 0) for m in fam_m]))
        md.append(f"| **{fam.upper()}** | {w_mean:.2f} ± {w_std:.2f} | {s_mean:.2f} B | {h_mean:.2f} | {j_mean:.4f} |")

    md.append("\n---\n")
    md.append("## 5. Complete Dataset Catalog (All 89 Datasets)\n")
    md.append("| Device | Class | Attack | Records | Size (MB) | Mean Packet Size (MI_dir_L5_mean) |")
    md.append("|---|---|---|---|---|---|")
    for m in sorted(metrics, key=lambda x: (x.device_category, x.device_name, x.attack_family, x.attack_name)):
        pkt_sz = m.selected_feature_means.get("MI_dir_L5_mean", 0.0)
        md.append(f"| {m.device_name} | `{m.attack_family}` | `{m.attack_name}` | {m.row_count:,} | {m.file_size_mb:,.2f} MB | {pkt_sz:.2f} |")

    return "\n".join(md)


TRAFFIC_FAMILIES = ["benign", "gafgyt", "mirai"]


def _percentage(value: int, total: int) -> float:
    return round((value / total) * 100, 2) if total else 0.0


def _family_counts(metrics: List[DatasetMetrics]) -> Dict[str, int]:
    return {
        family: sum(m.row_count for m in metrics if m.attack_family == family)
        for family in TRAFFIC_FAMILIES
    }


def _feature_profile(metrics: List[DatasetMetrics], feature: str) -> Dict[str, float]:
    """Combine per-file moments using valid feature counts as weights."""
    rows = [m for m in metrics if m.selected_feature_counts.get(feature, 0) > 0]
    count = sum(m.selected_feature_counts.get(feature, 0) for m in rows)
    if not count:
        return {"count": 0, "mean": 0.0, "std": 0.0}

    mean = sum(
        m.selected_feature_means.get(feature, 0.0)
        * m.selected_feature_counts.get(feature, 0)
        for m in rows
    ) / count
    second_moment = sum(
        m.selected_feature_counts.get(feature, 0)
        * (
            m.selected_feature_stds.get(feature, 0.0) ** 2
            + m.selected_feature_means.get(feature, 0.0) ** 2
        )
        for m in rows
    ) / count
    variance = max(0.0, second_moment - mean**2)
    return {"count": count, "mean": round(mean, 4), "std": round(float(np.sqrt(variance)), 4)}


def summarize_metrics(metrics: List[DatasetMetrics]) -> Dict[str, Any]:
    """Build reusable aggregate data for JSON, Markdown, and visualizations."""
    total_records = sum(m.row_count for m in metrics)
    total_cells = sum(m.row_count * m.column_count for m in metrics)
    total_nulls = sum(m.null_count for m in metrics)
    family_counts = _family_counts(metrics)

    category_summary = {}
    for category in sorted({m.device_category for m in metrics}):
        group = [m for m in metrics if m.device_category == category]
        counts = _family_counts(group)
        category_summary[category] = {
            "device_count": len({m.device_name for m in group}),
            "dataset_count": len(group),
            "record_count": sum(m.row_count for m in group),
            "size_mb": round(sum(m.file_size_mb for m in group), 2),
            "family_counts": counts,
            "family_percentages": {
                family: _percentage(count, sum(counts.values()))
                for family, count in counts.items()
            },
        }

    device_summary = {}
    for device in sorted({m.device_name for m in metrics}):
        group = [m for m in metrics if m.device_name == device]
        counts = _family_counts(group)
        device_summary[device] = {
            "device_category": group[0].device_category,
            "dataset_count": len(group),
            "record_count": sum(m.row_count for m in group),
            "size_mb": round(sum(m.file_size_mb for m in group), 2),
            "family_counts": counts,
            "family_percentages": {
                family: _percentage(count, sum(counts.values()))
                for family, count in counts.items()
            },
        }

    attack_vectors = {}
    for m in metrics:
        if m.attack_family == "benign":
            continue
        key = f"{m.attack_family}/{m.attack_name}"
        item = attack_vectors.setdefault(
            key,
            {
                "attack_family": m.attack_family,
                "attack_name": m.attack_name,
                "dataset_count": 0,
                "record_count": 0,
            },
        )
        item["dataset_count"] += 1
        item["record_count"] += m.row_count
    for item in attack_vectors.values():
        item["average_records_per_dataset"] = round(
            item["record_count"] / item["dataset_count"], 2
        )
        item["family_percentage"] = _percentage(
            item["record_count"], family_counts.get(item["attack_family"], 0)
        )

    devices = sorted({m.device_name for m in metrics})
    coverage = {
        device: {
            family: any(
                m.device_name == device and m.attack_family == family
                for m in metrics
            )
            for family in TRAFFIC_FAMILIES
        }
        for device in devices
    }

    column_counts = sorted({m.column_count for m in metrics})
    return {
        "total_datasets": len(metrics),
        "total_records": total_records,
        "total_size_mb": round(sum(m.file_size_mb for m in metrics), 2),
        "total_nulls": total_nulls,
        "total_cells": total_cells,
        "completeness_percent": round(
            (1 - total_nulls / total_cells) * 100 if total_cells else 100.0,
            4,
        ),
        "column_counts": column_counts,
        "family_counts": family_counts,
        "family_percentages": {
            family: _percentage(count, total_records)
            for family, count in family_counts.items()
        },
        "category_summary": category_summary,
        "device_summary": device_summary,
        "device_class_coverage": coverage,
        "attack_vectors": dict(sorted(attack_vectors.items())),
        "feature_profiles": {
            family: {
                feature: _feature_profile(
                    [m for m in metrics if m.attack_family == family], feature
                )
                for feature in KEY_FEATURES
            }
            for family in TRAFFIC_FAMILIES
        },
    }


def generate_markdown(metrics: List[DatasetMetrics], elapsed_sec: float) -> str:
    summary = summarize_metrics(metrics)
    total_files = summary["total_datasets"]
    total_records = summary["total_records"]
    total_size_mb = summary["total_size_mb"]
    total_nulls = summary["total_nulls"]
    column_counts = summary["column_counts"]
    categories = sorted(summary["category_summary"])
    devices = sorted(summary["device_summary"])

    if len(column_counts) == 1:
        column_text = f"{column_counts[0]} columns in every dataset"
    else:
        column_text = f"{min(column_counts)}-{max(column_counts)} columns across datasets"

    md = [
        "# N-BaIoT Dataset Exploratory Data Analysis (EDA) Report\n",
        "**Generated**: Automated Streaming Analysis Engine",
        f"**Total Execution Time**: {elapsed_sec:.2f} seconds",
        f"**Total CSV Datasets**: {total_files} files",
        f"**Total Network Traffic Records**: {total_records:,} packets",
        f"**Total Dataset Storage Volume**: {total_size_mb / 1024:.2f} GB ({total_size_mb:,.1f} MB)",
        f"**Feature Schema**: {column_text}",
        f"**Dataset Completeness**: {summary['completeness_percent']:.2f}% ({total_nulls:,} missing/null cells)\n",
        "---\n",
        "## 1. Executive Summary & Taxonomy\n",
        f"The dataset contains **{len(devices)} IoT devices** across **{len(categories)} device categories** and **{total_files} CSV datasets**. It contains benign traffic plus two botnet families: **Mirai** and **BASHLITE / GAFGYT**.\n",
        "| Traffic Class | Records | Share of Records |",
        "|---|---:|---:|",
    ]
    for family in TRAFFIC_FAMILIES:
        md.append(
            f"| **{family.upper()}** | {summary['family_counts'][family]:,} | {summary['family_percentages'][family]:.2f}% |"
        )
    md.extend(
        [
            "",
            "![Class distribution by device](figures/01_class_distribution_by_device.png)",
            "",
            "---\n",
            "## 2. Summary by Device Category\n",
            "| Category | Devices | CSVs | Records | Size (MB) | Benign | GAFGYT | Mirai |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for category in categories:
        item = summary["category_summary"][category]
        counts = item["family_counts"]
        md.append(
            f"| `{category}` | {item['device_count']} | {item['dataset_count']} | {item['record_count']:,} | {item['size_mb']:,.1f} | {counts['benign']:,} | {counts['gafgyt']:,} | {counts['mirai']:,} |"
        )
    md.extend(
        [
            "",
            "![Category composition](figures/05_category_composition.png)",
            "",
            "---\n",
            "## 3. Device Coverage and Class Balance\n",
            "A missing class/device combination can affect how well a model generalizes beyond the observed devices.\n",
            "| Device | Category | CSVs | Benign | GAFGYT | Mirai | Total Records |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for device in devices:
        item = summary["device_summary"][device]
        counts = item["family_counts"]
        md.append(
            f"| **{device}** | `{item['device_category']}` | {item['dataset_count']} | {counts['benign']:,} | {counts['gafgyt']:,} | {counts['mirai']:,} | **{item['record_count']:,}** |"
        )
    md.extend(
        [
            "",
            "### Device/Class Coverage Matrix\n",
            "| Device | Benign | GAFGYT | Mirai |",
            "|---|---:|---:|---:|",
        ]
    )
    for device in devices:
        coverage = summary["device_class_coverage"][device]
        md.append(
            f"| {device} | {'Yes' if coverage['benign'] else 'No'} | {'Yes' if coverage['gafgyt'] else 'No'} | {'Yes' if coverage['mirai'] else 'No'} |"
        )
    md.extend(
        [
            "",
            "![Class balance by device](figures/02_class_balance_percent_by_device.png)",
            "",
            "![Device/class coverage heatmap](figures/04_device_class_heatmap.png)",
            "",
            "---\n",
            "## 4. Attack Family and Vector Distribution\n",
            "| Attack Vector | Datasets | Records | Share Within Family | Avg Records/Dataset |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for key, item in summary["attack_vectors"].items():
        md.append(
            f"| `{key}` | {item['dataset_count']} | {item['record_count']:,} | {item['family_percentage']:.2f}% | {item['average_records_per_dataset']:,.2f} |"
        )
    md.extend(
        [
            "",
            "![Attack-vector distribution](figures/03_attack_vector_distribution.png)",
            "",
            "---\n",
            "## 5. Key Feature Statistical Profiles\n",
            "Profiles are combined using valid-value counts, rather than giving every CSV equal weight. Quantiles in the per-dataset catalog are estimated from bounded samples.\n",
            "| Traffic Class | MI_dir_L5_weight (mean +/- std) | MI_dir_L5_mean | H_L5_weight | HH_jit_L5_mean |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for family in TRAFFIC_FAMILIES:
        profiles = summary["feature_profiles"][family]
        weight = profiles["MI_dir_L5_weight"]
        md.append(
            f"| **{family.upper()}** | {weight['mean']:.2f} +/- {weight['std']:.2f} | {profiles['MI_dir_L5_mean']['mean']:.2f} | {profiles['H_L5_weight']['mean']:.2f} | {profiles['HH_jit_L5_mean']['mean']:.4f} |"
        )
    md.extend(
        [
            "",
            "![Feature mean heatmap](figures/07_feature_mean_heatmap.png)",
            "",
            "---\n",
            "## 6. Data Quality and Dataset Size\n",
            f"- Missing/null cells: **{total_nulls:,}**\n",
            f"- Estimated completeness: **{summary['completeness_percent']:.2f}%**\n",
            f"- Observed column counts: **{', '.join(str(value) for value in column_counts)}**\n",
            "- Visualizations use per-file aggregates from `eda_summary.json`; packet-level boxplots and PCA require a separate row-sampling phase.\n",
            "![Dataset size distribution](figures/06_dataset_size_distribution.png)",
            "",
            "---\n",
            f"## 7. Complete Dataset Catalog ({total_files} Datasets)\n",
            "| Device | Class | Attack | Records | Size (MB) | Mean Packet Size (MI_dir_L5_mean) |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for m in sorted(
        metrics,
        key=lambda x: (x.device_category, x.device_name, x.attack_family, x.attack_name),
    ):
        pkt_sz = m.selected_feature_means.get("MI_dir_L5_mean", 0.0)
        md.append(
            f"| {m.device_name} | `{m.attack_family}` | `{m.attack_name}` | {m.row_count:,} | {m.file_size_mb:,.2f} | {pkt_sz:.2f} |"
        )

    return "\n".join(md)


def run_eda_pipeline():
    start_time = time.time()
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(workspace_root, "data")
    reports_dir = os.path.join(workspace_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
    csv_files = [f for f in csv_files if not os.path.basename(f).startswith(".")]

    print(f"Discovered {len(csv_files)} datasets across data directory.")
    metrics_list: List[DatasetMetrics] = []

    for i, csv_path in enumerate(sorted(csv_files), 1):
        rel_path = os.path.relpath(csv_path, workspace_root)
        print(f"[{i:02d}/{len(csv_files)}] Processing {rel_path}...", end="", flush=True)
        m = analyze_single_csv(csv_path, workspace_root=workspace_root)
        metrics_list.append(m)
        print(f" Done ({m.row_count:,} rows, {m.file_size_mb:.1f} MB)")

    elapsed = time.time() - start_time
    summary = summarize_metrics(metrics_list)

    # Generate static figures from the aggregate JSON data. This keeps the
    # visualization step separate from the large CSV scan and works offline.
    try:
        from generate_eda_visuals import generate_visualizations

        figures_dir = os.path.join(reports_dir, "figures")
        generate_visualizations(summary, metrics_list, figures_dir)
        print(f"Saved static visualizations to {figures_dir}")
    except ImportError as exc:
        print(f"[WARN] Static visualizations skipped: {exc}")

    # Generate Markdown Report
    md_content = generate_markdown(metrics_list, elapsed)
    md_output_path = os.path.join(reports_dir, "eda_report.md")
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"\nSaved markdown report to {md_output_path}")

    # Generate JSON Summary
    json_output_path = os.path.join(reports_dir, "eda_summary.json")
    summary_data = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time_seconds": round(elapsed, 2),
        "total_datasets": len(metrics_list),
        "total_records": sum(m.row_count for m in metrics_list),
        "total_size_mb": round(sum(m.file_size_mb for m in metrics_list), 2),
        "summary": summary,
        "datasets": [asdict(m) for m in metrics_list],
    }
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved JSON summary to {json_output_path}")
    print(f"\nPipeline finished in {elapsed:.2f}s!")


if __name__ == "__main__":
    run_eda_pipeline()
