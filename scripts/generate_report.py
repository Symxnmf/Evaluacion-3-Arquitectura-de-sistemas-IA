from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def main() -> None:
    output = Path("docs/Informe_Tecnico_ShopFast_EP3.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = []

    sections = [
        (
            "Informe Técnico ShopFast - EP3",
            "Arquitectura de Sistemas de Inteligencia Artificial",
        ),
        (
            "1. Contexto y situación inicial",
            "ShopFast cuenta con 50.000 usuarios activos, 5.000 productos y 150.000 interacciones históricas. "
            "La conversión reportada es 2,3% y el ticket promedio es USD 85. "
            "Los objetivos son convertir al 4% y alcanzar USD 120 por ticket.",
        ),
        (
            "2. Diagnóstico y problemas",
            "No existía una implementación verificable en el workspace inicial. "
            "Los problemas incluidos en el alcance son falta de recomendación colaborativa ejecutable, "
            "ausencia de pruebas reproducibles, acoplamiento y falta de observabilidad.",
        ),
        (
            "3. Arquitectura implementada",
            "La solución mantiene FastAPI, SVD, Docker, RabbitMQ, Streamlit y preparación para S3, SageMaker, "
            "Kubernetes/EKS y CloudWatch. SageMaker no fue activado; AWS no recibió credenciales ni despliegues pagados.",
        ),
        (
            "4. Modelo SVD",
            "Se limpiaron los datos, se eliminaron valores fuera de rango y se agruparon duplicados usuario-producto. "
            "El entrenamiento produjo 149.956 interacciones, 47.506 usuarios, 5.000 productos y 20 factores. "
            "MAE medido: 1,1953. RMSE medido: 1,3613.",
        ),
        (
            "5. API y seguridad",
            "FastAPI expone salud, recomendaciones Top 10, productos populares, estado del modelo y métricas. "
            "Swagger se sirve en /docs. JWT y rate limiting están implementados. "
            "HTTPS debe terminarse en API Gateway, balanceador o proxy en producción.",
        ),
        (
            "6. Dashboard y mensajería",
            "Streamlit presenta recomendaciones, popularidad, comportamiento de usuarios y objetivos empresariales. "
            "RabbitMQ publica eventos por exchange durable y permite una cola de interacciones.",
        ),
        (
            "7. Evidencias de pruebas",
            "La suite pytest registró 9 pruebas aprobadas. "
            "En un servicio local se midieron p50=3,73 ms, p95=4,91 ms y p99=4,91 ms. "
            "Estas mediciones no representan SageMaker ni un entorno público.",
        ),
        (
            "8. Métricas empresariales",
            "Conversión objetivo: 4,0%. Ticket objetivo: USD 120. Disponibilidad objetivo: 99%. "
            "Los valores iniciales 2,3% y USD 85 se mantienen como datos de referencia. "
            "La mejora real requiere medición A/B posterior al despliegue.",
        ),
        (
            "9. AWS y costos",
            "La carpeta aws contiene CloudFormation de S3/CloudWatch y configuración SageMaker. "
            "La política de ejecución excluye endpoints pagados. "
            "El máximo autorizado es USD 200 mensuales y debe implementarse un presupuesto con alertas.",
        ),
        (
            "10. Conclusiones y próximos pasos",
            "El proyecto cumple una base técnica local funcional, reproducible y verificable. "
            "Las oportunidades siguientes son crear dataset real, ejecutar pruebas A/B, configurar HTTPS, "
            "activación AWS aprobada, pipeline de reentrenamiento y eliminación automática de endpoints no usados.",
        ),
    ]

    story.append(Paragraph(sections[0][0], styles["Title"]))
    story.append(Paragraph(sections[0][1], styles["Subtitle"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(f"Fecha: {date.today().isoformat()}", styles["Normal"]))
    story.append(Paragraph("Nota: todos los datos empresariales no medidos se presentan como objetivos.", styles["Normal"]))

    for title, body in sections[1:]:
        story.append(PageBreak())
        story.append(Paragraph(title, styles["Heading1"]))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(body, styles["Normal"]))

    SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    ).build(story)
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
