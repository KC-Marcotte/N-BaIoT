import os
import sys

import pytest


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from generate_eda_report import DatasetMetrics, generate_markdown, summarize_metrics


def make_metric(device, category, family, attack, rows, mean):
    features = {
        "MI_dir_L5_weight": mean,
        "MI_dir_L5_mean": mean * 10,
        "H_L5_weight": mean,
        "HH_jit_L5_mean": mean * 100,
    }
    counts = {feature: rows for feature in features}
    return DatasetMetrics(
        file_path=f"data/{category}/{device}/{family}/{attack}.csv",
        device_category=category,
        device_name=device,
        attack_family=family,
        attack_name=attack,
        row_count=rows,
        column_count=115,
        file_size_mb=1.0,
        null_count=0,
        selected_feature_counts=counts,
        selected_feature_means=features,
        selected_feature_stds={feature: 1.0 for feature in features},
        selected_feature_q25=features,
        selected_feature_median=features,
        selected_feature_q75=features,
    )


@pytest.fixture
def sample_metrics():
    return [
        make_metric("Device_A", "cameras", "benign", "benign_traffic", 100, 1),
        make_metric("Device_A", "cameras", "gafgyt", "udp", 200, 2),
        make_metric("Device_A", "cameras", "mirai", "udp", 300, 3),
        make_metric("Device_B", "doorbells", "benign", "benign_traffic", 50, 4),
        make_metric("Device_B", "doorbells", "gafgyt", "tcp", 150, 5),
    ]


def test_summary_contains_balances_and_coverage(sample_metrics):
    summary = summarize_metrics(sample_metrics)

    assert summary["total_datasets"] == 5
    assert summary["total_records"] == 800
    assert summary["family_counts"] == {"benign": 150, "gafgyt": 350, "mirai": 300}
    assert summary["family_percentages"]["mirai"] == 37.5
    assert summary["device_class_coverage"]["Device_A"]["mirai"] is True
    assert summary["device_class_coverage"]["Device_B"]["mirai"] is False
    assert summary["attack_vectors"]["mirai/udp"]["family_percentage"] == 100.0


def test_feature_profile_is_record_weighted(sample_metrics):
    summary = summarize_metrics(sample_metrics)
    profile = summary["feature_profiles"]["gafgyt"]["MI_dir_L5_weight"]

    # (2 * 200 + 5 * 150) / 350, rather than an unweighted mean of 2 and 5.
    assert profile["count"] == 350
    assert profile["mean"] == pytest.approx(3.2857, abs=0.0001)


def test_markdown_uses_dynamic_counts_and_embeds_figures(sample_metrics):
    report = generate_markdown(sample_metrics, elapsed_sec=1.25)

    assert "Complete Dataset Catalog (5 Datasets)" in report
    assert "**Feature Schema**: 115 columns in every dataset" in report
    assert "**Dataset Completeness**: 100.00%" in report
    assert "figures/04_device_class_heatmap.png" in report
    assert "100% complete" not in report


def test_generated_report_artifacts_exist():
    reports_dir = os.path.join(ROOT_DIR, "reports")
    with open(os.path.join(reports_dir, "eda_summary.json"), encoding="utf-8") as handle:
        summary = __import__("json").load(handle)

    assert summary["summary"]["total_datasets"] == 89
    assert summary["summary"]["total_records"] == 7062606
    assert summary["summary"]["completeness_percent"] == 100.0

    expected_figures = [
        "01_class_distribution_by_device.png",
        "02_class_balance_percent_by_device.png",
        "03_attack_vector_distribution.png",
        "04_device_class_heatmap.png",
        "05_category_composition.png",
        "06_dataset_size_distribution.png",
        "07_feature_mean_heatmap.png",
    ]
    for filename in expected_figures:
        figure_path = os.path.join(reports_dir, "figures", filename)
        assert os.path.exists(figure_path)
        assert os.path.getsize(figure_path) > 0