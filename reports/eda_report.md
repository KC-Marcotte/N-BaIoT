# N-BaIoT Dataset Exploratory Data Analysis (EDA) Report

**Generated**: Automated Streaming Analysis Engine  
**Total Execution Time**: 85.95 seconds  
**Total CSV Datasets**: 89 files  
**Total Network Traffic Records**: 7,062,606 packets  
**Total Dataset Storage Volume**: 7.58 GB (7,763.8 MB)  
**Feature Columns per Dataset**: 115 continuous features  
**Dataset Cleanliness**: 0 missing/null values (100% complete)

---

## 1. Executive Summary & Taxonomy

The N-BaIoT dataset captures real-world network traffic from 9 commercial IoT devices across 4 hardware categories infected with two botnets (**Mirai** and **BASHLITE / GAFGYT**).

### Summary by Device Category

| Category | Devices | Total CSVs | Total Records | Size (MB) | Benign Pkts | GAFGYT Pkts | Mirai Pkts |
|---|---|---|---|---|---|---|---|
| `baby_monitors` | 1 | 11 | 1,098,677 | 1,244.8 MB | 175,240 | 312,723 | 610,714 |
| `doorbells` | 2 | 17 | 1,373,798 | 1,461.3 MB | 88,648 | 633,050 | 652,100 |
| `security_cameras` | 5 | 50 | 3,754,255 | 4,088.5 MB | 278,931 | 1,581,869 | 1,893,455 |
| `thermostats` | 1 | 11 | 835,876 | 969.1 MB | 13,113 | 310,630 | 512,133 |

---

## 2. Granular Breakdown by IoT Device

| Device Name | Category | Total CSVs | Benign Rows | GAFGYT Rows | Mirai Rows | Total Rows | Total Size (MB) |
|---|---|---|---|---|---|---|---|
| **Danmini_Doorbell** | `doorbells` | 11 | 49,548 | 316,650 | 652,100 | **1,018,298** | 1,141.2 MB |
| **Ecobee_Thermostat** | `thermostats` | 11 | 13,113 | 310,630 | 512,133 | **835,876** | 969.1 MB |
| **Ennio_Doorbell** | `doorbells` | 6 | 39,100 | 316,400 | 0 | **355,500** | 320.1 MB |
| **Philips_B120N10_Baby_Monitor** | `baby_monitors` | 11 | 175,240 | 312,723 | 610,714 | **1,098,677** | 1,244.8 MB |
| **Provision_PT_737E_Security_Camera** | `security_cameras` | 11 | 62,154 | 330,096 | 436,010 | **828,260** | 877.0 MB |
| **Provision_PT_838_Security_Camera** | `security_cameras` | 11 | 98,514 | 309,040 | 429,337 | **836,891** | 887.5 MB |
| **Samsung_SNH_1011_N_Webcam** | `security_cameras` | 6 | 52,150 | 323,072 | 0 | **375,222** | 345.2 MB |
| **SimpleHome_XCS7_1002_WHT_Security_Camera** | `security_cameras` | 11 | 46,585 | 303,223 | 513,248 | **863,056** | 995.8 MB |
| **SimpleHome_XCS7_1003_WHT_Security_Camera** | `security_cameras` | 11 | 19,528 | 316,438 | 514,860 | **850,826** | 983.1 MB |

---

## 3. Attack Family & Vector Distribution

### Mirai Botnet Attack Vectors (5 Classes)

| Attack Vector | Description | Dataset Count | Total Packets | Avg Pkts / Attack |
|---|---|---|---|---|
| `mirai/ack` | Mirai ACK flood/probe | 7 | 643,821 | 91,974 |
| `mirai/scan` | Mirai SCAN flood/probe | 7 | 537,979 | 76,854 |
| `mirai/syn` | Mirai SYN flood/probe | 7 | 733,299 | 104,757 |
| `mirai/udp` | Mirai UDP flood/probe | 7 | 1,229,999 | 175,714 |
| `mirai/udpplain` | Mirai UDPPLAIN flood/probe | 7 | 523,304 | 74,757 |

