from pathlib import Path

import pandas as pd

from model.svd_recommender import SVDModel, prepare_data, train


def test_prepare_data_removes_invalid_rows():
    path = Path("tests/fixtures_invalid.csv")
    pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4],
            "product_id": [10, 11, 12, 13],
            "rating": [4.0, 0.0, 3.0, 6.0],
        }
    ).to_csv(path, index=False)
    frame = prepare_data(path)
    path.unlink()
    assert len(frame) == 2


def test_training_returns_metrics_and_top_ten(tmp_path):
    frame = pd.DataFrame(
        {
            "user_id": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
            "product_id": [10, 11, 12, 10, 11, 13, 10, 12, 13, 11, 12, 13],
            "rating": [5, 4, 3, 5, 5, 4, 4, 3, 5, 2, 4, 5],
        }
    )
    model, metrics = train(frame, factors=2)
    assert 0 <= metrics["rmse"] <= 5
    assert len(model.recommend(1, top_k=10)) == 4


def test_unknown_user_uses_popularity_fallback(tmp_path):
    model = SVDModel(
        user_ids=pd.Series([1, 2]).to_numpy(),
        product_ids=pd.Series([10, 11]).to_numpy(),
        user_factors=[[1.0], [1.0]],
        product_factors=[[1.0], [1.0]],
        singular_values=[1.0],
        global_mean=3.0,
        popularity=[2, 5],
    )
    assert model.recommend(999, top_k=2) == [11, 10]
