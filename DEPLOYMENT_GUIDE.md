# Guía de Deployment: Manantial Chatbot en AWS Academy

## 📋 Requisitos Previos

- Acceso a **AWS Academy** (Lab activo)
- **AWS CLI** instalada (`aws --version`)
- **SAM CLI** instalada (`sam --version`) [Descargar](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- **Python 3.11+**
- **Git**
- Variables de entorno configuradas (GITHUB_TOKEN)

---

## 🚀 Deployment en 3 Pasos

### Paso 1: Preparar el Entorno Local

```bash
# Clonar repo (si no lo has hecho)
git clone https://github.com/TU-USUARIO/proyecto_ia.git
cd PruebasConInteligenciaArtificial

# Crear .env desde ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # O abrir en editor

# Asegúrate que tengas:
# - GITHUB_TOKEN válido
# - USE_DYNAMODB=false (para testing local primero)
```

### Paso 2: Testing Local (Recomendado)

```bash
# Terminal 1: API FastAPI
pip install -r requirements-api.txt
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Streamlit UI (en otra terminal)
streamlit run streamlit_app.py

# Abrir navegador: http://localhost:8501
# Enviar 2-3 mensajes para verificar que funciona
```

**Si todo funciona** → Proceder a Paso 3

---

### Paso 3: Deployment en AWS Academy

#### 3.1 Configurar AWS Credentials

```bash
# En AWS Academy, copiar las credenciales temporales
# Dashboard → Account Details → AWS CLI

# Configurar en tu máquina
aws configure --profile academy
# Pegar: AWS Access Key ID, AWS Secret Access Key, Region

# Verificar
aws s3 ls --profile academy
```

#### 3.2 Build con SAM

```bash
# Desde la raíz del proyecto
sam build --use-container

# Output esperado:
# Build Succeeded
# Built Artifacts  : .aws-sam/build
```

#### 3.3 Deploy con SAM (Guided)

```bash
sam deploy --guided --profile academy

# Preguntas que hará SAM:
# Stack Name: manantial-chatbot
# Region: us-east-1  (o tu región)
# Confirm changes before deploy: Y
# Allow SAM to create IAM roles: Y
# Save parameters: Y

# Esperando...
# ✓ Deployment successful
```

**Copiar la salida:**
```
Outputs:
  ChatbotApiEndpoint: https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod
```

#### 3.4 Actualizar .env para Producción

```bash
# Editar .env
API_BASE_URL="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod"
USE_DYNAMODB="true"  # Cambiar a true
```

#### 3.5 Deployar Streamlit

**Opción A: Local + Lambda (Desarrollo)**
```bash
streamlit run streamlit_app.py
# Acceder a http://localhost:8501
# Apunta automáticamente a Lambda URL en .env
```

**Opción B: Streamlit Cloud (Gratuito)**
```bash
# Subir a GitHub
git push origin main

# En Streamlit Cloud (streamlit.io):
# New app → Deploy from GitHub
# Repo: TU-USUARIO/proyecto_ia
# Branch: main
# Main file path: streamlit_app.py

# Streamlit generará una URL pública
```

**Opción C: EC2 en AWS Academy (Más control)**
```bash
# Crear EC2 instance (t2.micro, free tier)
# SSH a la instancia
ssh -i tu-key.pem ec2-user@IP

# En la instancia:
git clone tu-repo
cd PruebasConInteligenciaArtificial
pip install -r requirements-api.txt
echo "API_BASE_URL=https://YOUR-API-ID..." > .env
streamlit run streamlit_app.py

# Acceder: http://EC2-IP:8501
```

---

## 🧪 Verificación

### Local (Antes de AWS)
```bash
# Terminal con API corriendo:
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Juan", "message": "Hola"}'

# Expected Response:
# {"trace_id": "ABC123...", "respuesta": "...", "tiempo_ms": 1234}
```

### AWS (Después de Deployment)
```bash
# Reemplazar con tu API endpoint
API="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod"

# Test 1: Health Check
curl -X GET $API/health

# Test 2: Chat Message
curl -X POST $API/chat/message \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Maria", "message": "Quiero comprar un bidon"}'

# Test 3: Metrics
curl -X GET $API/metrics
```

---

## 📊 Monitorar en AWS

### CloudWatch Logs
```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/manantial-chatbot --follow --profile academy

# O en AWS Console:
# CloudWatch → Log Groups → /aws/lambda/manantial-chatbot
```

### DynamoDB
```bash
# Ver items en tabla
aws dynamodb scan --table-name manantial-sessions --profile academy

# O en AWS Console:
# DynamoDB → Tables → manantial-sessions → Explore items
```

### API Gateway
```bash
# En AWS Console:
# API Gateway → manantial-chatbot-api → Stages → prod
# Ver: Throttling, Errors, Latency
```

---

## 🛠️ Troubleshooting

### Error: "Unable to upload artifact"
```bash
# Crear S3 bucket para SAM
aws s3 mb s3://manantial-sam-artifacts-RANDOM --region us-east-1 --profile academy

# Luego ejecutar deploy con:
sam deploy --s3-bucket manantial-sam-artifacts-RANDOM
```

### Error: "AccessDenied" en DynamoDB
```bash
# Verificar IAM role en Lambda
# AWS Console → Lambda → manantial-chatbot → Execution role
# Debe tener permisos DynamoDB
```

### Error: Timeout en Lambda
```bash
# En template.yaml, aumentar Timeout:
# Timeout: 60  (en lugar de 30)

# Luego re-deploy:
sam deploy
```

### API retorna 502 Bad Gateway
```bash
# Ver CloudWatch logs:
aws logs tail /aws/lambda/manantial-chatbot --follow

# Verificar:
# - GITHUB_TOKEN válido en Lambda Environment
# - Requirements instalados correctamente (sam build)
# - Handler path correcto: src.api.lambda_handler.handler
```

---

## 🧹 Cleanup (Borrar Recursos)

Si quieres eliminar todo para ahorrar costos:

```bash
# Deletear stack CloudFormation
aws cloudformation delete-stack --stack-name manantial-chatbot --profile academy

# Borrar S3 bucket
aws s3 rm s3://manantial-sam-artifacts-RANDOM --recursive --profile academy
aws s3 rb s3://manantial-sam-artifacts-RANDOM --profile academy

# Verificar que se eliminó
aws cloudformation describe-stacks --profile academy | grep manantial
```

---

## 📝 Paso a Paso Visual (Con Screenshots)

Para ver screenshots de cada paso, consulta:
- AWS Academy Dashboard: Account Details
- SAM CLI Output: Después de `sam deploy`
- CloudWatch: Monitoring → Dashboards

---

## 🎓 Para la Prueba Universitaria

**Checklist antes de presentar:**

- [ ] API funciona localmente (uvicorn)
- [ ] Streamlit carga correctamente
- [ ] 5+ mensajes de prueba completos
- [ ] Métricas visibles (latencia, agentes)
- [ ] CloudWatch logs accesibles
- [ ] DynamoDB tiene sesiones guardadas
- [ ] Costo dentro del límite de Academy (< $1)

---

## 📞 Soporte

- **AWS Academy**: Support → Ask a Question
- **SAM Docs**: https://docs.aws.amazon.com/serverless-application-model/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

**¡Listo para presentar tu proyecto! 🎉**
