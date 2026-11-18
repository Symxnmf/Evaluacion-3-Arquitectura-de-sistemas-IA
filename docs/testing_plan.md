# Plan de pruebas EP3

Todas las ejecuciones deben conservar sus resultados reales. Los archivos de evidencia se generan en `evidence/`.

| Paso | Objetivo | Procedimiento | Resultado |
|---|---|---|---|
| 1. Unitarias | Verificar limpieza y entrenamiento | `pytest tests/test_model.py tests/test_security.py` | 9 pruebas globales aprobadas |
| 2. Integración | Componer API y modelo | `pytest tests/test_api.py` | 9 pruebas globales aprobadas |
| 3. Funcionales | Validar flujos del usuario | Ejecutar API y dashboard localmente | API y dashboard HTTP 200 |
| 4. APIs | Validar Swagger y endpoints | Abrir `/docs` y ejecutar solicitudes | Salud, modelo, recomendación y Top 10 verificados |
| 5. Seguridad | Validar JWT y cabeceras | Ejecutar pruebas de autenticación y revisar respuestas | 401 sin token y JWT firmado verificados |
| 6. Carga | Medir concurrencia | Locust con 25 usuarios durante 60 segundos | Evidencia Locust por registrar |
| 7. Rendimiento | Medir latencia | Registrar p50, p95 y p99; comparar con 500 ms | p50 3.73 ms, p95 4.91 ms, p99 4.91 ms local |
| 8. Predicciones | Validar Top 10 y fallback | Consultar usuario conocido y desconocido | Top 10 y fallback por popularidad verificados |
| 9. Errores | Detectar estados 400/401/503 | Ejecutar casos negativos y revisar logs | Evidencia por registrar |
| 10. Calidad final | Aprobar criterios | Consolidar pruebas, métricas y defectos | Evidencia por registrar |
