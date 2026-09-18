# N-BaIoT Feature Glossary

This document translates the 115 columns in
[`demonstrate_structure.csv`](../demonstrate_structure.csv) into readable
network-behavior descriptions.

The feature names follow this pattern:

```text
<aggregation>_<window>_<statistic>
```

For example, `HH_L5_magnitude` means the bidirectional packet-size magnitude
for a host-to-host channel, calculated with the `L5` damped history window.

## Important interpretation notes

- These are derived stream statistics, not raw packet fields such as source IP,
  destination IP, port, timestamp, or packet length.
- The 115 numeric columns do not contain the class label. The label is derived
  from the dataset path and filename, for example
  `data/security_cameras/<device>/mirai/udp.csv`.
- `L5`, `L3`, `L1`, `L0.1`, and `L0.01` are damped-window/decay settings. They
  should not automatically be interpreted as five seconds, three seconds, one
  second, and so on.
- The source documentation does not define every statistic with a full formula.
  Descriptions below use the documented meaning and the feature taxonomy in the
  N-BaIoT paper. Exact units depend on the original feature extractor.

## Aggregation levels

| Prefix | Dataset meaning | Plain-language interpretation |
|---|---|---|
| `MI` | Source MAC-IP | Recent traffic from a source IP plus MAC identity; this helps distinguish gateways and spoofed IPs. |
| `H` | Source host/IP | Recent traffic from the source host/IP as a whole. |
| `HH` | Host-to-host channel | Recent traffic from the source host/IP to the destination host/IP. |
| `HH_jit` | Host-to-host channel jitter | Timing behavior, especially the time between packet arrivals on a host-to-host channel. |
| `HpHp` | Socket | Recent traffic between source and destination host-plus-port endpoints. |

The paper describes a socket as a flow such as:

```text
192.168.4.2:1242 -> 192.168.4.12:80
```

## Statistic suffixes

| Suffix | Meaning |
|---|---|
| `weight` | Effective recent stream activity or observation weight; it can be viewed approximately as the amount of recent stream history represented. |
| `mean` | Damped/online mean of the relevant value. For `MI`, `H`, `HH`, and `HpHp`, this is generally outbound packet size; for `HH_jit`, it is inter-arrival timing. |
| `variance` | Damped/online variance of the relevant value. |
| `std` | Standard deviation of the relevant value. |
| `magnitude` | Root-sum-square of the two directional stream means. |
| `radius` | Root-sum-square of the two directional stream variances. |
| `covariance` | Approximate covariance between the two directional streams. |
| `pcc` | Approximate Pearson correlation coefficient between the two directional streams. |

The bidirectional statistics (`magnitude`, `radius`, `covariance`, and `pcc`)
are used for `HH` and `HpHp` features. The `HH_jit` family describes packet
arrival timing rather than packet size.

## Feature-count breakdown

| Family | Windows | Statistics per window | Columns |
|---|---:|---:|---:|
| `MI` | 5 | 3 | 15 |
| `H` | 5 | 3 | 15 |
| `HH` | 5 | 7 | 35 |
| `HH_jit` | 5 | 3 | 15 |
| `HpHp` | 5 | 7 | 35 |
| **Total** |  |  | **115** |

## Complete column reference

### Source MAC-IP features (`MI`)

These describe source MAC-IP activity, outbound packet-size behavior, and its
variability across five damped history windows.

