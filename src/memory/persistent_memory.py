"""
RA2: Persistent Memory with SQLite
Almacenamiento persistente de sesiones y conversaciones.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class SessionDatabase:
    """Gestiona sesiones persistentes en SQLite."""

    def __init__(self, db_path: str = "data/manantial.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    conversation_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    state_json TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    agent_notes TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    product TEXT,
                    quantity INTEGER,
                    zone TEXT,
                    status TEXT,
                    total_price REAL,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()

    def save_session(
        self,
        conversation_id: str,
        customer_name: str,
        messages: List[Dict],
        state: Optional[Dict] = None
    ):
        """Guarda o actualiza una sesión."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (conversation_id, customer_name, messages, state_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                customer_name,
                json.dumps(messages),
                json.dumps(state) if state else None,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_session(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Recupera una sesión."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE conversation_id = ?",
                (conversation_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "conversation_id": row["conversation_id"],
                "customer_name": row["customer_name"],
                "messages": json.loads(row["messages"]),
                "state": json.loads(row["state_json"]) if row["state_json"] else None,
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }

    def get_customer_sessions(self, customer_name: str) -> List[Dict[str, Any]]:
        """Recupera todas las sesiones de un cliente."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE customer_name = ? ORDER BY updated_at DESC",
                (customer_name,)
            )
            rows = cursor.fetchall()

            return [
                {
                    "conversation_id": row["conversation_id"],
                    "customer_name": row["customer_name"],
                    "messages": json.loads(row["messages"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in rows
            ]

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
        """Guarda un pedido en la BD."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO orders
                (order_id, customer_name, product, quantity, zone, status, total_price, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                customer_name,
                product,
                quantity,
                zone,
                status,
                total_price,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_customer_orders(self, customer_name: str) -> List[Dict[str, Any]]:
        """Obtiene pedidos de un cliente."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM orders WHERE customer_name = ? ORDER BY created_at DESC",
                (customer_name,)
            )
            rows = cursor.fetchall()

            return [
                {
                    "order_id": row["order_id"],
                    "product": row["product"],
                    "quantity": row["quantity"],
                    "zone": row["zone"],
                    "status": row["status"],
                    "total_price": row["total_price"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]

    def delete_session(self, conversation_id: str):
        """Elimina una sesión (para limpieza)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE conversation_id = ?", (conversation_id,))
            conn.commit()


# Instancia global
session_db = SessionDatabase()


__all__ = ["SessionDatabase", "session_db"]
