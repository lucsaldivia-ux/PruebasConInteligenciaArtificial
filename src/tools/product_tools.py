"""
RA2: Product Tools
Herramientas para consultar información de productos.
"""

from typing import Optional


# Base de datos de productos (en producción, sería una API/BD)
PRODUCTS_DB = {
    "bidon_20l": {"name": "Bidón 20L", "price": 5000, "liters": 20},
    "bidon_12l": {"name": "Bidón 12L", "price": 3500, "liters": 12},
    "dispensador": {"name": "Dispensador (suscripción mensual)", "price": 20000, "type": "service"}
}

# Zonas de cobertura disponibles
COVERAGE_ZONES = ["norte", "sur", "este", "oeste", "centro", "Industrial"]

DELIVERY_HOURS = "Lunes a Viernes, 09:00 a 18:00"


def get_product_price(product_name: str) -> Optional[dict]:
    """
    Retorna precio e información de un producto.

    Args:
        product_name: Nombre del producto (bidon_20l, bidon_12l, dispensador)

    Returns:
        Dict con precio y detalles, None si no existe
    """
    product_key = product_name.lower().replace(" ", "_")

    # Búsqueda flexible
    for key, product in PRODUCTS_DB.items():
        if product_key in key or key in product_name.lower():
            return {
                "key": key,
                "name": product["name"],
                "price": product["price"],
                "currency": "CLP"
            }

    return None


def check_availability(zone: str) -> dict:
    """
    Verifica disponibilidad de servicio en una zona.

    Args:
        zone: Nombre de la zona

    Returns:
        Dict con disponibilidad y horarios
    """
    zone_lower = zone.lower()
    available = any(z.lower() == zone_lower for z in COVERAGE_ZONES)

    return {
        "zone": zone,
        "available": available,
        "delivery_hours": DELIVERY_HOURS,
        "coverage_zones": COVERAGE_ZONES if not available else None,
        "message": f"Sí, contamos con servicio en {zone}" if available else f"Aún no cubrimos {zone}. Zonas disponibles: {', '.join(COVERAGE_ZONES)}"
    }


def estimate_delivery(product: str, zone: str) -> dict:
    """
    Estima tiempo de entrega para un producto en una zona.

    Args:
        product: Nombre del producto
        zone: Zona de entrega

    Returns:
        Dict con estimación de entrega
    """
    # Lógica simple: si está disponible, 1-2 días hábiles
    availability = check_availability(zone)

    if not availability["available"]:
        return {
            "product": product,
            "zone": zone,
            "available": False,
            "message": f"No podemos entregar a {zone}"
        }

    return {
        "product": product,
        "zone": zone,
        "available": True,
        "estimated_days": 1,
        "delivery_hours": DELIVERY_HOURS,
        "message": f"Entrega estimada en 1-2 días hábiles en {zone} dentro de {DELIVERY_HOURS}"
    }


def get_all_products() -> dict:
    """Retorna lista de todos los productos disponibles."""
    return {
        "products": [
            {"name": p["name"], "price": p["price"], "key": k}
            for k, p in PRODUCTS_DB.items()
        ]
    }


# Exportar como funciones herramienta para CrewAI
__all__ = [
    "get_product_price",
    "check_availability",
    "estimate_delivery",
    "get_all_products"
]
