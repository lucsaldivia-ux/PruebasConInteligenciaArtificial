"""
RA3: Observability Metrics
Recolección y análisis de métricas de desempeño del sistema.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass
class MetricaInteraccion:
    """Métrica de una interacción individual."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tiempo_respuesta_ms: float = 0
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_total: int = 0
    agente: str = ""
    modelo: str = "gpt-4o-mini"
    exitoso: bool = True
    error: Optional[str] = None
    customer_name: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "tiempo_respuesta_ms": self.tiempo_respuesta_ms,
            "tokens_entrada": self.tokens_entrada,
            "tokens_salida": self.tokens_salida,
            "tokens_total": self.tokens_total,
            "agente": self.agente,
            "modelo": self.modelo,
            "exitoso": self.exitoso,
            "error": self.error,
            "customer_name": self.customer_name
        }


class RecolectorMetricas:
    """Recolector centralizado de métricas (RA3)."""

    def __init__(self, archivo_metricas: str = "logs/metrics.jsonl"):
        self.archivo_metricas = archivo_metricas
        self.metricas: List[MetricaInteraccion] = []
        Path(self.archivo_metricas).parent.mkdir(parents=True, exist_ok=True)

    def registrar(
        self,
        tiempo_respuesta_ms: float,
        tokens_entrada: int = 0,
        tokens_salida: int = 0,
        agente: str = "general",
        exitoso: bool = True,
        error: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> MetricaInteraccion:
        """Registra una métrica."""
        metrica = MetricaInteraccion(
            tiempo_respuesta_ms=tiempo_respuesta_ms,
            tokens_entrada=tokens_entrada,
            tokens_salida=tokens_salida,
            tokens_total=tokens_entrada + tokens_salida,
            agente=agente,
            exitoso=exitoso,
            error=error,
            customer_name=customer_name
        )
        self.metricas.append(metrica)

        # Guardar a archivo
        with open(self.archivo_metricas, "a") as f:
            f.write(json.dumps(metrica.to_dict()) + "\n")

        return metrica

    def resumen(self) -> Dict:
        """Retorna resumen de métricas agregadas."""
        if not self.metricas:
            return {
                "total_interacciones": 0,
                "tasa_exito": 0,
                "promedio_latencia_ms": 0,
                "total_tokens": 0,
                "promedio_tokens_entrada": 0,
                "promedio_tokens_salida": 0
            }

        exitosas = [m for m in self.metricas if m.exitoso]
        latencias = [m.tiempo_respuesta_ms for m in self.metricas]
        tokens_entrada_total = sum(m.tokens_entrada for m in self.metricas)
        tokens_salida_total = sum(m.tokens_salida for m in self.metricas)

        return {
            "total_interacciones": len(self.metricas),
            "interacciones_exitosas": len(exitosas),
            "tasa_exito": len(exitosas) / len(self.metricas) if self.metricas else 0,
            "promedio_latencia_ms": sum(latencias) / len(latencias) if latencias else 0,
            "latencia_min_ms": min(latencias) if latencias else 0,
            "latencia_max_ms": max(latencias) if latencias else 0,
            "total_tokens": tokens_entrada_total + tokens_salida_total,
            "promedio_tokens_entrada": tokens_entrada_total / len(self.metricas) if self.metricas else 0,
            "promedio_tokens_salida": tokens_salida_total / len(self.metricas) if self.metricas else 0,
            "costo_estimado_usd": (tokens_entrada_total * 0.00015 + tokens_salida_total * 0.0006) / 1000,
        }

    def resumen_por_agente(self) -> Dict[str, Dict]:
        """Retorna resumen por tipo de agente."""
        por_agente: Dict[str, List[MetricaInteraccion]] = {}

        for metrica in self.metricas:
            if metrica.agente not in por_agente:
                por_agente[metrica.agente] = []
            por_agente[metrica.agente].append(metrica)

        resumen = {}
        for agente, metricas in por_agente.items():
            exitosas = [m for m in metricas if m.exitoso]
            latencias = [m.tiempo_respuesta_ms for m in metricas]

            resumen[agente] = {
                "total": len(metricas),
                "exitosas": len(exitosas),
                "tasa_exito": len(exitosas) / len(metricas) if metricas else 0,
                "latencia_promedio_ms": sum(latencias) / len(latencias) if latencias else 0
            }

        return resumen

    def limpiar(self):
        """Limpia métricas en memoria (archivo se mantiene)."""
        self.metricas.clear()


# Instancia global
recolector = RecolectorMetricas()


__all__ = ["MetricaInteraccion", "RecolectorMetricas", "recolector"]
