# Preparación AWS sin despliegue

Esta carpeta prepara SageMaker, S3, CloudWatch y el endpoint. No ejecuta comandos pagados.

Antes de desplegar necesitas:

1. Crear una cuenta AWS y un usuario IAM con MFA.
2. Autorizar explícitamente los costos esperados.
3. Configurar presupuesto de USD 200 con alertas.
4. Instalar AWS CLI.
5. Ejecutar `aws configure`.
6. Confirmar la región y el bucket.

Configuración objetivo:

- SageMaker Real-Time Inference de menor tamaño disponible en la región.
- Suspender o eliminar el endpoint fuera de uso.
- S3 para dataset y modelo.
- CloudWatch para logs, latencia y errores.
- ECR para almacenar la imagen.
- HTTPS obligatorio mediante API Gateway o balanceador.

No debe crearse el endpoint hasta que el costo mensual estimado sea menor al presupuesto.

