# Informe de mejora del proceso empresarial

## Situación inicial

ShopFast tenía una conversión informada de 2.3% y un ticket promedio de USD 85. Se recibía un volumen de 150,000 interacciones históricas sobre 50,000 usuarios y 5,000 productos.

## Problemas detectados

- Recomendaciones sin modelo colaborativo verificable.
- Ausencia de validación automática de calidad.
- Operaciones acopladas sin mensajería.
- Falta de observabilidad centralizada.
- Riesgo de servir recomendaciones sin fallback.

## Solución implementada

El proyecto incorpora SVD, API FastAPI, dashboard, RabbitMQ, Docker y preparación AWS. Estos componentes forman una base local reproducible y un camino hacia SageMaker.

## Indicadores antes y después

| Indicador | Antes | Objetivo | Resultado medido |
|---|---:|---:|---:|
| Conversión | 2.3% | 4.0% | Pendiente de medición A/B |
| Ticket promedio | USD 85 | USD 120 | Pendiente de medición A/B |
| Latencia | No medida | <500 ms | Pendiente de medición local |
| Disponibilidad | No documentada | 99% | Pendiente de producción |
| Calidad MAE/RMSE | No documentada | Reducir ambas | Disponible después de entrenar |

## Garantía de calidad

Las pruebas del repositorio verifican datos, entrenamiento, API, autenticación y fallback. Las pruebas de carga generan métricas reales solamente cuando se ejecutan. No se presentan datos empresariales como observados si no existen.

## Conclusiones

La arquitectura establece los fundamentos para mejorar conversión y ticket mediante personalización. El impacto económico debe validarse con pruebas A/B en producción, no por simulación.
