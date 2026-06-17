"""
API REST (FastAPI) para Manantial Chatbot
Expone los agentes vía HTTP endpoints, compatible con AWS Lambda
"""

import os
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Importar el chatbot (sin CrewAI, usamos versión simplificada)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Crear chatbot mock simple (sin dependencia de CrewAI)
class SimpleChatbot:
    def procesar_mensaje(self, customer_name, mensaje, conversation_id=None):
        return {
            "trace_id": "LOCAL-TEST-001",
            "conversation_id": conversation_id or "conv-001",
            "respuesta": f"Echo: {mensaje}",
            "agente": "test",
            "tiempo_ms": 100,
            "exitoso": True
        }

    def obtener_metricas(self):
        return {
            "resumen_general": {
                "total_interacciones": 0,
                "tasa_exito": 1.0,
                "promedio_latencia_ms": 100,
                "latencia_min_ms": 50,
                "latencia_max_ms": 200,
                "total_tokens": 0,
                "promedio_tokens_entrada": 0,
                "promedio_tokens_salida": 0,
                "costo_estimado_usd": 0
            },
            "resumen_por_agente": {},
            "clientes_activos": []
        }

    def obtener_sesion(self, conversation_id):
        return {
            "conversation_id": conversation_id,
            "customer_name": "Test",
            "messages": [],
            "created_at": "2024-06-16T00:00:00",
            "updated_at": "2024-06-16T00:00:00"
        }

    def obtener_historial_cliente(self, customer_name):
        return {
            "customer_name": customer_name,
            "total_sesiones": 0,
            "total_pedidos": 0,
            "sesiones": [],
            "pedidos": []
        }

chatbot = SimpleChatbot()

# ============== Modelos Pydantic ==============

class MessageRequest(BaseModel):
    customer_name: str
    message: str
    conversation_id: Optional[str] = None


class MessageResponse(BaseModel):
    trace_id: str
    respuesta: str
    agente: str
    tiempo_ms: float
    exitoso: bool
    conversation_id: Optional[str] = None


class MetricasResponse(BaseModel):
    resumen_general: Dict[str, Any]
    resumen_por_agente: Dict[str, Any]
    clientes_activos: list


class SessionResponse(BaseModel):
    conversation_id: str
    customer_name: str
    messages: list
    created_at: str
    updated_at: str


# ============== FastAPI App ==============

app = FastAPI(
    title="Manantial Chatbot API",
    description="API REST para chatbot multi-agente con IA",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Endpoints ==============

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "name": "Manantial Chatbot API",
        "docs": "/docs"
    }


@app.post("/chat/message", response_model=MessageResponse)
async def chat_message(request: MessageRequest) -> MessageResponse:
    """
    Procesa un mensaje del cliente y retorna respuesta de agente.

    Request:
    - customer_name: Nombre del cliente
    - message: Mensaje del usuario
    - conversation_id: ID de sesión (opcional)

    Response:
    - trace_id: ID único para debugging
    - respuesta: Texto de respuesta del agente
    - agente: Tipo de agente (sales, support, error)
    - tiempo_ms: Latencia en milisegundos
    - exitoso: Booleano de éxito
    """
    try:
        # Validación básica
        if not request.customer_name or not request.customer_name.strip():
            raise HTTPException(status_code=400, detail="customer_name requerido")

        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="message requerido")

        # Limitar longitud del mensaje
        max_length = int(os.getenv("MAX_INPUT_LENGTH", "500"))
        if len(request.message) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Mensaje muy largo (máx {max_length} caracteres)"
            )

        # Procesar mensaje
        resultado = chatbot.procesar_mensaje(
            customer_name=request.customer_name,
            mensaje=request.message,
            conversation_id=request.conversation_id
        )

        return MessageResponse(
            trace_id=resultado["trace_id"],
            respuesta=resultado["respuesta"],
            agente=resultado.get("agente", "unknown"),
            tiempo_ms=resultado.get("tiempo_ms", 0),
            exitoso=resultado.get("exitoso", False),
            conversation_id=resultado.get("conversation_id")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/metrics", response_model=MetricasResponse)
async def get_metrics() -> MetricasResponse:
    """
    Retorna métricas agregadas del sistema.

    Response:
    - resumen_general: Estadísticas globales
    - resumen_por_agente: Desempeño por agente
    - clientes_activos: Lista de clientes en sesión
    """
    try:
        metricas = chatbot.obtener_metricas()

        return MetricasResponse(
            resumen_general=metricas["resumen_general"],
            resumen_por_agente=metricas["resumen_por_agente"],
            clientes_activos=metricas["clientes_activos"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas: {str(e)}")


@app.get("/session/{conversation_id}", response_model=SessionResponse)
async def get_session(conversation_id: str) -> SessionResponse:
    """
    Recupera una sesión guardada.

    Parameters:
    - conversation_id: ID de la conversación

    Response:
    - Detalles de la sesión con historial completo
    """
    try:
        sesion = chatbot.obtener_sesion(conversation_id)

        if not sesion:
            raise HTTPException(
                status_code=404,
                detail=f"Sesión {conversation_id} no encontrada"
            )

        return SessionResponse(
            conversation_id=sesion["conversation_id"],
            customer_name=sesion["customer_name"],
            messages=sesion["messages"],
            created_at=sesion["created_at"],
            updated_at=sesion["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al recuperar sesión: {str(e)}")


@app.get("/history/{customer_name}")
async def get_customer_history(customer_name: str) -> Dict[str, Any]:
    """
    Obtiene historial completo de un cliente.

    Parameters:
    - customer_name: Nombre del cliente

    Response:
    - Todas las sesiones y pedidos del cliente
    """
    try:
        historial = chatbot.obtener_historial_cliente(customer_name)

        return {
            "customer_name": historial["customer_name"],
            "total_sesiones": historial["total_sesiones"],
            "total_pedidos": historial["total_pedidos"],
            "sesiones": historial["sesiones"][:10],  # Limitar a últimas 10
            "pedidos": historial["pedidos"][:10]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint para monitoreo."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "manantial-chatbot-api",
        "version": "1.0.0"
    }


# ============== Error Handlers ==============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": True,
        "status_code": exc.status_code,
        "detail": exc.detail
    }


# ============== Local Testing ==============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
