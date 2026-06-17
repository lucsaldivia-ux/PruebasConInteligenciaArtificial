"""
RA2 + RA3: Main Orchestrator
Integración completa: Agentes + Observabilidad + Persistencia
"""

import os
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.agent.coordinator import ManantialCrew
from src.shared.state import StateManager, CustomerState
from src.memory.persistent_memory import session_db
from src.observability.tracer import sistema_traces
from src.observability.metrics import recolector


class ManantialChatbot:
    """Chatbot principal que integra todo."""

    def __init__(self):
        self.crew = ManantialCrew()
        self.state_manager = StateManager()
        self.session_db = session_db
        self.sistema_traces = sistema_traces
        self.recolector = recolector

        # LangSmith tracing
        if os.getenv("LANGSMITH_TRACING", "false").lower() == "true":
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
            os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "manantial-chatbot")

    def procesar_mensaje(
        self,
        customer_name: str,
        mensaje: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje del cliente:
        1. Crea trace ID
        2. Obtiene/crea estado del cliente
        3. Pasa por el crew de agentes
        4. Registra métricas
        5. Persiste en BD
        """
        # Inicio de trace
        start_time = time.time()
        traza = self.sistema_traces.crear_traza(
            mensaje_entrada=mensaje,
            customer_name=customer_name,
            conversation_id=conversation_id
        )

        try:
            # Evento 1: Validación
            traza.add_evento("validacion_entrada")

            # Evento 2: Obtener estado
            estado = self.state_manager.get_or_create(customer_name)
            if conversation_id:
                estado.conversation_id = conversation_id

            traza.add_evento("cargar_estado_cliente")

            # Evento 3: Añadir mensaje al historial
            estado.add_message("user", mensaje)
            traza.add_evento("actualizar_memoria")

            # Evento 4: Procesamiento por crew
            traza.add_evento("crew_processing_inicio")
            crew_result = self.crew.procesar_mensaje(customer_name, mensaje)
            traza.add_evento("crew_processing_fin")

            respuesta = crew_result.get("respuesta", "Error procesando mensaje")
            agente_usado = crew_result.get("agent", "unknown")

            # Evento 5: Respuesta
            estado.add_message("assistant", respuesta)
            estado.add_note(agente_usado, f"Procesó: {mensaje[:50]}...")

            # Evento 6: Persistencia
            traza.add_evento("persistencia_bd")
            self.session_db.save_session(
                conversation_id=estado.conversation_id,
                customer_name=customer_name,
                messages=estado.message_history,
                state=estado.to_dict()
            )

            # Finalizar trace
            elapsed_ms = (time.time() - start_time) * 1000
            traza.respuesta_final = respuesta
            traza.exitoso = True
            traza.duracion_total_ms = elapsed_ms

            self.sistema_traces.finalizar_traza(
                trace_id=traza.trace_id,
                respuesta_final=respuesta,
                exitoso=True,
                duracion_ms=elapsed_ms
            )

            # Registrar métrica
            self.recolector.registrar(
                tiempo_respuesta_ms=elapsed_ms,
                tokens_entrada=len(mensaje.split()),  # Estimado
                tokens_salida=len(respuesta.split()),  # Estimado
                agente=agente_usado,
                exitoso=True,
                customer_name=customer_name
            )

            return {
                "trace_id": traza.trace_id,
                "conversation_id": estado.conversation_id,
                "respuesta": respuesta,
                "agente": agente_usado,
                "tiempo_ms": elapsed_ms,
                "exitoso": True
            }

        except Exception as e:
            # Error handling
            error_msg = str(e)
            traza.respuesta_final = f"Error: {error_msg}"
            traza.exitoso = False

            self.sistema_traces.finalizar_traza(
                trace_id=traza.trace_id,
                respuesta_final=error_msg,
                exitoso=False,
                duracion_ms=(time.time() - start_time) * 1000
            )

            self.recolector.registrar(
                tiempo_respuesta_ms=(time.time() - start_time) * 1000,
                agente="error",
                exitoso=False,
                error=error_msg,
                customer_name=customer_name
            )

            return {
                "trace_id": traza.trace_id,
                "respuesta": f"Disculpa, ocurrió un error: {error_msg}",
                "exitoso": False,
                "error": error_msg
            }

    def obtener_metricas(self) -> Dict[str, Any]:
        """Retorna resumen de métricas."""
        return {
            "resumen_general": self.recolector.resumen(),
            "resumen_por_agente": self.recolector.resumen_por_agente(),
            "clientes_activos": self.state_manager.list_active_conversations()
        }

    def obtener_sesion(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene sesión persistida."""
        return self.session_db.get_session(conversation_id)

    def obtener_historial_cliente(self, customer_name: str) -> Dict[str, Any]:
        """Obtiene todas las sesiones de un cliente."""
        sesiones = self.session_db.get_customer_sessions(customer_name)
        pedidos = self.session_db.get_customer_orders(customer_name)

        return {
            "customer_name": customer_name,
            "total_sesiones": len(sesiones),
            "total_pedidos": len(pedidos),
            "sesiones": sesiones,
            "pedidos": pedidos
        }


# Instancia global
chatbot = ManantialChatbot()


if __name__ == "__main__":
    # Ejemplo de uso interactivo
    print("🤖 Manantial Chatbot - RA2 + RA3")
    print("=" * 50)

    customer_name = input("¿Cuál es tu nombre? ")

    while True:
        mensaje = input(f"\n{customer_name}: ").strip()

        if mensaje.lower() in ["salir", "exit", "quit"]:
            print("Gracias por usar Manantial. ¡Hasta pronto!")
            break

        resultado = chatbot.procesar_mensaje(customer_name, mensaje)

        print(f"\n🤖 Asistente: {resultado['respuesta']}")
        print(f"⏱️  Tiempo: {resultado.get('tiempo_ms', 0):.0f}ms | 📍 Trace: {resultado['trace_id']}")

        # Mostrar métricas cada 5 mensajes
        if int(resultado.get('trace_id', '0')[-1]) % 5 == 0:
            metricas = chatbot.obtener_metricas()
            print(f"\n📊 Métricas: {metricas['resumen_general']}")