| # | Column | Translation |
|---:|---|---|
| 1 | `MI_dir_L5_weight` | Source MAC-IP recent activity weight using `L5`. |
| 2 | `MI_dir_L5_mean` | Source MAC-IP outbound packet-size mean using `L5`. |
| 3 | `MI_dir_L5_variance` | Source MAC-IP outbound packet-size variance using `L5`. |
| 4 | `MI_dir_L3_weight` | Source MAC-IP recent activity weight using `L3`. |
| 5 | `MI_dir_L3_mean` | Source MAC-IP outbound packet-size mean using `L3`. |
| 6 | `MI_dir_L3_variance` | Source MAC-IP outbound packet-size variance using `L3`. |
| 7 | `MI_dir_L1_weight` | Source MAC-IP recent activity weight using `L1`. |
| 8 | `MI_dir_L1_mean` | Source MAC-IP outbound packet-size mean using `L1`. |
| 9 | `MI_dir_L1_variance` | Source MAC-IP outbound packet-size variance using `L1`. |
| 10 | `MI_dir_L0.1_weight` | Source MAC-IP recent activity weight using `L0.1`. |
| 11 | `MI_dir_L0.1_mean` | Source MAC-IP outbound packet-size mean using `L0.1`. |
| 12 | `MI_dir_L0.1_variance` | Source MAC-IP outbound packet-size variance using `L0.1`. |
| 13 | `MI_dir_L0.01_weight` | Source MAC-IP recent activity weight using `L0.01`. |
| 14 | `MI_dir_L0.01_mean` | Source MAC-IP outbound packet-size mean using `L0.01`. |
| 15 | `MI_dir_L0.01_variance` | Source MAC-IP outbound packet-size variance using `L0.01`. |

### Source host/IP features (`H`)

These describe source-host activity without the additional MAC-IP identity.

| # | Column | Translation |
|---:|---|---|
| 16 | `H_L5_weight` | Source-host recent activity weight using `L5`. |
| 17 | `H_L5_mean` | Source-host outbound packet-size mean using `L5`. |
| 18 | `H_L5_variance` | Source-host outbound packet-size variance using `L5`. |
| 19 | `H_L3_weight` | Source-host recent activity weight using `L3`. |
| 20 | `H_L3_mean` | Source-host outbound packet-size mean using `L3`. |
| 21 | `H_L3_variance` | Source-host outbound packet-size variance using `L3`. |
| 22 | `H_L1_weight` | Source-host recent activity weight using `L1`. |
| 23 | `H_L1_mean` | Source-host outbound packet-size mean using `L1`. |
| 24 | `H_L1_variance` | Source-host outbound packet-size variance using `L1`. |
| 25 | `H_L0.1_weight` | Source-host recent activity weight using `L0.1`. |
| 26 | `H_L0.1_mean` | Source-host outbound packet-size mean using `L0.1`. |
| 27 | `H_L0.1_variance` | Source-host outbound packet-size variance using `L0.1`. |
| 28 | `H_L0.01_weight` | Source-host recent activity weight using `L0.01`. |
| 29 | `H_L0.01_mean` | Source-host outbound packet-size mean using `L0.01`. |
| 30 | `H_L0.01_variance` | Source-host outbound packet-size variance using `L0.01`. |

### Host-to-host channel features (`HH`)

These describe source-to-destination host channels. Each window has activity,
outbound-size, variability, and bidirectional interaction statistics.

