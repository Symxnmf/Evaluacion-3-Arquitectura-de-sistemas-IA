from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="ShopFast Business Intelligence",
    layout="wide",
)
st.title("ShopFast - Dashboard Empresarial")
st.caption("Datos simulados claramente identificados. Los resultados empresariales reales deben sustituir las simulaciones.")

metrics_path = Path("artifacts/model_metrics.json")
metrics = (
    json.loads(metrics_path.read_text(encoding="utf-8"))
    if metrics_path.exists()
    else {"mae": 0.0, "rmse": 0.0, "interactions": 0, "users": 0, "products": 0}
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Conversión actual", "2.3%", "Objetivo: 4.0%")
col2.metric("Ticket promedio", "USD 85", "Objetivo: USD 120")
col3.metric("MAE del modelo", metrics["mae"])
col4.metric("RMSE del modelo", metrics["rmse"])

st.subheader("Recomendaciones Top 10")
model_path = Path("artifacts/svd_model.joblib")
selected_user = st.number_input("Usuario", min_value=1, value=1, step=1)

if model_path.exists():
    import joblib

    model = joblib.load(model_path)
    recommendations = model.recommend(int(selected_user), top_k=10)
    recommendations_df = pd.DataFrame(
        {
            "Posición": range(1, 11),
            "Producto": recommendations,
        }
    )
    st.dataframe(recommendations_df, use_container_width=True, hide_index=True)
    fig = px.bar(
        recommendations_df,
        x="Posición",
        y="Producto",
        title="Top 10 recomendaciones",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Entrena el modelo para generar recomendaciones.")

st.subheader("Comportamiento de usuarios")
interaction_path = Path("data/raw/interactions.csv")
if interaction_path.exists():
    frame = pd.read_csv(interaction_path)
    if "timestamp" in frame.columns:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        daily = frame.set_index("timestamp").resample("7D").size().reset_index()
        daily.columns = ["Fecha", "Interacciones"]
        st.plotly_chart(
            px.line(daily, x="Fecha", y="Interacciones", title="Interacciones semanales"),
            use_container_width=True,
        )
    st.caption(
        f"{len(frame):,.0f} filas de interacción; "
        f"{frame['user_id'].nunique():,.0f} usuarios observados."
    )
else:
    st.info("El dataset aún no fue generado.")

st.subheader("Resultados del modelo")
model_metrics = pd.DataFrame(
    [
        {"Métrica": "Interacciones", "Valor": metrics["interactions"]},
        {"Métrica": "Usuarios", "Valor": metrics["users"]},
        {"Métrica": "Productos", "Valor": metrics["products"]},
        {"Métrica": "Factores", "Valor": metrics.get("factors", 0)},
    ]
)
st.dataframe(model_metrics, use_container_width=True, hide_index=True)

st.subheader("Métricas objetivo")
st.progress(0.575, text="Conversión: 2.3% respecto del objetivo 4.0%")
st.progress(0.708, text="Ticket: USD 85 respecto del objetivo USD 120")