### GAFGYT / BASHLITE Botnet Attack Vectors (5 Classes)

| Attack Vector | Description | Dataset Count | Total Packets | Avg Pkts / Attack |
|---|---|---|---|---|
| `gafgyt/combo` | GAFGYT COMBO flood/anomaly | 9 | 515,156 | 57,239 |
| `gafgyt/junk` | GAFGYT JUNK flood/anomaly | 9 | 261,789 | 29,087 |
| `gafgyt/scan` | GAFGYT SCAN flood/anomaly | 9 | 255,111 | 28,345 |
| `gafgyt/tcp` | GAFGYT TCP flood/anomaly | 9 | 859,850 | 95,538 |
| `gafgyt/udp` | GAFGYT UDP flood/anomaly | 9 | 946,366 | 105,151 |

---

## 4. Key Feature Statistical Profiles (Benign vs Attacks)

Comparison of traffic dynamics using 100-packet damp window (`L5` decay factor $\lambda=0.01$):


| Traffic Class | MI_dir_L5_weight (mean ± std) | MI_dir_L5_mean (pkt size) | H_L5_weight (host rate) | HH_jit_L5_mean (jitter) |
|---|---|---|---|---|
| **BENIGN** | 3.73 ± 6.99 | 149.09 B | 3.73 | 4244063.5979 |
| **GAFGYT** | 76.18 ± 16.07 | 69.25 B | 76.18 | 705191035.0437 |
| **MIRAI** | 111.39 ± 36.45 | 253.10 B | 111.39 | 715786123.4036 |

---

## 5. Complete Dataset Catalog (All 89 Datasets)

