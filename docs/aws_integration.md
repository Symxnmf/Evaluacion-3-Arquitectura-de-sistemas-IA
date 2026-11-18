# Integración AIaaS ShopFast

## Servicios

- **S3:** contiene dataset, modelo empaquetado y artefactos.
- **SageMaker:** hospeda el modelo y expone un endpoint de inferencia.
- **CloudWatch:** recolecta logs y métricas.
- **API Gateway:** recomendable como entrada HTTPS y protección.
- **EKS:** no es obligatorio para el entorno local, pero conserva compatibilidad con la arquitectura EP2.

## Ruta de despliegue manual

1. Ejecutar las pruebas localmente.
2. Obtener autorización para recursos pagados.
3. Crear bucket con CloudFormation.
4. Subir dataset y modelo.
5. Construir una imagen SageMaker.
6. Crear modelo y endpoint configuration.
7. Crear endpoint.
8. Comparar costo estimado con USD 200 mensuales.
9. Configurar alertas.
10. Eliminar el endpoint cuando no se use.

El script `aws/sagemaker_config.json` contiene valores de referencia. Las cadenas `REPLACE_WITH_*` deben completarse con recursos reales.
