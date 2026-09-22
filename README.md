# 🧪 Pruebas con Inteligencia Artificial — Proyecto Manantial (Laboratorio Experimental)

![Status](https://img.shields.io/badge/Estado-En_Desarrollo_%2F_Incompleto-yellow)
![Focus](https://img.shields.io/badge/Enfoque-Testing_%26_Evaluaci%C3%B3n_de_IA-purple)
![Project](https://img.shields.io/badge/Destinado_a-Proyecto_Manantial-blue)
![Python](https://img.shields.io/badge/Language-Python-blue)

> ⚠️ **Nota:** Este repositorio es un **proyecto en desarrollo (Work in Progress)**. Contiene pruebas conceptuales, prototipos, scripts experimentales y ejercicios en progreso relacionados con Inteligencia Artificial.

---

## 🎯 Propósito del Proyecto (Proyecto Manantial)

Este repositorio está **destinado al Proyecto Manantial**, sirviendo como entorno de pruebas, investigación y validación de componentes de Inteligencia Artificial antes de su integración final en la arquitectura del sistema.

Su objetivo es experimentar con las capacidades, límites y metodologías de evaluación de la **Inteligencia Artificial**, enfocándose en tres pilares principales:

1. **Ingeniería de Prompts & Comportamiento de Modelos:**
   - Pruebas con distintas técnicas de instrucción (*Few-Shot*, *Chain-of-Thought*, *System Prompts*).
   - Evaluación de cómo responden los modelos ante restricciones estrictas y alucinaciones.

2. **Automatización de Pruebas asistida por IA (AI-Driven Testing):**
   - Generación automática de casos de prueba (*test cases*) y escenarios límite (*edge cases*).
   - Creación de datos sintéticos de prueba mediante modelos generativos.

3. **Evaluación de Respuestas & Salidas Estructuradas (Evals):**
   - Validación del formato de salida en JSON / Pydantic para consumo en software.
   - Comparación preliminar entre distintos modelos de lenguaje (LLMs).

---

<Image src="image_agent_tag_16042685068038860033" alt="Gráfico de radar comparando diferentes modelos de IA en varias métricas" caption="Métricas de evaluación de modelos de IA" />

---

## 🛠️ Stack & Herramientas Utilizadas

- **Lenguaje:** Python 3.10+
- **Modelos / APIs:** OpenAI API / Anthropic / Ollama (Modelos locales)
- **Librerías & Frameworks:** Pytest, Pydantic, Pandas, LangChain

---

## 📁 Estructura del Repositorio

```text
├── 01-prompt-experiments/   # Ensayos de prompt engineering y respuestas
├── 02-qa-automation/        # Scripts experimentales para generación de tests
├── 03-evaluaciones-llm/     # Comparativas y pruebas de precisión de modelos
├── requirements.txt         # Dependencias del laboratorio
└── README.md
