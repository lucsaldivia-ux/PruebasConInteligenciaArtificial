"""
DynamoDB Adapter para Manantial Chatbot
Reemplaza SQLite para deployment en AWS Lambda (serverless)
"""

import boto3
import json
import time
from typing import Optional, Dict, List, Any
from pathlib import Path


class SessionDynamoDB:
    """Gestiona sesiones usando DynamoDB (para AWS Lambda)."""

    def __init__(self, table_name: str = "manantial-sessions"):
        """
        Inicializa conexión a DynamoDB.

        Args:
            table_name: Nombre de la tabla DynamoDB
        """
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)

    def save_session(
        self,
        conversation_id: str,
        customer_name: str,
        messages: List[Dict],
        state: Optional[Dict] = None
    ):
        """Guarda o actualiza una sesión en DynamoDB."""
        try:
            self.table.put_item(
                Item={
                    "conversation_id": conversation_id,
                    "customer_name": customer_name,
                    "messages": json.dumps(messages),
                    "state_json": json.dumps(state) if state else None,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                    "ttl": int(time.time()) + (30 * 24 * 60 * 60)  # 30 días
                }
            )
        except Exception as e:
            print(f"Error al guardar en DynamoDB: {e}")
            raise

    def get_session(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Recupera una sesión de DynamoDB."""
        try:
            response = self.table.get_item(Key={"conversation_id": conversation_id})

            if "Item" not in response:
                return None

            item = response["Item"]

            return {
                "conversation_id": item["conversation_id"],
                "customer_name": item["customer_name"],
                "messages": json.loads(item["messages"]),
                "state": json.loads(item["state_json"]) if item.get("state_json") else None,
                "created_at": item["created_at"],
                "updated_at": item["updated_at"]
            }

        except Exception as e:
            print(f"Error al recuperar de DynamoDB: {e}")
            return None

    def get_customer_sessions(self, customer_name: str) -> List[Dict[str, Any]]:
        """Recupera todas las sesiones de un cliente usando Query."""
        try:
            response = self.table.query(
                IndexName="customer_name-updated_at-index",  # Requerida
                KeyConditionExpression="customer_name = :customer",
                ExpressionAttributeValues={":customer": customer_name},
                ScanIndexForward=False,  # Orden descendente (más reciente primero)
                Limit=10
            )

            sesiones = []
            for item in response.get("Items", []):
                sesiones.append({
                    "conversation_id": item["conversation_id"],
                    "customer_name": item["customer_name"],
                    "messages": json.loads(item["messages"]),
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"]
                })

            return sesiones

        except Exception as e:
            print(f"Error al query sesiones: {e}")
            return []

    def save_order(
        self,
        order_id: str,
        customer_name: str,
        product: str,
        quantity: int,
        zone: str,
        status: str,
        total_price: float
    ):
        """Guarda un pedido en tabla de órdenes."""
        try:
            orders_table = self.dynamodb.Table("manantial-orders")
            orders_table.put_item(
                Item={
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "product": product,
                    "quantity": quantity,
                    "zone": zone,
                    "status": status,
                    "total_price": total_price,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time())
                }
            )
        except Exception as e:
            print(f"Error al guardar orden: {e}")

    def get_customer_orders(self, customer_name: str) -> List[Dict[str, Any]]:
        """Obtiene pedidos de un cliente."""
        try:
            orders_table = self.dynamodb.Table("manantial-orders")
            response = orders_table.query(
                IndexName="customer_name-created_at-index",  # Requerida
                KeyConditionExpression="customer_name = :customer",
                ExpressionAttributeValues={":customer": customer_name},
                ScanIndexForward=False,
                Limit=10
            )

            pedidos = []
            for item in response.get("Items", []):
                pedidos.append({
                    "order_id": item["order_id"],
                    "product": item["product"],
                    "quantity": item["quantity"],
                    "zone": item["zone"],
                    "status": item["status"],
                    "total_price": item["total_price"],
                    "created_at": item["created_at"]
                })

            return pedidos

        except Exception as e:
            print(f"Error al obtener órdenes: {e}")
            return []

    def delete_session(self, conversation_id: str):
        """Elimina una sesión (para cleanup)."""
        try:
            self.table.delete_item(Key={"conversation_id": conversation_id})
        except Exception as e:
            print(f"Error al eliminar sesión: {e}")


# Factory function para usar SQLite en desarrollo y DynamoDB en producción

def get_session_db(use_dynamodb: bool = False, table_name: str = "manantial-sessions"):
    """
    Factory para obtener DB adapter.

    Args:
        use_dynamodb: Si True, usa DynamoDB. Si False, usa SQLite
        table_name: Nombre de tabla DynamoDB

    Returns:
        SessionDynamoDB o SessionDatabase
    """
    if use_dynamodb:
        return SessionDynamoDB(table_name)
    else:
        from src.memory.persistent_memory import SessionDatabase
        return SessionDatabase()


__all__ = ["SessionDynamoDB", "get_session_db"]
