#!/usr/bin/env python3
"""Combine defbuffer I-V CSV files into one Excel workbook.

Each matching CSV becomes its own sheet, so data stays separated by file title.
The script reads:
- current from the "Reading" column (A)
- voltage from the "Value" column (V)
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from openpyxl import Workbook


def read_iv_csv_like(csv_path: Path) -> tuple[list[float], list[float]]:
    """Return voltage and current arrays parsed from a Keithley-style CSV."""
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(
            (
                row
                for row in reader
                if "reading" in [c.strip().lower() for c in row]
                and "value" in [c.strip().lower() for c in row]
            ),
            None,
        )
        if header is None:
            raise ValueError("Could not find header row containing Reading and Value")

        lowered = [c.strip().lower() for c in header]
        current_index = lowered.index("reading")
        voltage_index = lowered.index("value")

        current: list[float] = []
        voltage: list[float] = []
        for row in reader:
            if len(row) <= max(current_index, voltage_index):
                continue
            try:
                current.append(float(row[current_index]))
                voltage.append(float(row[voltage_index]))
            except ValueError:
                continue

    if not current:
        raise ValueError("No numeric I-V rows found")
    return voltage, current


def excel_safe_sheet_name(name: str, used: set[str]) -> str:
    """Convert file title to a valid, unique Excel worksheet name."""
    invalid = set('[]:*?/\\')
    cleaned = "".join("_" if ch in invalid else ch for ch in name).strip()
    if not cleaned:
        cleaned = "sheet"
    cleaned = cleaned[:31]

    candidate = cleaned
    counter = 2
    while candidate in used:
        suffix = f"_{counter}"
        candidate = f"{cleaned[:31 - len(suffix)]}{suffix}"
        counter += 1
    used.add(candidate)
    return candidate


def build_workbook(data_dir: Path, pattern: str, out_path: Path) -> None:
    csv_paths = sorted(data_dir.glob(pattern))
    if not csv_paths:
        raise SystemExit(f"No files found for pattern '{pattern}' in {data_dir}")

    workbook = Workbook()
    summary = workbook.active
    summary.title = "summary"
    summary.append(["file_name", "sheet_name", "row_count"])

    used_names: set[str] = {"summary"}
    written_count = 0

    for path in csv_paths:
        try:
            voltage, current = read_iv_csv_like(path)
        except ValueError as exc:
            print(f"Skipping {path.name}: {exc}")
            continue

        sheet_name = excel_safe_sheet_name(path.stem, used_names)
        ws = workbook.create_sheet(title=sheet_name)
        ws.append(["current_A", "voltage_V"])
        for i, v in zip(current, voltage):
            ws.append([i, v])

        summary.append([path.name, sheet_name, len(current)])
        written_count += 1

    if written_count == 0:
        raise SystemExit("No readable defbuffer CSV files were found.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(out_path)
    print(f"Saved {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine defbuffer CSV current/voltage data into one Excel workbook."
    )
    parser.add_argument(
        "data_directory",
        type=Path,
        nargs="?",
        default=Path("/Users/abbyzhou/slac 26/new wired measurements"),
        help="Folder containing defbuffer CSV files",
    )
    parser.add_argument(
        "--pattern",
        default="defbuffer*.csv",
        help="Glob pattern for input CSV files",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output workbook path (default: <data_directory>/defbuffer_iv_data.xlsx)",
    )
    args = parser.parse_args()

    out_path = args.out or (args.data_directory / "defbuffer_iv_data.xlsx")
    build_workbook(args.data_directory, args.pattern, out_path)


if __name__ == "__main__":
    main()
