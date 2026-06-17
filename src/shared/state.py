"""
RA2: Shared State (Blackboard Pattern)
Estado compartido entre agentes para evitar inconsistencias y duplicación.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4


@dataclass
class CustomerState:
    """Estado central de un cliente - accesible por todos los agentes."""
    customer_name: str
    conversation_id: str = field(default_factory=lambda: str(uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Información del cliente
    phone: Optional[str] = None
    email: Optional[str] = None

    # Historial y contexto
    message_history: List[Dict[str, str]] = field(default_factory=list)
    agent_notes: Dict[str, str] = field(default_factory=dict)  # {agent_name: notes}

    # Pedido activo
    active_order: Optional[Dict[str, Any]] = None  # {product, quantity, zone, status}
    order_history: List[Dict[str, Any]] = field(default_factory=list)

    # Contexto para enrutamiento
    last_intent: Optional[str] = None  # "sales", "support", "info"
    escalated: bool = False

    def add_message(self, role: str, content: str):
        """Añade mensaje al historial."""
        self.message_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def add_note(self, agent_name: str, note: str):
        """Añade nota de agente."""
        self.agent_notes[agent_name] = f"{note} [{datetime.now().isoformat()}]"

    def start_order(self, product: str, quantity: int, zone: str):
        """Inicia un nuevo pedido."""
        self.active_order = {
            "product": product,
            "quantity": quantity,
            "zone": zone,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

    def complete_order(self):
        """Completa el pedido activo."""
        if self.active_order:
            self.active_order["status"] = "completed"
            self.order_history.append(self.active_order)
            self.active_order = None

    def to_dict(self) -> Dict:
        """Convierte a dict para serialización."""
        return asdict(self)


class StateManager:
    """Gestor centralizado de estado (Blackboard)."""

    def __init__(self):
        self.states: Dict[str, CustomerState] = {}

    def get_or_create(self, customer_name: str) -> CustomerState:
        """Obtiene o crea estado de cliente."""
        if customer_name not in self.states:
            self.states[customer_name] = CustomerState(customer_name=customer_name)
        return self.states[customer_name]

    def get_state(self, customer_name: str) -> Optional[CustomerState]:
        """Obtiene estado de cliente."""
        return self.states.get(customer_name)

    def list_active_conversations(self) -> List[str]:
        """Lista clientes con conversaciones activas."""
        return list(self.states.keys())
