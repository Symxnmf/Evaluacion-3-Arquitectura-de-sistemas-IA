"""Collaborative filtering recommender based on truncated SVD."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


@dataclass
class SVDModel:
    user_ids: np.ndarray
    product_ids: np.ndarray
    user_factors: np.ndarray
    product_factors: np.ndarray
    singular_values: np.ndarray
    global_mean: float
    popularity: np.ndarray

    def recommend(self, user_id: int, top_k: int = 10) -> list[int]:
        user_index = int(np.searchsorted(self.user_ids, user_id))
        if (
            user_index >= len(self.user_ids)
            or self.user_ids[user_index] != user_id
        ):
            return self.popular_top(top_k)

        scores = (
            self.global_mean
            + (self.user_factors[user_index] * self.singular_values)
            @ self.product_factors
        )
        ranked = np.argsort(-scores, kind="stable")[:top_k]
        return [int(self.product_ids[index]) for index in ranked]

    def popular_top(self, top_k: int = 10) -> list[int]:
        popularity = np.asarray(self.popularity)
        ranked = np.argsort(-popularity, kind="stable")[:top_k]
        return [int(self.product_ids[index]) for index in ranked]

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str | Path) -> "SVDModel":
        return joblib.load(path)


def prepare_data(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"user_id", "product_id", "rating"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    frame = frame.dropna(subset=required)
    frame = frame[
        (frame["rating"] >= 1)
        & (frame["rating"] <= 5)
        & (frame["user_id"] > 0)
        & (frame["product_id"] > 0)
    ].copy()
    frame["rating"] = frame["rating"].astype(float)
    frame = (
        frame.groupby(["user_id", "product_id"], as_index=False)["rating"]
        .mean()
        .sort_values(["user_id", "product_id"])
    )
    return frame


def train(frame: pd.DataFrame, factors: int = 20) -> tuple[SVDModel, dict]:
    user_ids = np.sort(frame["user_id"].unique())
    product_ids = np.sort(frame["product_id"].unique())
    user_lookup = {value: index for index, value in enumerate(user_ids)}
    product_lookup = {value: index for index, value in enumerate(product_ids)}

    rows = frame["user_id"].map(user_lookup).to_numpy()
    columns = frame["product_id"].map(product_lookup).to_numpy()
    ratings = frame["rating"].to_numpy(dtype=float)
    global_mean = float(ratings.mean())

    centered = ratings - global_mean
    matrix = csr_matrix(
        (centered, (rows, columns)),
        shape=(len(user_ids), len(product_ids)),
    )
    rank = min(factors, min(matrix.shape) - 1)
    u, singular_values, vt = svds(matrix, k=rank)
    order = np.argsort(singular_values)[::-1]
    user_factors = u[:, order]
    singular_values = singular_values[order]
    product_factors = vt[order, :]

    popularity = np.asarray(matrix.sum(axis=0)).ravel()

    train_ids, test_ids = train_test_split(
        np.arange(len(frame)), test_size=0.2, random_state=42
    )
    predicted = (
        global_mean
        + (
            user_factors[rows[test_ids]]
            * singular_values
        )
        @ product_factors
    )
    test_columns = columns[test_ids]
    test_predictions = predicted[
        np.arange(len(test_ids)), test_columns
    ]
    test_ratings = ratings[test_ids]

    mae = mean_absolute_error(test_ratings, test_predictions)
    rmse = mean_squared_error(test_ratings, test_predictions) ** 0.5
    metrics = {
        "interactions": int(len(frame)),
        "users": int(len(user_ids)),
        "products": int(len(product_ids)),
        "factors": int(rank),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "global_mean": round(global_mean, 4),
    }
    model = SVDModel(
        user_ids=user_ids,
        product_ids=product_ids,
        user_factors=user_factors,
        product_factors=product_factors,
        singular_values=singular_values,
        global_mean=global_mean,
        popularity=popularity,
    )
    return model, metrics

