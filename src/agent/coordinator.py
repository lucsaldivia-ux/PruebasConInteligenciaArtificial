"""
RA2: CrewAI Agents
Agentes especializados usando el framework CrewAI.
- Coordinator: Clasifica el intent y encamina
- Sales: Información y pedidos
- Support: Consultas y soporte
"""

import os
from typing import Optional
from crewai import Agent, Task, Crew
from crewai.tools import Tool
from langchain_openai import ChatOpenAI

# Importar herramientas
from ..tools.product_tools import (
    get_product_price,
    check_availability,
    estimate_delivery,
    get_all_products
)
from ..tools.customer_tools import (
    get_customer_info,
    get_customer_history
)
from ..tools.order_tools import (
    process_order,
    get_order_status_by_id,
    create_support_ticket
)


# Configurar modelo LLM
def get_llm():
    """Retorna instancia de LLM configurada."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("GITHUB_TOKEN")
    )


# Convertir funciones Python a herramientas CrewAI
tools = [
    Tool(
        name="get_product_price",
        func=get_product_price,
        description="Obtiene precio e información de un producto. Productos: bidon_20l, bidon_12l, dispensador"
    ),
    Tool(
        name="check_availability",
        func=check_availability,
        description="Verifica disponibilidad de servicio en una zona"
    ),
    Tool(
        name="estimate_delivery",
        func=estimate_delivery,
        description="Estima tiempo de entrega para un producto en una zona"
    ),
    Tool(
        name="get_all_products",
        func=get_all_products,
        description="Retorna lista de todos los productos disponibles"
    ),
    Tool(
        name="get_customer_info",
        func=get_customer_info,
        description="Obtiene información de un cliente (historial, zona, etc.)"
    ),
    Tool(
        name="get_customer_history",
        func=get_customer_history,
        description="Obtiene historial de pedidos de un cliente"
    ),
    Tool(
        name="process_order",
        func=process_order,
        description="Procesa un pedido: requiere customer_name, product, quantity, zone"
    ),
    Tool(
        name="get_order_status",
        func=get_order_status_by_id,
        description="Consulta estado de un pedido por su ID"
    ),
    Tool(
        name="create_support_ticket",
        func=create_support_ticket,
        description="Crea un ticket de soporte/queja para derivar a un ejecutivo"
    )
]


def create_coordinator_agent() -> Agent:
    """Crea agente coordinador."""
    return Agent(
        role="Coordinador de Atención al Cliente",
        goal="Clasificar el intent del cliente y encaminarlo al agente apropiado (Sales o Support)",
        backstory="""Eres el primer punto de contacto. Tu trabajo es:
1. Identificar al cliente por su nombre
2. Entender qué quiere (comprar, consultar, quejarse, etc.)
3. Encaminar a Sales si quiere comprar o consultar precios
4. Encaminar a Support si tiene un problema o queja
5. Mantener un tono amable y profesional""",
        tools=tools,
        llm=get_llm(),
        verbose=os.getenv("CREW_VERBOSE", "true").lower() == "true"
    )


def create_sales_agent() -> Agent:
    """Crea agente de ventas."""
    return Agent(
        role="Ejecutivo de Ventas",
        goal="Ayudar al cliente a encontrar el producto correcto, responder preguntas sobre precios y disponibilidad, y procesar pedidos",
        backstory="""Eres un ejecutivo de ventas amable y profesional de Manantial.
Tu objetivo es:
1. Entender las necesidades del cliente
2. Recomendar los productos adecuados (bidones 20L, 12L, o dispensadores)
3. Informar precios y zonas de cobertura
4. Confirmar la disponibilidad en su zona
5. Procesar el pedido si el cliente acepta
6. Proporcionar ID de pedido y fecha de entrega estimada
Sé conciso, directo y profesional.""",
        tools=tools,
        llm=get_llm(),
        verbose=os.getenv("CREW_VERBOSE", "true").lower() == "true"
    )


def create_support_agent() -> Agent:
    """Crea agente de soporte."""
    return Agent(
        role="Agente de Soporte al Cliente",
        goal="Resolver problemas, responder consultas y crear tickets para derivación a ejecutivos",
        backstory="""Eres un agente de soporte empático y profesional de Manantial.
