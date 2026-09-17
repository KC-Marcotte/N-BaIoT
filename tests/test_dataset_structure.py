import os
import glob
import json
import pytest
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")

EXPECTED_CATEGORIES = {
    "baby_monitors": ["Philips_B120N10_Baby_Monitor"],
    "doorbells": ["Danmini_Doorbell", "Ennio_Doorbell"],
    "security_cameras": [
        "Provision_PT_737E_Security_Camera",
        "Provision_PT_838_Security_Camera",
        "Samsung_SNH_1011_N_Webcam",
        "SimpleHome_XCS7_1002_WHT_Security_Camera",
        "SimpleHome_XCS7_1003_WHT_Security_Camera",
    ],
    "thermostats": ["Ecobee_Thermostat"],
}


def test_device_categories_structure():
    assert os.path.isdir(DATA_DIR), "data/ directory must exist"
    present_cats = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    for cat in EXPECTED_CATEGORIES:
        assert cat in present_cats, f"Category folder '{cat}' missing from data/"
        cat_dir = os.path.join(DATA_DIR, cat)
        present_devs = [d for d in os.listdir(cat_dir) if os.path.isdir(os.path.join(cat_dir, d))]
        for dev in EXPECTED_CATEGORIES[cat]:
            assert dev in present_devs, f"Device '{dev}' missing from data/{cat}/"


def test_total_datasets_count():
    csv_files = glob.glob(os.path.join(DATA_DIR, "**", "*.csv"), recursive=True)
    csv_files = [f for f in csv_files if not os.path.basename(f).startswith(".")]
    # 7 devices * 11 files (1 benign + 5 gafgyt + 5 mirai) = 77
    # 2 devices * 6 files (1 benign + 5 gafgyt) = 12
    # Total = 89 files
    assert len(csv_files) == 89, f"Expected 89 CSV datasets, found {len(csv_files)}"


def test_csv_feature_schema():
    demo_path = os.path.join(ROOT_DIR, "demonstrate_structure.csv")
    with open(demo_path, "r", encoding="utf-8") as f:
        demo_header = [c.strip() for c in f.readline().strip().split(",") if c.strip()]
    assert len(demo_header) == 115, "Expected 115 feature columns in schema definition"

    # Sample test CSV from each category
    sample_files = [
        os.path.join(DATA_DIR, "doorbells", "Danmini_Doorbell", "benign", "benign_traffic.csv"),
        os.path.join(DATA_DIR, "thermostats", "Ecobee_Thermostat", "gafgyt", "combo.csv"),
        os.path.join(DATA_DIR, "security_cameras", "SimpleHome_XCS7_1002_WHT_Security_Camera", "mirai", "udp.csv"),
    ]
    for sample in sample_files:
        assert os.path.exists(sample), f"Sample file {sample} must exist"
        df_sample = pd.read_csv(sample, nrows=5)
        assert df_sample.shape[1] == 115, f"Expected 115 features in {sample}, got {df_sample.shape[1]}"
        assert list(df_sample.columns) == demo_header, f"Header mismatch in {sample}"


def test_whitepaper_markdown_conversion():
    paper_path = os.path.join(DOCS_DIR, "N_BaIoT_Paper_Reference.md")
    assert os.path.exists(paper_path), "N_BaIoT_Paper_Reference.md must exist in docs/"
    with open(paper_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "N-BaIoT: Network-based Detection of IoT Botnet Attacks Using Deep Autoencoders" in content
    assert len(content) > 30000, "Markdown documentation too short or incomplete"


def test_eda_reports_exist():
    report_md = os.path.join(REPORTS_DIR, "eda_report.md")
    report_json = os.path.join(REPORTS_DIR, "eda_summary.json")
    assert os.path.exists(report_md), "reports/eda_report.md must exist"
    assert os.path.exists(report_json), "reports/eda_summary.json must exist"

    with open(report_json, "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["total_datasets"] == 89
    assert summary["total_records"] == 7062606