| # | Column | Translation |
|---:|---|---|
| 31 | `HH_L5_weight` | Host-to-host channel activity weight using `L5`. |
| 32 | `HH_L5_mean` | Channel outbound packet-size mean using `L5`. |
| 33 | `HH_L5_std` | Channel outbound packet-size standard deviation using `L5`. |
| 34 | `HH_L5_magnitude` | Bidirectional packet-size magnitude using `L5`. |
| 35 | `HH_L5_radius` | Bidirectional packet-size variability/radius using `L5`. |
| 36 | `HH_L5_covariance` | Directional packet-stream covariance using `L5`. |
| 37 | `HH_L5_pcc` | Directional packet-stream correlation using `L5`. |
| 38 | `HH_L3_weight` | Host-to-host channel activity weight using `L3`. |
| 39 | `HH_L3_mean` | Channel outbound packet-size mean using `L3`. |
| 40 | `HH_L3_std` | Channel outbound packet-size standard deviation using `L3`. |
| 41 | `HH_L3_magnitude` | Bidirectional packet-size magnitude using `L3`. |
| 42 | `HH_L3_radius` | Bidirectional packet-size variability/radius using `L3`. |
| 43 | `HH_L3_covariance` | Directional packet-stream covariance using `L3`. |
| 44 | `HH_L3_pcc` | Directional packet-stream correlation using `L3`. |
| 45 | `HH_L1_weight` | Host-to-host channel activity weight using `L1`. |
| 46 | `HH_L1_mean` | Channel outbound packet-size mean using `L1`. |
| 47 | `HH_L1_std` | Channel outbound packet-size standard deviation using `L1`. |
| 48 | `HH_L1_magnitude` | Bidirectional packet-size magnitude using `L1`. |
| 49 | `HH_L1_radius` | Bidirectional packet-size variability/radius using `L1`. |
| 50 | `HH_L1_covariance` | Directional packet-stream covariance using `L1`. |
| 51 | `HH_L1_pcc` | Directional packet-stream correlation using `L1`. |
| 52 | `HH_L0.1_weight` | Host-to-host channel activity weight using `L0.1`. |
| 53 | `HH_L0.1_mean` | Channel outbound packet-size mean using `L0.1`. |
| 54 | `HH_L0.1_std` | Channel outbound packet-size standard deviation using `L0.1`. |
| 55 | `HH_L0.1_magnitude` | Bidirectional packet-size magnitude using `L0.1`. |
| 56 | `HH_L0.1_radius` | Bidirectional packet-size variability/radius using `L0.1`. |
| 57 | `HH_L0.1_covariance` | Directional packet-stream covariance using `L0.1`. |
| 58 | `HH_L0.1_pcc` | Directional packet-stream correlation using `L0.1`. |
| 59 | `HH_L0.01_weight` | Host-to-host channel activity weight using `L0.01`. |
| 60 | `HH_L0.01_mean` | Channel outbound packet-size mean using `L0.01`. |
| 61 | `HH_L0.01_std` | Channel outbound packet-size standard deviation using `L0.01`. |
| 62 | `HH_L0.01_magnitude` | Bidirectional packet-size magnitude using `L0.01`. |
| 63 | `HH_L0.01_radius` | Bidirectional packet-size variability/radius using `L0.01`. |
| 64 | `HH_L0.01_covariance` | Directional packet-stream covariance using `L0.01`. |
| 65 | `HH_L0.01_pcc` | Directional packet-stream correlation using `L0.01`. |

### Channel jitter features (`HH_jit`)

These describe packet-arrival timing on a host-to-host channel. The `mean` is
the mean inter-arrival time and the `variance` is the variability of that timing.

| # | Column | Translation |
|---:|---|---|
| 66 | `HH_jit_L5_weight` | Channel-jitter observation weight using `L5`. |
| 67 | `HH_jit_L5_mean` | Mean packet inter-arrival time using `L5`. |
| 68 | `HH_jit_L5_variance` | Packet inter-arrival-time variance using `L5`. |
| 69 | `HH_jit_L3_weight` | Channel-jitter observation weight using `L3`. |
| 70 | `HH_jit_L3_mean` | Mean packet inter-arrival time using `L3`. |
| 71 | `HH_jit_L3_variance` | Packet inter-arrival-time variance using `L3`. |
| 72 | `HH_jit_L1_weight` | Channel-jitter observation weight using `L1`. |
| 73 | `HH_jit_L1_mean` | Mean packet inter-arrival time using `L1`. |
| 74 | `HH_jit_L1_variance` | Packet inter-arrival-time variance using `L1`. |
| 75 | `HH_jit_L0.1_weight` | Channel-jitter observation weight using `L0.1`. |
| 76 | `HH_jit_L0.1_mean` | Mean packet inter-arrival time using `L0.1`. |
| 77 | `HH_jit_L0.1_variance` | Packet inter-arrival-time variance using `L0.1`. |
| 78 | `HH_jit_L0.01_weight` | Channel-jitter observation weight using `L0.01`. |
| 79 | `HH_jit_L0.01_mean` | Mean packet inter-arrival time using `L0.01`. |
| 80 | `HH_jit_L0.01_variance` | Packet inter-arrival-time variance using `L0.01`. |

### Socket features (`HpHp`)

These describe source/destination host-plus-port flows. They use the same seven
statistics as `HH`, but at a more specific socket level.

