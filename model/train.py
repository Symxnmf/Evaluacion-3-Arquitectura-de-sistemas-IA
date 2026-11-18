from __future__ import annotations

import json
from pathlib import Path

from model.svd_recommender import prepare_data, train


def main() -> None:
    frame = prepare_data("data/raw/interactions.csv")
    model, metrics = train(frame, factors=20)
    model.save("artifacts/svd_model.joblib")

    output = Path("artifacts/model_metrics.json")
    output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
