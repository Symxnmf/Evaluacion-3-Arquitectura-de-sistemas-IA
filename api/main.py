from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.auth import create_token, require_token
from model.svd_recommender import SVDModel


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = Path(os.getenv("MODEL_PATH", "artifacts/svd_model.joblib"))
    app.state.model = SVDModel.load(model_path) if model_path.exists() else None
    yield


app = FastAPI(
    title="ShopFast Recommendation API",
    description="Recommendations, model state and metrics for ShopFast.",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.post("/auth/token", tags=["Authentication"])
@limiter.limit("10/minute")
async def login(request: Request):
    if os.getenv("ENVIRONMENT", "development") == "development":
        return {"access_token": create_token(), "token_type": "bearer"}
    raise HTTPException(status_code=403, detail="Use the enterprise identity provider")


@app.get("/health", tags=["Operations"])
async def health():
    return {"status": "ok", "model_loaded": app.state.model is not None}


@app.get("/recommendations/{user_id}", tags=["Recommendations"])
@limiter.limit("60/minute")
async def recommendations(
    user_id: int,
    request: Request,
    payload: dict = Depends(require_token),
):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id must be positive")
    if app.state.model is None:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Model unavailable",
                "fallback": True,
                "product_ids": [],
            },
        )
    product_ids = app.state.model.recommend(user_id, top_k=10)
    return {
        "user_id": user_id,
        "recommendations": product_ids,
        "count": len(product_ids),
        "fallback": bool(
            user_id not in app.state.model.user_ids
        ),
        "subject": payload["sub"],
    }


@app.get("/products/top", tags=["Products"])
@limiter.limit("60/minute")
async def top_products(
    request: Request,
    payload: dict = Depends(require_token),
):
    if app.state.model is None:
        raise HTTPException(status_code=503, detail="Model unavailable")
    product_ids = app.state.model.popular_top(10)
    return {"top_10_products": product_ids}


@app.get("/model/status", tags=["Model"])
@limiter.limit("60/minute")
async def model_status(
    request: Request,
    payload: dict = Depends(require_token),
):
    metrics_path = Path("artifacts/model_metrics.json")
    metrics = {}
    if metrics_path.exists():
        import json

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    return {
        "loaded": app.state.model is not None,
        "status": "ready" if app.state.model is not None else "unavailable",
        "backend": "local-svd",
        "metrics": metrics,
    }


@app.get("/metrics", tags=["Operations"])
@limiter.limit("60/minute")
async def metrics(
    request: Request,
    payload: dict = Depends(require_token),
):
    metrics_path = Path("artifacts/model_metrics.json")
    if not metrics_path.exists():
        return {
            "model": "not-trained",
            "conversion_target": 4.0,
            "ticket_target_usd": 120.0,
            "response_target_ms": 500,
        }
    import json

    model_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    model_metrics.update(
        {
            "conversion_target": 4.0,
            "ticket_target_usd": 120.0,
            "response_target_ms": 500,
        }
    )
    return model_metrics