| Device | Class | Attack | Records | Size (MB) | Mean Packet Size (MI_dir_L5_mean) |
|---|---|---|---|---|---|
| Philips_B120N10_Baby_Monitor | `benign` | `benign_traffic` | 175,240 | 204.44 MB | 85.35 |
| Philips_B120N10_Baby_Monitor | `gafgyt` | `combo` | 58,152 | 98.66 MB | 74.48 |
| Philips_B120N10_Baby_Monitor | `gafgyt` | `junk` | 28,349 | 46.03 MB | 74.67 |
| Philips_B120N10_Baby_Monitor | `gafgyt` | `scan` | 27,859 | 35.80 MB | 76.97 |
| Philips_B120N10_Baby_Monitor | `gafgyt` | `tcp` | 92,581 | 49.70 MB | 60.16 |
| Philips_B120N10_Baby_Monitor | `gafgyt` | `udp` | 105,782 | 56.79 MB | 60.12 |
| Philips_B120N10_Baby_Monitor | `mirai` | `ack` | 91,123 | 115.28 MB | 383.25 |
| Philips_B120N10_Baby_Monitor | `mirai` | `scan` | 103,621 | 98.66 MB | 60.02 |
| Philips_B120N10_Baby_Monitor | `mirai` | `syn` | 118,128 | 151.61 MB | 69.59 |
| Philips_B120N10_Baby_Monitor | `mirai` | `udp` | 217,034 | 274.65 MB | 377.74 |
| Philips_B120N10_Baby_Monitor | `mirai` | `udpplain` | 80,808 | 113.18 MB | 329.79 |
| Danmini_Doorbell | `benign` | `benign_traffic` | 49,548 | 44.38 MB | 92.39 |
| Danmini_Doorbell | `gafgyt` | `combo` | 59,718 | 100.93 MB | 74.47 |
| Danmini_Doorbell | `gafgyt` | `junk` | 29,068 | 47.04 MB | 74.66 |
| Danmini_Doorbell | `gafgyt` | `scan` | 29,849 | 38.32 MB | 76.83 |
| Danmini_Doorbell | `gafgyt` | `tcp` | 92,141 | 49.46 MB | 60.16 |
| Danmini_Doorbell | `gafgyt` | `udp` | 105,874 | 56.84 MB | 60.12 |
| Danmini_Doorbell | `mirai` | `ack` | 102,195 | 129.22 MB | 382.80 |
| Danmini_Doorbell | `mirai` | `scan` | 107,685 | 102.53 MB | 60.02 |
| Danmini_Doorbell | `mirai` | `syn` | 122,573 | 157.01 MB | 69.53 |
| Danmini_Doorbell | `mirai` | `udp` | 237,665 | 300.70 MB | 377.53 |
| Danmini_Doorbell | `mirai` | `udpplain` | 81,982 | 114.79 MB | 329.54 |
| Ennio_Doorbell | `benign` | `benign_traffic` | 39,100 | 35.42 MB | 82.65 |
| Ennio_Doorbell | `gafgyt` | `combo` | 53,014 | 89.67 MB | 74.42 |
| Ennio_Doorbell | `gafgyt` | `junk` | 29,797 | 48.47 MB | 74.64 |
| Ennio_Doorbell | `gafgyt` | `scan` | 28,120 | 36.21 MB | 76.69 |
| Ennio_Doorbell | `gafgyt` | `tcp` | 101,536 | 54.50 MB | 60.15 |
| Ennio_Doorbell | `gafgyt` | `udp` | 103,933 | 55.80 MB | 60.13 |
| Provision_PT_737E_Security_Camera | `benign` | `benign_traffic` | 62,154 | 61.58 MB | 94.16 |
| Provision_PT_737E_Security_Camera | `gafgyt` | `combo` | 61,380 | 104.02 MB | 74.46 |
| Provision_PT_737E_Security_Camera | `gafgyt` | `junk` | 30,898 | 50.19 MB | 74.62 |
| Provision_PT_737E_Security_Camera | `gafgyt` | `scan` | 29,297 | 37.75 MB | 76.88 |
| Provision_PT_737E_Security_Camera | `gafgyt` | `tcp` | 104,510 | 56.10 MB | 60.14 |
| Provision_PT_737E_Security_Camera | `gafgyt` | `udp` | 104,011 | 55.84 MB | 60.13 |
| Provision_PT_737E_Security_Camera | `mirai` | `ack` | 60,554 | 73.29 MB | 333.39 |
| Provision_PT_737E_Security_Camera | `mirai` | `scan` | 96,781 | 91.58 MB | 60.09 |
| Provision_PT_737E_Security_Camera | `mirai` | `syn` | 65,746 | 79.43 MB | 67.75 |
| Provision_PT_737E_Security_Camera | `mirai` | `udp` | 156,248 | 191.08 MB | 339.51 |
| Provision_PT_737E_Security_Camera | `mirai` | `udpplain` | 56,681 | 76.12 MB | 299.94 |
| Provision_PT_838_Security_Camera | `benign` | `benign_traffic` | 98,514 | 98.82 MB | 98.78 |
| Provision_PT_838_Security_Camera | `gafgyt` | `combo` | 57,530 | 97.46 MB | 74.49 |
| Provision_PT_838_Security_Camera | `gafgyt` | `junk` | 29,068 | 47.24 MB | 74.66 |
| Provision_PT_838_Security_Camera | `gafgyt` | `scan` | 28,397 | 36.67 MB | 76.91 |
| Provision_PT_838_Security_Camera | `gafgyt` | `tcp` | 89,387 | 47.99 MB | 60.16 |
| Provision_PT_838_Security_Camera | `gafgyt` | `udp` | 104,658 | 56.18 MB | 60.12 |
| Provision_PT_838_Security_Camera | `mirai` | `ack` | 57,997 | 70.15 MB | 331.30 |
| Provision_PT_838_Security_Camera | `mirai` | `scan` | 97,096 | 91.87 MB | 60.09 |
| Provision_PT_838_Security_Camera | `mirai` | `syn` | 61,851 | 74.91 MB | 67.82 |
| Provision_PT_838_Security_Camera | `mirai` | `udp` | 158,608 | 193.97 MB | 339.68 |
| Provision_PT_838_Security_Camera | `mirai` | `udpplain` | 53,785 | 72.22 MB | 299.65 |
| Samsung_SNH_1011_N_Webcam | `benign` | `benign_traffic` | 52,150 | 52.42 MB | 276.29 |
| Samsung_SNH_1011_N_Webcam | `gafgyt` | `combo` | 58,669 | 99.20 MB | 74.48 |
| Samsung_SNH_1011_N_Webcam | `gafgyt` | `junk` | 28,305 | 46.03 MB | 74.67 |
| Samsung_SNH_1011_N_Webcam | `gafgyt` | `scan` | 27,698 | 35.71 MB | 76.73 |
| Samsung_SNH_1011_N_Webcam | `gafgyt` | `tcp` | 97,783 | 52.49 MB | 60.15 |
| Samsung_SNH_1011_N_Webcam | `gafgyt` | `udp` | 110,617 | 59.38 MB | 60.12 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `benign` | `benign_traffic` | 46,585 | 45.41 MB | 183.79 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `gafgyt` | `combo` | 54,283 | 92.12 MB | 74.51 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `gafgyt` | `junk` | 28,579 | 46.34 MB | 74.67 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `gafgyt` | `scan` | 27,825 | 35.77 MB | 76.98 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `gafgyt` | `tcp` | 88,816 | 47.68 MB | 60.16 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `gafgyt` | `udp` | 103,720 | 55.68 MB | 60.13 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `mirai` | `ack` | 111,480 | 146.09 MB | 440.90 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `mirai` | `scan` | 45,930 | 43.70 MB | 60.12 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `mirai` | `syn` | 125,715 | 165.56 MB | 70.83 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `mirai` | `udp` | 151,879 | 198.68 MB | 428.82 |
| SimpleHome_XCS7_1002_WHT_Security_Camera | `mirai` | `udpplain` | 78,244 | 118.72 MB | 407.16 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `benign` | `benign_traffic` | 19,528 | 16.82 MB | 220.83 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `gafgyt` | `combo` | 59,398 | 100.70 MB | 74.47 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `gafgyt` | `junk` | 27,413 | 44.42 MB | 74.70 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `gafgyt` | `scan` | 28,572 | 36.67 MB | 76.55 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `gafgyt` | `tcp` | 98,075 | 52.65 MB | 60.15 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `gafgyt` | `udp` | 102,980 | 55.28 MB | 60.13 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `mirai` | `ack` | 107,187 | 140.37 MB | 440.33 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `mirai` | `scan` | 43,674 | 41.54 MB | 60.12 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `mirai` | `syn` | 122,479 | 161.26 MB | 70.82 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `mirai` | `udp` | 157,084 | 205.64 MB | 429.67 |
| SimpleHome_XCS7_1003_WHT_Security_Camera | `mirai` | `udpplain` | 84,436 | 127.72 MB | 404.73 |
| Ecobee_Thermostat | `benign` | `benign_traffic` | 13,113 | 13.31 MB | 207.56 |
| Ecobee_Thermostat | `gafgyt` | `combo` | 53,012 | 89.89 MB | 74.49 |
| Ecobee_Thermostat | `gafgyt` | `junk` | 30,312 | 49.28 MB | 74.63 |
| Ecobee_Thermostat | `gafgyt` | `scan` | 27,494 | 35.39 MB | 76.97 |
| Ecobee_Thermostat | `gafgyt` | `tcp` | 95,021 | 51.01 MB | 60.16 |
| Ecobee_Thermostat | `gafgyt` | `udp` | 104,791 | 56.26 MB | 60.12 |
| Ecobee_Thermostat | `mirai` | `ack` | 113,285 | 148.43 MB | 440.82 |
| Ecobee_Thermostat | `mirai` | `scan` | 43,192 | 41.08 MB | 60.12 |
| Ecobee_Thermostat | `mirai` | `syn` | 116,807 | 154.09 MB | 70.89 |
| Ecobee_Thermostat | `mirai` | `udp` | 151,481 | 198.16 MB | 429.19 |
| Ecobee_Thermostat | `mirai` | `udpplain` | 87,368 | 132.25 MB | 405.12 |