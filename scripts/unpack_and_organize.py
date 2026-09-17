#!/usr/bin/env python3
"""
N-BaIoT Dataset Unpack and Organization Pipeline.
Scaffolds dataset hierarchy by device type:
  data/<device_type>/<device_name>/<benign|gafgyt|mirai>/*.csv
Handles unpacking of .rar archives with tar.exe (libarchive),
header validation against demonstrate_structure.csv, and RAR cleanup.
"""

import os
import sys
import glob
import shutil
import subprocess
from typing import Dict, List

# Device category mapping
DEVICE_CATEGORY_MAP = {
    "Danmini_Doorbell": "doorbells",
    "Ennio_Doorbell": "doorbells",
    "Ecobee_Thermostat": "thermostats",
    "Philips_B120N10_Baby_Monitor": "baby_monitors",
    "Provision_PT_737E_Security_Camera": "security_cameras",
    "Provision_PT_838_Security_Camera": "security_cameras",
    "Samsung_SNH_1011_N_Webcam": "security_cameras",
    "SimpleHome_XCS7_1002_WHT_Security_Camera": "security_cameras",
    "SimpleHome_XCS7_1003_WHT_Security_Camera": "security_cameras",
}

EXPECTED_ATTACK_FILES = {
    "gafgyt": ["combo.csv", "junk.csv", "scan.csv", "tcp.csv", "udp.csv"],
    "mirai": ["ack.csv", "scan.csv", "syn.csv", "udp.csv", "udpplain.csv"],
}


def get_expected_header(root_dir: str) -> List[str]:
    demo_path = os.path.join(root_dir, "demonstrate_structure.csv")
    if os.path.exists(demo_path):
        with open(demo_path, "r", encoding="utf-8") as f:
            header_line = f.readline().strip()
            return [col.strip() for col in header_line.split(",") if col.strip()]
    return []


def verify_csv_header(csv_path: str, expected_header: List[str]) -> bool:
    if not os.path.exists(csv_path):
        return False
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        header_line = f.readline().strip()
        cols = [col.strip() for col in header_line.split(",") if col.strip()]
        if len(cols) != len(expected_header):
            print(f"[WARN] Header length mismatch in {csv_path}: {len(cols)} vs {len(expected_header)}")
            return False
        return True


def unpack_rar_to_dir(rar_path: str, dest_dir: str) -> bool:
    os.makedirs(dest_dir, exist_ok=True)
    cmd = ["tar", "-xf", rar_path, "-C", dest_dir]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to extract {rar_path}: {e.stderr}")
        return False


