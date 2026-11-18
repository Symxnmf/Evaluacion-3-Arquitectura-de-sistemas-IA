"""Reference SageMaker inference entry point. It is not activated by local setup."""

import json
import os

import joblib


def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "svd_model.joblib"))


def input_fn(request_body, request_content_type):
    if request_content_type != "application/json":
        raise ValueError("Unsupported content type")
    return json.loads(request_body)


def predict_fn(input_data, model):
    user_id = int(input_data["user_id"])
    top_k = int(input_data.get("top_k", 10))
    return model.recommend(user_id, top_k=top_k)


def output_fn(prediction, response_content_type):
    if response_content_type != "application/json":
        raise ValueError("Unsupported response content type")
    return json.dumps({"recommendations": prediction})
