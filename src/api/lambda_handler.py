"""
AWS Lambda Handler para Manantial Chatbot
Integración de FastAPI con AWS Lambda + API Gateway
"""

import json
import base64
from urllib.parse import parse_qs
from src.api.app import app
from mangum import Mangum

# Wrapper para Mangum (ASGI adapter para Lambda)
handler = Mangum(app, lifespan="off")


# Alternativa manual si no usas Mangum:
def lambda_handler_manual(event, context):
    """
    Manejo manual de eventos Lambda.
    Útil para debugging o si Mangum no está disponible.
    """
    try:
        # Parsear evento HTTP
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        body = event.get("body", "")
        headers = event.get("headers", {})

        # Decodificar body si está encoded
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode()

        # Parsear JSON
        if body:
            try:
                payload = json.loads(body)
            except:
                payload = {}
        else:
            payload = {}

        # Rutas disponibles
        if method == "GET" and path == "/":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "ok",
                    "version": "1.0.0",
                    "name": "Manantial Chatbot API (Lambda)"
                })
            }

        elif method == "POST" and path == "/chat/message":
            from main import chatbot

            customer_name = payload.get("customer_name")
            message = payload.get("message")
            conversation_id = payload.get("conversation_id")

            if not customer_name or not message:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "customer_name y message requeridos"})
                }

            resultado = chatbot.procesar_mensaje(customer_name, message, conversation_id)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(resultado, default=str)
            }

        elif method == "GET" and path == "/metrics":
            from main import chatbot

            metricas = chatbot.obtener_metricas()

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(metricas, default=str)
            }

        elif method == "GET" and path == "/health":
            import time
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "healthy",
                    "timestamp": time.time(),
                    "service": "manantial-chatbot-api"
                })
            }

        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Endpoint {method} {path} no encontrado"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Error interno: {str(e)}"})
        }


# Para desarrollo local, usa: from src.api.app import app + uvicorn
# Para AWS Lambda, usa: handler de Mangum arriba
