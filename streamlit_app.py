"""
Streamlit App para Manantial Chatbot
Interfaz web interactiva para el chatbot
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ============== Configuración ==============

# Para desarrollo local: http://localhost:8000
# Para AWS: https://tu-api-id.execute-api.us-east-1.amazonaws.com/Prod
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Manantial Chatbot",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== Estilos ==============

st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-message.user {
        background-color: #e3f2fd;
        text-align: right;
    }
    .chat-message.assistant {
        background-color: #f5f5f5;
    }
    .metric-box {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success { color: green; }
    .error { color: red; }
    .info { color: blue; }
</style>
""", unsafe_allow_html=True)

# ============== Sidebar ==============

st.sidebar.title("⚙️ Configuración")

with st.sidebar:
    st.markdown("## 👤 Cliente")
    customer_name = st.text_input(
        "Nombre del cliente",
        value=st.session_state.get("customer_name", "Juan González"),
        key="customer_input"
    )

    if customer_name:
        st.session_state.customer_name = customer_name

    st.markdown("---")
    st.markdown("## 🔧 API")
    st.info(f"**API Base URL**: {API_BASE_URL}")

    # Test conexión
    if st.button("🔌 Probar Conexión"):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API conectada y saludable")
            else:
                st.error(f"⚠️ API retornó: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error de conexión: {str(e)}")

    st.markdown("---")
    st.markdown("## 📊 Controles")

    if st.button("🗑️ Limpiar Historial"):
        st.session_state.messages = []
        st.success("Historial limpiado")

    if st.button("📈 Ver Métricas"):
        st.session_state.show_metrics = True

    if st.button("📜 Ver Historial Cliente"):
        st.session_state.show_history = True

    st.markdown("---")
    st.markdown("## ℹ️ Información")
    st.caption("Manantial Chatbot v1.0\nRA1 + RA2 + RA3\nPotenciado por CrewAI")

# ============== Inicializar Session State ==============

if "messages" not in st.session_state:
    st.session_state.messages = []

if "customer_name" not in st.session_state:
    st.session_state.customer_name = "Juan González"

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "show_metrics" not in st.session_state:
    st.session_state.show_metrics = False

if "show_history" not in st.session_state:
    st.session_state.show_history = False

# ============== Main Content ==============

st.title("💧 Manantial Chatbot")
st.markdown(f"**Cliente**: {st.session_state.customer_name}")

# ============== Chat Display ==============

st.markdown("### 💬 Chat")

# Mostrar historial
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]

    if role == "user":
        st.markdown(f"<div class='chat-message user'><b>📝 Tú:</b> {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-message assistant'><b>🤖 Asistente:</b> {content}</div>", unsafe_allow_html=True)

        # Mostrar metadata si existe
        if "metadata" in message:
            meta = message["metadata"]
            cols = st.columns([1, 1, 1])
            with cols[0]:
                st.caption(f"⏱️ {meta['tiempo_ms']:.0f}ms")
            with cols[1]:
                st.caption(f"👤 {meta.get('agente', 'unknown')}")
            with cols[2]:
                st.caption(f"📍 {meta['trace_id'][:8]}...")

# ============== Input ==============

st.markdown("---")

col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Escribe tu mensaje:",
        placeholder="Ej: Quiero comprar un bidón de 20L",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 Enviar", use_container_width=True)

# ============== Procesar Mensaje ==============

if send_button and user_input:
    try:
        # Añadir mensaje del usuario
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Mostrar loading
        with st.spinner("🤖 Procesando..."):
            # Llamar API
            response = requests.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "customer_name": st.session_state.customer_name,
                    "message": user_input,
                    "conversation_id": st.session_state.conversation_id
                },
                timeout=60
            )

        if response.status_code == 200:
            data = response.json()

            # Guardar conversation_id
            st.session_state.conversation_id = data.get("conversation_id")

            # Añadir respuesta del asistente
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["respuesta"],
                "metadata": {
                    "trace_id": data["trace_id"],
                    "tiempo_ms": data["tiempo_ms"],
                    "agente": data["agente"]
                }
            })

            st.success(f"✅ Respuesta recibida en {data['tiempo_ms']:.0f}ms")

        else:
            error_detail = response.json().get("detail", "Error desconocido")
            st.error(f"❌ Error: {error_detail}")

    except requests.exceptions.Timeout:
        st.error("❌ Timeout: API tardó demasiado (>60s)")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Error de conexión: ¿API disponible en {API_BASE_URL}?")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

    # Refrescar
    st.rerun()

# ============== Métricas ==============

if st.session_state.show_metrics:
    st.markdown("---")
    st.markdown("### 📊 Métricas del Sistema")

    try:
        with st.spinner("Obteniendo métricas..."):
            response = requests.get(f"{API_BASE_URL}/metrics", timeout=10)

        if response.status_code == 200:
            metricas = response.json()

            # Resumen General
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Interacciones", metricas["resumen_general"]["total_interacciones"])

            with col2:
                tasa = metricas["resumen_general"]["tasa_exito"] * 100
                st.metric("Tasa Éxito", f"{tasa:.1f}%")

            with col3:
                latencia = metricas["resumen_general"]["promedio_latencia_ms"]
                st.metric("Latencia Promedio", f"{latencia:.0f}ms")

            with col4:
                tokens = metricas["resumen_general"]["total_tokens"]
                st.metric("Total Tokens", tokens)

            # Por Agente
            st.markdown("#### Por Agente:")
            for agente, stats in metricas["resumen_por_agente"].items():
                with st.expander(f"{agente} ({stats['total']} interacciones)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Exitosas", stats['exitosas'])
                    with col2:
                        st.metric("Tasa Éxito", f"{stats['tasa_exito']*100:.1f}%")
                    with col3:
                        st.metric("Latencia", f"{stats['latencia_promedio_ms']:.0f}ms")

            st.session_state.show_metrics = False

        else:
            st.error("Error al obtener métricas")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# ============== Historial Cliente ==============

if st.session_state.show_history:
    st.markdown("---")
    st.markdown("### 📜 Historial del Cliente")

    try:
        with st.spinner("Obteniendo historial..."):
            response = requests.get(
                f"{API_BASE_URL}/history/{st.session_state.customer_name}",
                timeout=10
            )

        if response.status_code == 200:
            historial = response.json()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Sesiones", historial["total_sesiones"])
            with col2:
                st.metric("Total Pedidos", historial["total_pedidos"])

            # Sesiones
            if historial["sesiones"]:
                st.markdown("#### Sesiones Recientes:")
                for sesion in historial["sesiones"][:5]:
                    with st.expander(f"🗓️ {sesion['created_at'][:10]} ({len(sesion['messages'])} msgs)"):
                        st.write(f"**ID**: {sesion['conversation_id']}")
                        st.write(f"**Mensajes**: {len(sesion['messages'])}")

            # Pedidos
            if historial["pedidos"]:
                st.markdown("#### Pedidos:")
                for pedido in historial["pedidos"][:5]:
                    st.info(
                        f"📦 {pedido['product']} x{pedido['quantity']} → "
                        f"{pedido['zone']} | ${pedido['total_price']} | {pedido['status']}"
                    )

            st.session_state.show_history = False

        else:
            st.warning("No hay historial para este cliente")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# ============== Footer ==============

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Manantial Chatbot | RA1+RA2+RA3 | AWS Deployment</div>",
    unsafe_allow_html=True
)
