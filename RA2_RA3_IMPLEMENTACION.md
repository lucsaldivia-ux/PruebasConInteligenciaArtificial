# Manantial Chatbot - RA2 + RA3 Implementación

## 🎉 ¡Listo para Producción!

Has evolucionado tu chatbot Manantial de **RA1 (Fundamentos)** a **RA1+RA2+RA3 (Agentes Inteligentes + Producción)**.

---

## 📁 Estructura Creada

```
proyecto_ia/PruebasConInteligenciaArtificial/
├── src/
│   ├── agent/
│   │   └── coordinator.py          # RA2: Agentes multi-especializados (CrewAI)
│   ├── tools/
│   │   ├── product_tools.py        # get_product_price, check_availability, estimate_delivery
│   │   ├── customer_tools.py       # get_customer_info, get_customer_history
│   │   └── order_tools.py          # process_order, create_support_ticket
│   ├── memory/
│   │   └── persistent_memory.py    # RA2: SQLite sessions + orders (persistencia)
│   ├── shared/
│   │   └── state.py                # Blackboard pattern (estado compartido)
│   └── observability/
│       ├── tracer.py               # RA3: Trace IDs + eventos (auditoría)
│       └── metrics.py              # RA3: Métricas de desempeño (latencia, tokens, costo)
├── data/
│   └── manantial.db               # BD SQLite (generada automáticamente)
├── logs/
│   ├── traces.jsonl               # Log de traces (auditoría completa)
│   └── metrics.jsonl              # Log de métricas
├── main.py                         # Orquestador principal
├── main_ra2_ra3.ipynb             # Notebook demo interactivo
├── requirements.txt               # Dependencias actualizadas
└── .env.example                   # Variables de entorno (RA2+RA3)
```

---

## 🚀 Quick Start

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar .env
```bash
cp .env.example .env
# Editar .env y agregar:
# - GITHUB_TOKEN (ya tienes)
# - LANGSMITH_API_KEY (opcional, para dashboard)
```

### 3. Ejecutar chatbot interactivo
```bash
python main.py
```

### 4. Demo en Jupyter
```bash
jupyter notebook main_ra2_ra3.ipynb
```

---

## 🤖 Componentes RA2 (Agentes Inteligentes)

### Agentes Especializados
1. **Coordinator** - Clasifica intent (Sales vs Support) y encamina
2. **SalesAgent** - Información, precios, disponibilidad, pedidos
3. **SupportAgent** - Consultas, quejas, tickets de escalación

### Herramientas Explícitas (9 total)
```
Productos:
  - get_product_price(product) → precio e info
  - check_availability(zone) → cobertura
  - estimate_delivery(product, zone) → tiempo entrega
  - get_all_products() → catálogo

Cliente:
  - get_customer_info(name) → historial y datos
  - get_customer_history(name) → pedidos anteriores

Pedidos:
  - process_order(customer, product, qty, zone) → crear pedido
  - get_order_status(order_id) → estado
  - create_support_ticket(customer, type, description) → escalación
```

### Blackboard Pattern (Estado Compartido)
```python
CustomerState:
  - customer_name, conversation_id
  - message_history (todos los agentes ven el historial)
  - active_order, order_history
  - agent_notes (cada agente anota lo que hizo)
```

### Persistencia SQLite
```sql
sessions:
  - conversation_id, customer_name, messages, state_json, created_at
  
orders:
  - order_id, customer_name, product, qty, zone, status, total_price
```

---

## 📊 Componentes RA3 (Observabilidad en Producción)

### Trazabilidad Completa (Trace IDs)
```
Cada mensaje genera:
  - trace_id (UUID único para debugging)
  - 5-7 eventos: validacion → memoria → crew → persistencia → respuesta
  - Duración por evento en ms
  - Full input/output logging
```

**Ejemplo de traza:**
```json
{
  "trace_id": "ABC12345DEF67890",
  "customer_name": "Juan González",
  "mensaje_entrada": "¿Cuál es el precio del bidón?",
  "eventos": [
    {"nombre": "validacion_entrada", "duracion_ms": 2, "exitoso": true},
    {"nombre": "cargar_estado_cliente", "duracion_ms": 5, "exitoso": true},
    {"nombre": "crew_processing", "duracion_ms": 2150, "exitoso": true},
    {"nombre": "persistencia_bd", "duracion_ms": 10, "exitoso": true}
  ],
  "duracion_total_ms": 2167,
  "exitoso": true
}
```

### Métricas Agregadas
```
Resumen General:
  - Total interacciones
  - Tasa de éxito (%)
  - Latencia promedio/mín/máx (ms)
  - Total tokens (entrada + salida)
  - Costo estimado (USD)
  
Por Agente:
  - Contador, tasa éxito, latencia
```

