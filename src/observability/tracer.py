"""
RA3: Traceability System
Sistema de trazabilidad con Trace IDs para debugging y auditoría.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
import json
import logging


@dataclass
class Evento:
    """Evento individual en una traza."""
    nombre: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duracion_ms: float = 0
    exitoso: bool = True
    detalles: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Traza:
    """Traza completa de una conversación/request."""
    trace_id: str = field(default_factory=lambda: str(uuid4())[:16].upper())
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    customer_name: Optional[str] = None
    conversation_id: Optional[str] = None

    # Input/Output
    mensaje_entrada: str = ""
    respuesta_final: str = ""

    # Pipeline de eventos
    eventos: List[Evento] = field(default_factory=list)

    # Metadata
    modelo: str = "gpt-4o-mini"
    version_agente: str = "ra2.0"
    exitoso: bool = True
    duracion_total_ms: float = 0

    def add_evento(
        self,
        nombre: str,
        duracion_ms: float = 0,
        exitoso: bool = True,
        detalles: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> Evento:
        """Añade un evento a la traza."""
        evento = Evento(
            nombre=nombre,
            duracion_ms=duracion_ms,
            exitoso=exitoso,
            detalles=detalles or {},
            error=error
        )
        self.eventos.append(evento)
        return evento

    def to_dict(self) -> Dict:
        """Convierte a dict para serialización."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "customer_name": self.customer_name,
            "conversation_id": self.conversation_id,
            "mensaje_entrada": self.mensaje_entrada,
            "respuesta_final": self.respuesta_final,
            "eventos": [e.to_dict() for e in self.eventos],
            "modelo": self.modelo,
            "version_agente": self.version_agente,
            "exitoso": self.exitoso,
            "duracion_total_ms": self.duracion_total_ms
        }

    def to_json(self) -> str:
        """Serializa a JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class SistemaTraces:
    """Gestor centralizado de traces."""

    def __init__(self, log_file: str = "logs/traces.jsonl"):
        self.log_file = log_file
        self.traces: Dict[str, Traza] = {}
        self._init_logging()

    def _init_logging(self):
        """Inicializa logging JSON."""
        from pathlib import Path
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("manantial.traces")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def crear_traza(
        self,
        mensaje_entrada: str,
        customer_name: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Traza:
        """Crea una nueva traza."""
        traza = Traza(
            mensaje_entrada=mensaje_entrada,
            customer_name=customer_name,
            conversation_id=conversation_id
        )
        self.traces[traza.trace_id] = traza
        return traza

    def finalizar_traza(
        self,
        trace_id: str,
        respuesta_final: str,
        exitoso: bool = True,
        duracion_ms: float = 0
    ):
        """Finaliza una traza y la loguea."""
        if trace_id not in self.traces:
            return

        traza = self.traces[trace_id]
        traza.respuesta_final = respuesta_final
        traza.exitoso = exitoso
        traza.duracion_total_ms = duracion_ms

        # Log a archivo JSONL
        self.logger.info(traza.to_json())

    def get_traza(self, trace_id: str) -> Optional[Traza]:
        """Recupera una traza por ID."""
        return self.traces.get(trace_id)

    def listar_traces_cliente(self, customer_name: str) -> List[Traza]:
        """Lista todas las traces de un cliente."""
        return [
            t for t in self.traces.values()
            if t.customer_name == customer_name
        ]


# Instancia global
sistema_traces = SistemaTraces()


__all__ = ["Evento", "Traza", "SistemaTraces", "sistema_traces"]