def process_dataset(root_dir: str, target_base_dir: str, remove_rar: bool = True):
    print(f"Starting N-BaIoT Organization Pipeline...")
    expected_header = get_expected_header(root_dir)
    print(f"Loaded {len(expected_header)} expected feature columns.")

    devices = [
        d for d in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, d))
        and d in DEVICE_CATEGORY_MAP
    ]

    total_extracted = 0
    total_files_verified = 0

    for device in sorted(devices):
        category = DEVICE_CATEGORY_MAP[device]
        src_device_dir = os.path.join(root_dir, device)
        dest_device_dir = os.path.join(target_base_dir, category, device)

        print(f"\nProcessing [{category.upper()}] -> {device}")
        os.makedirs(dest_device_dir, exist_ok=True)

        # 1. Handle benign traffic
        src_benign = os.path.join(src_device_dir, "benign_traffic.csv")
        dest_benign_dir = os.path.join(dest_device_dir, "benign")
        dest_benign_file = os.path.join(dest_benign_dir, "benign_traffic.csv")
        os.makedirs(dest_benign_dir, exist_ok=True)

        if os.path.exists(src_benign):
            if not os.path.exists(dest_benign_file):
                print(f"  Copying benign_traffic.csv -> {dest_benign_dir}")
                shutil.copy2(src_benign, dest_benign_file)
                try:
                    os.remove(src_benign)
                except Exception as e:
                    print(f"  [WARN] Could not remove source {src_benign}: {e}")
            else:
                try:
                    os.remove(src_benign)
                except Exception:
                    pass
            if verify_csv_header(dest_benign_file, expected_header):
                total_files_verified += 1

        # 2. Handle GAFGYT attacks
        gafgyt_rar = os.path.join(src_device_dir, "gafgyt_attacks.rar")
        dest_gafgyt_dir = os.path.join(dest_device_dir, "gafgyt")
        os.makedirs(dest_gafgyt_dir, exist_ok=True)

        src_gafgyt_sub = os.path.join(src_device_dir, "gafgyt_attacks")
        if os.path.exists(src_gafgyt_sub) and os.path.isdir(src_gafgyt_sub):
            for f in os.listdir(src_gafgyt_sub):
                if f.endswith(".csv"):
                    shutil.move(os.path.join(src_gafgyt_sub, f), os.path.join(dest_gafgyt_dir, f))
            shutil.rmtree(src_gafgyt_sub, ignore_errors=True)

        if os.path.exists(gafgyt_rar):
            print(f"  Unpacking {gafgyt_rar} -> {dest_gafgyt_dir}")
            if unpack_rar_to_dir(gafgyt_rar, dest_gafgyt_dir):
                total_extracted += 1
                if remove_rar:
                    os.remove(gafgyt_rar)

        for expected_f in EXPECTED_ATTACK_FILES["gafgyt"]:
            fpath = os.path.join(dest_gafgyt_dir, expected_f)
            if verify_csv_header(fpath, expected_header):
                total_files_verified += 1

        # 3. Handle Mirai attacks (if applicable)
        mirai_rar = os.path.join(src_device_dir, "mirai_attacks.rar")
        dest_mirai_dir = os.path.join(dest_device_dir, "mirai")
        os.makedirs(dest_mirai_dir, exist_ok=True)

        src_mirai_sub = os.path.join(src_device_dir, "mirai_attacks")
        if os.path.exists(src_mirai_sub) and os.path.isdir(src_mirai_sub):
            for f in os.listdir(src_mirai_sub):
                if f.endswith(".csv"):
                    shutil.move(os.path.join(src_mirai_sub, f), os.path.join(dest_mirai_dir, f))
            shutil.rmtree(src_mirai_sub, ignore_errors=True)

        if os.path.exists(mirai_rar):
            print(f"  Unpacking {mirai_rar} -> {dest_mirai_dir}")
            if unpack_rar_to_dir(mirai_rar, dest_mirai_dir):
                total_extracted += 1
                if remove_rar:
                    os.remove(mirai_rar)

        if os.path.exists(dest_mirai_dir) and os.listdir(dest_mirai_dir):
            for expected_f in EXPECTED_ATTACK_FILES["mirai"]:
                fpath = os.path.join(dest_mirai_dir, expected_f)
                if verify_csv_header(fpath, expected_header):
                    total_files_verified += 1
        elif os.path.exists(dest_mirai_dir) and len(os.listdir(dest_mirai_dir)) == 0:
            os.rmdir(dest_mirai_dir)

        if os.path.exists(src_device_dir) and src_device_dir != dest_device_dir:
            remaining = os.listdir(src_device_dir)
            if not remaining:
                os.rmdir(src_device_dir)
            else:
                print(f"  [INFO] Remaining items in source dir {src_device_dir}: {remaining}")

    print("\n" + "=" * 60)
    print(f"Pipeline Completed!")
    print(f"Total RAR archives extracted: {total_extracted}")
    print(f"Total CSV datasets verified: {total_files_verified}")
    print("=" * 60)


if __name__ == "__main__":
    root_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_data_dir = os.path.join(root_workspace, "data")
    process_dataset(root_workspace, target_data_dir, remove_rar=True)
