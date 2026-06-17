"""
RA2: Customer Tools
Herramientas para consultar información de clientes.
"""

from typing import Optional, Dict, Any


class CustomerDatabase:
    """Simula una BD de clientes (en producción sería SQLite/PostgreSQL)."""

    def __init__(self):
        # Clientes de ejemplo
        self.customers = {
            "juan": {
                "name": "Juan González",
                "phone": "+56912345678",
                "email": "juan@empresa.com",
                "zone": "norte",
                "order_count": 3,
                "total_spent": 15500,
                "last_order": "2024-06-10"
            },
            "maria": {
                "name": "María López",
                "phone": "+56987654321",
                "email": "maria@empresa.com",
                "zone": "sur",
                "order_count": 5,
                "total_spent": 35000,
                "last_order": "2024-06-15"
            },
            "manantial_empresa": {
                "name": "Manantial Empresa",
                "phone": "+56232000000",
                "email": "pedidos@manantial.com",
                "zone": "centro",
                "order_count": 50,
                "total_spent": 500000,
                "last_order": "2024-06-16"
            }
        }
        self.order_history = {}

    def get_customer(self, name: str) -> Optional[Dict[str, Any]]:
        """Busca cliente por nombre (búsqueda flexible)."""
        name_lower = name.lower()

        for key, customer in self.customers.items():
            if name_lower in key or key in name_lower:
                return customer

        return None

    def add_order(self, customer_name: str, order: Dict[str, Any]):
        """Registra un pedido para un cliente."""
        if customer_name not in self.order_history:
            self.order_history[customer_name] = []
        self.order_history[customer_name].append(order)


# Instancia global
db = CustomerDatabase()


def get_customer_info(customer_name: str) -> Dict[str, Any]:
    """
    Obtiene información de un cliente.

    Args:
        customer_name: Nombre del cliente

    Returns:
        Dict con información del cliente o mensaje de error
    """
    customer = db.get_customer(customer_name)

    if not customer:
        return {
            "found": False,
            "message": f"No encontré cliente con el nombre '{customer_name}'",
            "action": "ask_for_name"
        }

    return {
        "found": True,
        "name": customer["name"],
        "zone": customer["zone"],
        "order_count": customer["order_count"],
        "total_spent": customer["total_spent"],
        "last_order": customer["last_order"],
        "message": f"Bienvenido {customer['name']}! Encontré tu información."
    }


def get_customer_history(customer_name: str) -> Dict[str, Any]:
    """
    Obtiene historial de pedidos de un cliente.

    Args:
        customer_name: Nombre del cliente

    Returns:
        Historial de pedidos
    """
    customer = db.get_customer(customer_name)

    if not customer:
        return {"found": False, "message": "Cliente no encontrado"}

    history = db.order_history.get(customer_name, [])

    return {
        "found": True,
        "customer": customer["name"],
        "order_count": len(history),
        "orders": history,
        "message": f"El cliente ha realizado {len(history)} pedidos"
    }


def lookup_customer_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """
    Busca cliente por teléfono (para verificación).

    Args:
        phone: Número telefónico

    Returns:
        Info del cliente o None
    """
    for customer in db.customers.values():
        if phone in customer.get("phone", ""):
            return customer

    return None


__all__ = [
    "get_customer_info",
    "get_customer_history",
    "lookup_customer_by_phone",
    "db"
]