| # | Column | Translation |
|---:|---|---|
| 81 | `HpHp_L5_weight` | Socket activity weight using `L5`. |
| 82 | `HpHp_L5_mean` | Socket outbound packet-size mean using `L5`. |
| 83 | `HpHp_L5_std` | Socket outbound packet-size standard deviation using `L5`. |
| 84 | `HpHp_L5_magnitude` | Socket bidirectional packet-size magnitude using `L5`. |
| 85 | `HpHp_L5_radius` | Socket bidirectional packet-size variability/radius using `L5`. |
| 86 | `HpHp_L5_covariance` | Socket directional packet-stream covariance using `L5`. |
| 87 | `HpHp_L5_pcc` | Socket directional packet-stream correlation using `L5`. |
| 88 | `HpHp_L3_weight` | Socket activity weight using `L3`. |
| 89 | `HpHp_L3_mean` | Socket outbound packet-size mean using `L3`. |
| 90 | `HpHp_L3_std` | Socket outbound packet-size standard deviation using `L3`. |
| 91 | `HpHp_L3_magnitude` | Socket bidirectional packet-size magnitude using `L3`. |
| 92 | `HpHp_L3_radius` | Socket bidirectional packet-size variability/radius using `L3`. |
| 93 | `HpHp_L3_covariance` | Socket directional packet-stream covariance using `L3`. |
| 94 | `HpHp_L3_pcc` | Socket directional packet-stream correlation using `L3`. |
| 95 | `HpHp_L1_weight` | Socket activity weight using `L1`. |
| 96 | `HpHp_L1_mean` | Socket outbound packet-size mean using `L1`. |
| 97 | `HpHp_L1_std` | Socket outbound packet-size standard deviation using `L1`. |
| 98 | `HpHp_L1_magnitude` | Socket bidirectional packet-size magnitude using `L1`. |
| 99 | `HpHp_L1_radius` | Socket bidirectional packet-size variability/radius using `L1`. |
| 100 | `HpHp_L1_covariance` | Socket directional packet-stream covariance using `L1`. |
| 101 | `HpHp_L1_pcc` | Socket directional packet-stream correlation using `L1`. |
| 102 | `HpHp_L0.1_weight` | Socket activity weight using `L0.1`. |
| 103 | `HpHp_L0.1_mean` | Socket outbound packet-size mean using `L0.1`. |
| 104 | `HpHp_L0.1_std` | Socket outbound packet-size standard deviation using `L0.1`. |
| 105 | `HpHp_L0.1_magnitude` | Socket bidirectional packet-size magnitude using `L0.1`. |
| 106 | `HpHp_L0.1_radius` | Socket bidirectional packet-size variability/radius using `L0.1`. |
| 107 | `HpHp_L0.1_covariance` | Socket directional packet-stream covariance using `L0.1`. |
| 108 | `HpHp_L0.1_pcc` | Socket directional packet-stream correlation using `L0.1`. |
| 109 | `HpHp_L0.01_weight` | Socket activity weight using `L0.01`. |
| 110 | `HpHp_L0.01_mean` | Socket outbound packet-size mean using `L0.01`. |
| 111 | `HpHp_L0.01_std` | Socket outbound packet-size standard deviation using `L0.01`. |
| 112 | `HpHp_L0.01_magnitude` | Socket bidirectional packet-size magnitude using `L0.01`. |
| 113 | `HpHp_L0.01_radius` | Socket bidirectional packet-size variability/radius using `L0.01`. |
| 114 | `HpHp_L0.01_covariance` | Socket directional packet-stream covariance using `L0.01`. |
| 115 | `HpHp_L0.01_pcc` | Socket directional packet-stream correlation using `L0.01`. |

## How to read common examples

### `MI_dir_L5_weight`

The effective recent outbound activity from a source MAC-IP identity using the
longer `L5` damped history.

### `H_L0.01_variance`

The outbound packet-size variability of a source host/IP using the most reactive
`L0.01` history setting.

### `HH_L1_pcc`

The approximate correlation between the two traffic directions on a
source-host-to-destination-host channel using `L1`.

### `HH_jit_L3_mean`

The average packet inter-arrival time on a host-to-host channel using `L3`.

### `HpHp_L0.01_magnitude`

The combined inbound/outbound packet-size magnitude for a specific socket flow,
emphasizing the most recent traffic through the `L0.01` setting.

## Sources

- [`N-BaIoT dataset description`](references/N_BaIoT_dataset_description_v1.txt)
- [`N-BaIoT paper reference`](N_BaIoT_Paper_Reference.md), especially Table 2
- [`demonstrate_structure.csv`](../demonstrate_structure.csv)