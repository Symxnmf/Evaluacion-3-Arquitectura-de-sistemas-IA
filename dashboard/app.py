from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "artifacts" / "model_metrics.json"
MODEL_PATH = ROOT / "artifacts" / "svd_model.joblib"
DATA_PATH = ROOT / "data" / "raw" / "interactions.csv"
BENCHMARK_PATH = ROOT / "evidence" / "benchmarks.json"
PYTEST_PATH = ROOT / "evidence" / "pytest.txt"

st.set_page_config(
    page_title="ShopFast | Business Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding: 2rem 3rem 3rem; }
    [data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 16px;
    }
    .status-card {
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        min-height: 110px;
    }
    .status-ok { border-left: 5px solid #16a34a; }
    .status-pending { border-left: 5px solid #f59e0b; }
    .muted { color: #64748b; font-size: 0.9rem; }
    .synthetic {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 10px;
        padding: 12px 16px;
        color: #9a3412;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return default


def load_interactions() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(DATA_PATH)


def metric_value(metrics: dict, key: str, fallback: object = "No disponible") -> object:
    value = metrics.get(key, fallback)
    return fallback if value is None else value


def format_count(value: object) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "No disponible"


def format_decimal(value: object) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return "No disponible"


def recommendation_details(model: object, user_id: int, top_k: int = 10) -> pd.DataFrame:
    product_ids = model.recommend(user_id, top_k=top_k)
    details = pd.DataFrame(
        {
            "Posición": range(1, len(product_ids) + 1),
            "ID del producto": product_ids,
            "Puntuación estimada": [None] * len(product_ids),
        }
    )
    user_ids = pd.Series(model.user_ids)
    user_positions = user_ids.searchsorted(user_id)
    if (
        user_positions < len(user_ids)
        and int(user_ids.iloc[user_positions]) == user_id
    ):
        scores = (
            float(model.global_mean)
            + (
                model.user_factors[user_positions]
                * model.singular_values
            )
            @ model.product_factors
        )
        score_by_product = {
            int(product_id): float(scores[index])
            for index, product_id in enumerate(model.product_ids)
        }
        details["Puntuación estimada"] = [
            round(score_by_product[product_id], 4)
            for product_id in product_ids
        ]
    return details


def load_test_result() -> str:
    if not PYTEST_PATH.exists():
        return "No disponible"
    content = PYTEST_PATH.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(\d+)\s+passed", content)
    return f"{match.group(1)} aprobadas" if match else "Resultado disponible"


metrics = load_json(
    METRICS_PATH,
    {"interactions": 0, "users": 0, "products": 0, "factors": 0, "mae": None, "rmse": None},
)
benchmarks = load_json(BENCHMARK_PATH, {})
interactions = load_interactions()
has_model = MODEL_PATH.exists()
interaction_count = metric_value(
    metrics,
    "interactions",
    len(interactions) if not interactions.empty else "No disponible",
)
user_count = metric_value(
    metrics,
    "users",
    interactions["user_id"].nunique() if not interactions.empty else "No disponible",
)
product_count = metric_value(
    metrics,
    "products",
    interactions["product_id"].nunique() if not interactions.empty else "No disponible",
)

updated_at = benchmarks.get("date")
if updated_at:
    try:
        updated_label = datetime.fromisoformat(updated_at).strftime("%d-%m-%Y %H:%M")
    except ValueError:
        updated_label = updated_at
else:
    updated_label = "No disponible"

st.title("ShopFast")
st.markdown("### Business Intelligence & AI Recommendations")
st.caption(f"Última actualización de datos y evidencias: **{updated_label}**")
st.markdown(
    '<div class="synthetic"><strong>Entorno de evaluación:</strong> '
    "el dataset y las métricas empresariales mostradas como referencia son sintéticos o locales. "
    "No representan resultados de producción ni un despliegue AWS.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Panel de control")
    st.markdown("**Fuente:** `data/raw/interactions.csv`")
    st.markdown(f"**Modelo cargado:** {'Sí' if has_model else 'No'}")
    st.divider()
    st.markdown("### Estado de integración")
    st.success("SVD local disponible" if has_model else "SVD no disponible")
    st.warning("RabbitMQ pendiente de conexión")
    st.info("AWS no desplegado")

st.header("Resumen ejecutivo")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total de interacciones", format_count(interaction_count))
kpi2.metric("Usuarios observados", format_count(user_count))
kpi3.metric("Productos disponibles", format_count(product_count))
model_kpi1, model_kpi2 = st.columns(2)
model_kpi1.metric("MAE del modelo", format_decimal(metric_value(metrics, "mae")))
model_kpi2.metric("RMSE del modelo", format_decimal(metric_value(metrics, "rmse")))
st.caption("Indicadores de volumen medidos sobre el dataset local disponible.")

tab_recommendations, tab_users, tab_model, tab_quality = st.tabs(
    ["Recomendaciones", "Comportamiento de usuarios", "Rendimiento del modelo", "Calidad e integraciones"]
)

with tab_recommendations:
    st.subheader("Recomendaciones personalizadas Top 10")
    selected_user = st.number_input("ID de usuario", min_value=1, value=1, step=1)
    if has_model:
        model = joblib.load(MODEL_PATH)
        recommendation_frame = recommendation_details(model, int(selected_user))
        catalog_columns = {"product_name", "name", "category", "product_category"}
        catalog_available = catalog_columns.intersection(interactions.columns)
        if catalog_available:
            st.info(
                "Se detectaron columnas de catálogo, pero no existe un catálogo "
                "separado con relación producto-nombre-categoría disponible."
            )
        else:
            st.info(
                "El dataset actual no contiene nombre ni categoría de producto. "
                "Se muestran únicamente IDs, sin generar información ficticia."
            )
        st.dataframe(
            recommendation_frame,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Posición": st.column_config.NumberColumn(format="%d"),
                "ID del producto": st.column_config.NumberColumn(format="%d"),
                "Puntuación estimada": st.column_config.NumberColumn(format="%.4f"),
            },
        )
        if recommendation_frame["Puntuación estimada"].notna().any():
            chart_frame = recommendation_frame.dropna(subset=["Puntuación estimada"])
            st.plotly_chart(
                px.bar(
                    chart_frame,
                    x="Posición",
                    y="Puntuación estimada",
                    title="Puntuación estimada por posición",
                    hover_data=["ID del producto"],
                    template="plotly_white",
                ),
                use_container_width=True,
            )
        else:
            st.info(
                "El usuario no tiene factores aprendidos; las recomendaciones "
                "provienen del fallback de popularidad y no tienen puntuación estimada."
            )
    else:
        st.warning("Entrena el modelo para generar recomendaciones.")

with tab_users:
    st.subheader("Comportamiento de usuarios")
    if interactions.empty:
        st.info("El dataset aún no está disponible.")
    else:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                px.histogram(
                    interactions.groupby("user_id", as_index=False)
                    .size()
                    .rename(columns={"size": "Interacciones"}),
                    x="Interacciones",
                    nbins=20,
                    title="Distribución de interacciones por usuario",
                    template="plotly_white",
                ),
                use_container_width=True,
            )
        with right:
            if "timestamp" in interactions.columns:
                interactions["timestamp"] = pd.to_datetime(
                    interactions["timestamp"], utc=True
                )
                weekly = (
                    interactions.set_index("timestamp")
                    .resample("7D")
                    .size()
                    .reset_index(name="Interacciones")
                )
                st.plotly_chart(
                    px.line(
                        weekly,
                        x="timestamp",
                        y="Interacciones",
                        title="Interacciones semanales",
                        template="plotly_white",
                    ),
                    use_container_width=True,
                )
        st.caption(
            f"{len(interactions):,} interacciones observadas; "
            f"{interactions['user_id'].nunique():,} usuarios con actividad."
        )

with tab_model:
    st.subheader("Rendimiento del modelo SVD")
    model_col1, model_col2, model_col3 = st.columns(3)
    model_col1.metric("MAE", metrics.get("mae", "No disponible"))
    model_col2.metric("RMSE", metrics.get("rmse", "No disponible"))
    model_col3.metric("Media global", metrics.get("global_mean", "No disponible"))
    st.caption("Métricas calculadas durante el entrenamiento local del modelo.")
    model_table = pd.DataFrame(
        [
            {"Métrica": "MAE", "Valor": metrics.get("mae"), "Origen": "Entrenamiento local"},
            {"Métrica": "RMSE", "Valor": metrics.get("rmse"), "Origen": "Entrenamiento local"},
            {"Métrica": "Factores", "Valor": metrics.get("factors"), "Origen": "Configuración SVD"},
        ]
    )
    st.dataframe(model_table, use_container_width=True, hide_index=True)

    st.subheader("Métricas de API disponibles")
    if benchmarks:
        api_frame = pd.DataFrame(
            [
                {"Métrica": "Latencia p50", "Valor": benchmarks.get("api_p50_ms"), "Unidad": "ms", "Origen": "Benchmark local"},
                {"Métrica": "Latencia p95", "Valor": benchmarks.get("api_p95_ms"), "Unidad": "ms", "Origen": "Benchmark local"},
                {"Métrica": "Latencia p99", "Valor": benchmarks.get("api_p99_ms"), "Unidad": "ms", "Origen": "Benchmark local"},
            ]
        )
        st.dataframe(api_frame, use_container_width=True, hide_index=True)
    else:
        st.info("No hay métricas de API disponibles.")

with tab_quality:
    st.subheader("Testing y calidad")
    quality1, quality2, quality3 = st.columns(3)
    quality1.metric("Pruebas automatizadas", load_test_result())
    quality2.metric("Fallback", "Verificado" if benchmarks.get("fallback") == "verified" else "No disponible")
    quality3.metric("Estado del modelo", "Listo" if has_model else "Pendiente")

    st.subheader("Estado de componentes")
    status_left, status_right = st.columns(2)
    with status_left:
        st.markdown(
            '<div class="status-card status-ok"><h4>Modelo SVD</h4>'
            "<p>Entrenado y disponible localmente.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="status-card status-ok"><h4>API REST</h4>'
            "<p>Benchmark local disponible.</p></div>",
            unsafe_allow_html=True,
        )
    with status_right:
        st.markdown(
            '<div class="status-card status-pending"><h4>RabbitMQ</h4>'
            "<p>Pendiente: no hay broker conectado en este entorno.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="status-card status-pending"><h4>AWS</h4>'
            "<p>Pendiente: configuración preparada, sin despliegue.</p></div>",
            unsafe_allow_html=True,
        )

st.divider()
st.caption(
    "ShopFast EP3 · Datos sintéticos/locales identificados explícitamente · "
    "Los resultados empresariales reales requieren datos de producción y validación A/B."
)
