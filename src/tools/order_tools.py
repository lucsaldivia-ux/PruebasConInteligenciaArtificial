"""
RA2: Order Tools
Herramientas para gestionar pedidos.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4


class OrderManager:
    """Gestiona pedidos en memoria (en producción sería persistente)."""

    def __init__(self):
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.tickets: Dict[str, Dict[str, Any]] = {}

    def create_order(
        self, customer_name: str, product: str, quantity: int, zone: str
    ) -> Dict[str, Any]:
        """Crea un nuevo pedido."""
        order_id = f"ORD-{str(uuid4())[:8].upper()}"

        order = {
            "order_id": order_id,
            "customer": customer_name,
            "product": product,
            "quantity": quantity,
            "zone": zone,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "expected_delivery": "1-2 días hábiles"
        }

        self.orders[order_id] = order
        return order

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene estado de un pedido."""
        return self.orders.get(order_id)

    def create_ticket(
        self, customer_name: str, issue_type: str, description: str
    ) -> Dict[str, Any]:
        """Crea ticket de soporte."""
        ticket_id = f"TKT-{str(uuid4())[:8].upper()}"

        ticket = {
            "ticket_id": ticket_id,
            "customer": customer_name,
            "type": issue_type,
            "description": description,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "priority": "normal"
        }

        self.tickets[ticket_id] = ticket
        return ticket


# Instancia global
manager = OrderManager()


def process_order(
    customer_name: str, product: str, quantity: int, zone: str
) -> Dict[str, Any]:
    """
    Procesa un pedido de cliente.

    Args:
        customer_name: Nombre del cliente
        product: Producto a comprar
        quantity: Cantidad
        zone: Zona de entrega

    Returns:
        Confirmación de pedido con ID y detalles
    """
    if quantity <= 0:
        return {
            "success": False,
            "message": "La cantidad debe ser mayor a cero"
        }

    # Cálculo simple de precio
    product_prices = {
        "bidon_20l": 5000,
        "bidon_12l": 3500,
        "dispensador": 20000
    }

    price_per_unit = product_prices.get(product.lower(), 0)

    if not price_per_unit:
        return {
            "success": False,
            "message": f"Producto '{product}' no reconocido"
        }

    order = manager.create_order(customer_name, product, quantity, zone)
    total_price = price_per_unit * quantity

    return {
        "success": True,
        "order_id": order["order_id"],
        "customer": customer_name,
        "product": product,
        "quantity": quantity,
        "unit_price": price_per_unit,
        "total_price": total_price,
        "zone": zone,
        "expected_delivery": order["expected_delivery"],
        "status": "confirmado",
        "message": f"✓ Pedido confirmado. ID: {order['order_id']}. Total: ${total_price:,}. Entrega estimada: {order['expected_delivery']}"
    }


def get_order_status_by_id(order_id: str) -> Dict[str, Any]:
    """
    Consulta estado de un pedido.

    Args:
        order_id: ID del pedido

    Returns:
        Estado del pedido
    """
    order = manager.get_order_status(order_id)

    if not order:
        return {
            "found": False,
            "message": f"No encontré el pedido {order_id}"
        }

    return {
        "found": True,
        "order_id": order["order_id"],
        "customer": order["customer"],
        "product": order["product"],
        "quantity": order["quantity"],
        "status": order["status"],
        "created_at": order["created_at"],
        "expected_delivery": order["expected_delivery"],
        "message": f"Pedido {order_id} en estado: {order['status']}"
    }


def create_support_ticket(
    customer_name: str, issue_type: str, description: str
) -> Dict[str, Any]:
    """
    Crea un ticket de soporte (derivación a ejecutivo).

    Args:
        customer_name: Nombre del cliente
        issue_type: Tipo de issue (queja, devolucion, otro)
        description: Descripción del problema

    Returns:
        Ticket creado
    """
    ticket = manager.create_ticket(customer_name, issue_type, description)

    return {
        "success": True,
        "ticket_id": ticket["ticket_id"],
        "customer": customer_name,
        "issue_type": issue_type,
        "status": ticket["status"],
        "created_at": ticket["created_at"],
        "message": f"✓ Ticket creado: {ticket['ticket_id']}. Un ejecutivo se comunicará contigo pronto."
    }


__all__ = [
    "process_order",
    "get_order_status_by_id",
    "create_support_ticket",
    "manager"
]
