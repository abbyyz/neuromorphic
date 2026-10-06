#!/usr/bin/env python3
"""Plot current-voltage (I-V) curves from Keithley-style sweep CSV exports.

Examples
--------
python plot_iv_curves.py "/Users/abbyzhou/slac 26/wired measurements"
python plot_iv_curves.py "/Users/abbyzhou/slac 26/wired measurements" --save iv_curves.png
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def read_iv_csv(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return source voltage (V) and measured current (A).

    The instrument export begins with metadata.  Rather than assuming a fixed
    number of metadata lines, find the row that names the data columns.
    """
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        rows = csv.reader(handle)
        header = next((row for row in rows if "Reading" in row and "Value" in row), None)
        if header is None:
            raise ValueError("Could not find the data-column header")

        current_index = header.index("Reading")  # measured current, in amperes
        voltage_index = header.index("Value")    # swept/source voltage, in volts
        voltage, current = [], []

        for row in rows:
            if len(row) <= max(current_index, voltage_index):
                continue
            try:
                current.append(float(row[current_index]))
                voltage.append(float(row[voltage_index]))
            except ValueError:
                continue

    if not voltage:
        raise ValueError("No numeric voltage/current measurements found")
    return np.asarray(voltage), np.asarray(current)


def build_resistance_rows(file_name: str, voltage: np.ndarray, current: np.ndarray) -> list[dict[str, Any]]:
    nonzero_mask = current != 0
    if not np.any(nonzero_mask):
        return []

    filtered_voltage = voltage[nonzero_mask]
    filtered_current = current[nonzero_mask]
    resistance = filtered_voltage / filtered_current

    return [
        {
            "file_name": file_name,
            "voltage_V": float(v),
            "current_A": float(i),
            "resistance_ohm": float(r),
        }
        for v, i, r in zip(filtered_voltage, filtered_current, resistance)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot I-V curves from a directory of CSV sweeps.")
    parser.add_argument("data_directory", type=Path, help="Directory containing the CSV sweep files")
    parser.add_argument("--save", type=Path, help="Optional PNG/PDF output path")
    parser.add_argument("--show-individual", action="store_true", help="Also show one panel per sweep")
    parser.add_argument(
        "--resistance-list-out",
        type=Path,
        help="Optional CSV output path for resistance values by file (default: <data_directory>/resistance_by_file.csv)",
    )
    args = parser.parse_args()

    paths = sorted(args.data_directory.glob("*.csv"))
    if not paths:
        raise SystemExit(f"No CSV files found in {args.data_directory}")

    fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
    curves: list[tuple[str, np.ndarray, np.ndarray]] = []
    resistance_rows: list[dict[str, Any]] = []
    for path in paths:
        try:
            voltage, current = read_iv_csv(path)
        except ValueError as exc:
            print(f"Skipping {path.name}: {exc}")
            continue
        label = path.stem.replace("_", " ")
        curves.append((label, voltage, current))
        resistance_rows.extend(build_resistance_rows(path.name, voltage, current))
        ax.plot(voltage, current * 1e3, marker="o", markersize=3, linewidth=1.3, label=label)

    if not curves:
        raise SystemExit("No usable I-V data found.")
    ax.set(title="Current–Voltage Characteristics", xlabel="Voltage (V)", ylabel="Current (mA)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Sweep", fontsize=8)

    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.save, dpi=300, bbox_inches="tight")
        print(f"Saved {args.save}")

    resistance_out = args.resistance_list_out or (args.data_directory / "resistance_by_file.csv")
    resistance_out.parent.mkdir(parents=True, exist_ok=True)
    with resistance_out.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["file_name", "voltage_V", "current_A", "resistance_ohm"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resistance_rows)
    print(f"Saved {resistance_out}")

    if args.show_individual:
        n = len(curves)
        panels, axes = plt.subplots(n, 1, figsize=(7, 2.6 * n), sharex=True, constrained_layout=True)
        axes = np.atleast_1d(axes)
        for axis, (label, voltage, current) in zip(axes, curves):
            axis.plot(voltage, current * 1e3, "o-", markersize=3)
            axis.set(title=label, ylabel="Current (mA)")
            axis.grid(True, alpha=0.3)
        axes[-1].set_xlabel("Voltage (V)")

    plt.show()


if __name__ == "__main__":
    main()