### LangSmith Integration (Listo)
```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=tu_key
LANGSMITH_PROJECT=manantial-chatbot
```
Visualiza automáticamente todas las llamadas a herramientas y LLM en `smith.langchain.com`

---

## 📝 Ejemplos de Uso

### Uso Programático
```python
from main import chatbot

# Procesar mensaje
resultado = chatbot.procesar_mensaje(
    customer_name="Juan González",
    mensaje="Quiero comprar 3 bidones de 12L"
)

print(resultado['respuesta'])
print(f"Trace ID: {resultado['trace_id']}")
print(f"Tiempo: {resultado['tiempo_ms']:.0f}ms")

# Obtener métricas
metricas = chatbot.obtener_metricas()
print(metricas['resumen_general'])

# Obtener historial cliente
historial = chatbot.obtener_historial_cliente("Juan González")
print(f"Sesiones: {len(historial['sesiones'])}")
print(f"Pedidos: {len(historial['pedidos'])}")
```

### Uso Interactivo
```bash
$ python main.py
🤖 Manantial Chatbot - RA2 + RA3
==================================================
¿Cuál es tu nombre? Juan González

Juan González: ¿Cuál es el precio del bidón de 20L?
🤖 Asistente: El bidón de 20 litros cuesta $5.000 pesos...
⏱️  Tiempo: 2150ms | 📍 Trace: ABC12345DEF67890
```

---

## 🎯 Diferencias: Antes vs Después

| Aspecto | RA1 (Antes) | RA1+RA2+RA3 (Después) |
|--------|-----------|---------------------|
| **Arquitectura** | Chatbot monolítico | 3 agentes especializados |
| **Herramientas** | RAG + LLM implícito | 9 herramientas explícitas |
| **Enrutamiento** | Prompt text | Coordinator agent clasificador |
| **Memoria** | En RAM | SQLite persistente |
| **Trazabilidad** | Logs básicos | Trace IDs + eventos detallados |
| **Métricas** | Tiempo + contexto | Latencia, tokens, costo, por agente |
| **Observabilidad** | Ninguna | LangSmith integration lista |
| **Escalabilidad** | Limitada | Producción-ready |

---

## 🔍 Debugging con Traces

**Acceder a logs:**
```bash
# Ver últimas 10 trazas
tail -10 logs/traces.jsonl

# Buscar por trace ID
grep "ABC12345DEF67890" logs/traces.jsonl | jq .

# Ver métricas
cat logs/metrics.jsonl | jq '.tiempo_respuesta_ms' | stats
```

---

## ⚙️ Configuración Avanzada

### Rate Limiting
```env
MAX_REQUESTS_PER_MINUTE=10
MAX_INPUT_LENGTH=500
```

### CrewAI Verbosity
```env
CREW_VERBOSE=true
CREW_LOG_LEVEL=INFO
```

### LangSmith
```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=xxxxxxxxxxx
LANGSMITH_PROJECT=manantial-chatbot
```

---

## 📚 Próximos Pasos

### Corto Plazo (1-2 semanas)
- [ ] Integración con Streamlit (UI web)
- [ ] FastAPI para API REST
- [ ] Webhooks para Slack/WhatsApp

### Mediano Plazo (2-4 semanas)
- [ ] Redis para estado distribuido
- [ ] PostgreSQL en lugar de SQLite
- [ ] Feedback loop: satisfacción del cliente
- [ ] A/B testing de prompts

### Largo Plazo (1+ meses)
- [ ] Workflow graphs (LanGraph)
- [ ] Fine-tuning en datos de Manantial
- [ ] Escalación a múltiples regiones
- [ ] Dashboard de analytics en Grafana

---

## 🐛 Troubleshooting

### Error: "module not found"
```bash
pip install -r requirements.txt
python -m pip install --upgrade langchain langchain-openai crewai
```

### DB locked
```bash
rm data/manantial.db  # Recrear
```

### LangSmith no conecta
```bash
export LANGSMITH_TRACING=false  # Deshabilitar temporalmente
```

### Tokens insuficientes
Verificar GITHUB_TOKEN válido y con permisos de "models"

---

## 📞 Soporte

- **Código**: `src/` con docstrings en español
- **Ejemplos**: `main_ra2_ra3.ipynb` con 3 escenarios
- **Logs**: `logs/traces.jsonl` y `logs/metrics.jsonl`
- **DB**: `data/manantial.db` (SQLite browser tools)

¡Listo para llevar a producción! 🚀
