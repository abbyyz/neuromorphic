#!/usr/bin/env python3
"""Extract resistances from defbuffer-style CSV files.

Scans a folder for CSV files matching a glob (default: defbuffer*.csv),
parses each file looking for a header row that contains 'Reading' and 'Value',
reads current (A) from the 'Reading' column and voltage (V) from the 'Value' column,
computes resistances R = V / I (skipping zero/invalid currents), and writes
results to JSON and CSV outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import List, Tuple
import numpy as np


def read_iv_csv_like(csv_path: Path) -> Tuple[List[float], List[float]]:
    """Return (voltage_list, current_list) for an instrument-style CSV.

    The function locates the first row that contains both 'Reading' and 'Value'
    (case-insensitive) and then parses subsequent numeric rows. Current is
    expected under the 'Reading' column (A) and voltage under 'Value' (V).
    """
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header_row_index = None
        header = None
        rows_consumed = 0
        for i, row in enumerate(reader):
            lower = [c.strip().lower() for c in row]
            if "reading" in lower and "value" in lower:
                header_row_index = i
                header = row
                break
            rows_consumed += 1

    if header is None:
        raise ValueError(f"Could not find header row with Reading and Value in {csv_path.name}")

    # Re-open and skip to header_row_index, then parse following lines
    voltage: List[float] = []
    current: List[float] = []
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        # skip header row and any preceding metadata lines
        for _ in range(header_row_index + 1):
            next(reader, None)

        header_cells = [c.strip() for c in header]
        try:
            current_index = [c.lower() for c in header_cells].index("reading")
            voltage_index = [c.lower() for c in header_cells].index("value")
        except ValueError:
            raise ValueError("Header found but could not map Reading/Value indices")

        for row in reader:
            if len(row) <= max(current_index, voltage_index):
                continue
            try:
                i = float(row[current_index])
                v = float(row[voltage_index])
            except Exception:
                continue
            current.append(i)
            voltage.append(v)

    return voltage, current


def compute_resistance_from_fit(voltage: List[float], current: List[float]) -> dict:
    """Fit V = m*I + b and return slope m and its stderr and resistance = 1/m with propagated error.

    Returns dict with keys: slope, slope_err, resistance, resistance_err, resistance_lo, resistance_hi, n_points
    """
    x = np.asarray(current, dtype=float)
    y = np.asarray(voltage, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 2:
        return {
            "slope": float("nan"),
            "slope_err": float("nan"),
            "resistance": float("nan"),
            "resistance_err": float("nan"),
            "resistance_lo": float("nan"),
            "resistance_hi": float("nan"),
            "n_points": n,
        }
    try:
        # Fit V (y) vs I (x): slope m has units V/A
        p, cov = np.polyfit(x[mask], y[mask], 1, cov=True)
        m = float(p[0])
        # covariance matrix may be returned; variance of slope is cov[0,0]
        slope_err = float(np.sqrt(cov[0, 0])) if cov is not None else float("nan")
        # resistance is inverse of slope
        if not np.isfinite(m) or m == 0.0:
            resistance = float("inf")
            resistance_err = float("nan")
            r_lo = float("inf")
            r_hi = float("inf")
        else:
            resistance = 1.0 / m
            # propagate error: sigma_R = sigma_m / m^2
            resistance_err = float(slope_err) / (m * m) if np.isfinite(slope_err) else float("nan")
            r_lo = resistance - resistance_err
            r_hi = resistance + resistance_err
        return {
            "slope": m,
            "slope_err": slope_err,
            "resistance": resistance,
            "resistance_err": resistance_err,
            "resistance_lo": r_lo,
            "resistance_hi": r_hi,
            "n_points": n,
        }
    except Exception:
        return {
            "slope": float("nan"),
            "slope_err": float("nan"),
            "resistance": float("nan"),
            "resistance_err": float("nan"),
            "resistance_lo": float("nan"),
            "resistance_hi": float("nan"),
            "n_points": n,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract resistances from defbuffer CSVs")
    parser.add_argument(
        "folder",
        type=Path,
        nargs="?",
        default=Path("/Users/abbyzhou/slac 26/new wired measurements"),
        help="Folder containing defbuffer CSV files (default: new wired measurements)",
    )
    parser.add_argument("--pattern", default="defbuffer*.csv", help="Glob pattern for files")
    parser.add_argument("--out-json", type=Path, help="Output JSON file path")
    parser.add_argument("--out-csv", type=Path, help="Output CSV file path")
    args = parser.parse_args()

    folder = args.folder
    pattern = args.pattern
    files = sorted(folder.glob(pattern))

    if not files:
        print(f"No files found matching {pattern} in {folder}")
        return

    results = []

    for f in files:
        try:
            voltage, current = read_iv_csv_like(f)
        except Exception as e:
            print(f"Warning: skipping {f.name}: {e}")
            continue
        fit = compute_resistance_from_fit(voltage, current)
        results.append({"file": f.name, **fit})

    out_json = args.out_json or (folder / "defbuffer_resistances.json")
    out_csv = args.out_csv or (folder / "defbuffer_resistances.csv")

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file","slope_V_per_A","slope_err","resistance_ohm","resistance_err","resistance_lo","resistance_hi","n_points"])
        for row in results:
            writer.writerow([
                row.get("file"),
                f"{row.get('slope'):.6g}" if row.get("slope") is not None else "",
                f"{row.get('slope_err'):.6g}" if row.get("slope_err") is not None else "",
                f"{row.get('resistance'):.6g}" if row.get("resistance") is not None else "",
                f"{row.get('resistance_err'):.6g}" if row.get("resistance_err") is not None else "",
                f"{row.get('resistance_lo'):.6g}" if row.get("resistance_lo") is not None else "",
                f"{row.get('resistance_hi'):.6g}" if row.get("resistance_hi") is not None else "",
                int(row.get('n_points', 0)),
            ])

    print(f"Saved {out_json}\nSaved {out_csv}")


if __name__ == "__main__":
    main()
