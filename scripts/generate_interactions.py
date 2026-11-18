"""Generate a reproducible synthetic ShopFast interaction dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(rows: int, users: int, products: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    user_ids = rng.integers(1, users + 1, size=rows)
    product_ids = rng.integers(1, products + 1, size=rows)
    base = rng.integers(1, 6, size=rows)
    noise = rng.normal(0, 0.45, size=rows)
    ratings = np.clip(base + noise, 1, 5).round(2)

    timestamp_start = pd.Timestamp("2026-01-01", tz="UTC")
    timestamps = timestamp_start + pd.to_timedelta(
        rng.integers(0, 300, size=rows), unit="D"
    )

    frame = pd.DataFrame(
        {
            "user_id": user_ids,
            "product_id": product_ids,
            "rating": ratings,
            "timestamp": timestamps,
        }
    )
    frame = frame.drop_duplicates(["user_id", "product_id"], keep="first")
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=150_000)
    parser.add_argument("--users", type=int, default=50_000)
    parser.add_argument("--products", type=int, default=5_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/raw/interactions.csv")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = generate(args.rows, args.users, args.products, args.seed)
    frame.to_csv(output, index=False)
    print(f"Generated {len(frame):,} synthetic interactions")
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()