Tu objetivo es:
1. Escuchar el problema del cliente
2. Buscar soluciones o información
3. Si es una queja, crear un ticket para que un ejecutivo se comunique
4. Proporcionar información sobre pedidos anteriores
5. Ser empático y profesional en todo momento
Recuerda: el cliente siempre tiene razón, busca resolver o escalar adecuadamente.""",
        tools=tools,
        llm=get_llm(),
        verbose=os.getenv("CREW_VERBOSE", "true").lower() == "true"
    )


class ManantialCrew:
    """Orquestador de agentes para Manantial."""

    def __init__(self):
        self.coordinator = create_coordinator_agent()
        self.sales = create_sales_agent()
        self.support = create_support_agent()

    def procesar_mensaje(self, customer_name: str, mensaje: str) -> dict:
        """
        Procesa un mensaje del cliente:
        1. Coordinador clasifica el intent
        2. Encamina a Sales o Support
        3. Retorna respuesta
        """
        # Tarea del coordinador: clasificar
        task_coordinator = Task(
            description=f"""Analiza este mensaje del cliente '{customer_name}':
            "{mensaje}"

            Determina si es:
            - SALES: Cliente quiere información, precios, disponibilidad, o hacer un pedido
            - SUPPORT: Cliente tiene un problema, queja, o necesita soporte

            Responde SOLO con: "SALES" o "SUPPORT" seguido de un resumen breve.""",
            agent=self.coordinator,
            expected_output="SALES o SUPPORT"
        )

        crew_coordinator = Crew(
            agents=[self.coordinator],
            tasks=[task_coordinator],
            verbose=True
        )

        result = crew_coordinator.kickoff()
        decision = str(result).split()[0].upper()

        # Basado en la decisión, delegar a Sales o Support
        if "SALES" in decision:
            return self._procesar_con_sales(customer_name, mensaje)
        else:
            return self._procesar_con_support(customer_name, mensaje)

    def _procesar_con_sales(self, customer_name: str, mensaje: str) -> dict:
        """Procesa con el agente de ventas."""
        task_sales = Task(
            description=f"""Cliente '{customer_name}' dice: "{mensaje}"

            Tu objetivo:
            1. Busca información del cliente con get_customer_info
            2. Si quiere comprar, identifica qué producto
            3. Usa check_availability para verificar su zona
            4. Usa get_product_price para mostrar precios
            5. Si confirma, usa process_order para registrar

            Sé conciso y profesional.""",
            agent=self.sales,
            expected_output="Respuesta completa al cliente"
        )

        crew_sales = Crew(
            agents=[self.sales],
            tasks=[task_sales],
            verbose=True
        )

        response = str(crew_sales.kickoff())

        return {
            "agent": "sales",
            "respuesta": response,
            "customer_name": customer_name
        }

    def _procesar_con_support(self, customer_name: str, mensaje: str) -> dict:
        """Procesa con el agente de soporte."""
        task_support = Task(
            description=f"""Cliente '{customer_name}' dice: "{mensaje}"

            Tu objetivo:
            1. Busca información del cliente
            2. Busca su historial de pedidos
            3. Si es un problema, crea un support ticket con create_support_ticket
            4. Sé empático y profesional

            Responde en español, de manera natural.""",
            agent=self.support,
            expected_output="Respuesta empática y solución o ticket generado"
        )

        crew_support = Crew(
            agents=[self.support],
            tasks=[task_support],
            verbose=True
        )

        response = str(crew_support.kickoff())

        return {
            "agent": "support",
            "respuesta": response,
            "customer_name": customer_name
        }


__all__ = [
    "create_coordinator_agent",
    "create_sales_agent",
    "create_support_agent",
    "ManantialCrew",
    "tools"
]
