"""Command-line entry point for data inspection, validation, and first baseline."""
from __future__ import annotations

import argparse
import json

from road_icing.data.inventory import write_inventory
from road_icing.data.validation import read_table, validate_model_table
from road_icing.ml.train import run_training


def main() -> None:
    parser = argparse.ArgumentParser(description="Jeonbuk highway road-icing research scaffold")
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory", help="List raw data and file/header summaries")
    inv.add_argument("--raw-dir", default="data/raw")
    inv.add_argument("--out", default="reports/data_inventory.json")
    val = sub.add_parser("validate", help="Check canonical training table integrity")
    val.add_argument("--table", required=True)
    tr = sub.add_parser("train", help="Train station-disjoint numeric baselines")
    tr.add_argument("--table", required=True)
    tr.add_argument("--config", default="configs/experiment.yaml")
    tr.add_argument("--output", default="models")
    tr.add_argument("--report", default="reports/baseline_metrics.json")
    args = parser.parse_args()
    if args.command == "inventory":
        result = write_inventory(args.raw_dir, args.out)
    elif args.command == "validate":
        result = validate_model_table(read_table(args.table))
    else:
        result = run_training(args.table, args.config, args.output, args.report)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
