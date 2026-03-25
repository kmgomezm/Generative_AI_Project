# Generative_AI_Project
Maestría en Ciencia de Datos · Docente: Jorge I. Padilla-Buriticá · Período 2026-1
*Final workshop for Introduction to AI.*

**Integrantes:**
- Ana Patricia Montes Pimienta
- Karen Melissa Gómez Montoya
- Juan Esteban Estrada Herrera

**Nota**: El modelo gratuito de Groq de Text to Speech tiene un límite de tokens, se acaba pronto y se resetea a la hora.

# 🎓 Generative AI Project – QuickStudy Assistant

## 📌 Descripción

**QuickStudy Assistant** es una aplicación web desarrollada con **Streamlit** que utiliza **Inteligencia Artificial Generativa** para apoyar procesos de estudio.  

Permite cargar documentos en **PDF**, realizar preguntas **por texto o voz**, y obtener **resúmenes, cuestionarios interactivos y audio**, basados exclusivamente en el contenido de los documentos cargados.

El proyecto implementa una arquitectura de **Retrieval‑Augmented Generation (RAG)**, combinando búsqueda semántica con modelos de lenguaje de gran escala.

---

## 🎯 Objetivo

Demostrar el uso práctico de IA generativa para:
- Comprender documentos extensos
- Responder preguntas fundamentadas en texto
- Generar resúmenes estructurados
- Crear cuestionarios de autoevaluación
- Evaluar respuestas del estudiante
- Ofrecer aprendizaje multimodal (texto + voz)

---

## 🧠 Funcionalidades principales

- 📄 **Carga de PDFs** y extracción de texto
- 📐 **Indexación vectorial** con FAISS y embeddings multilingües
- 🎙️ **Preguntas por voz** con transcripción automática (Whisper)
- 🔍 **Búsqueda semántica (RAG)** sobre los documentos
- 🧠 **Generación de resúmenes y cuestionarios** con LLM
- ✅ **Evaluación automática** de respuestas (Correcto / Parcial / Incorrecto)
- 🔊 **Text‑to‑Speech** para escuchar el resumen
- 📥 Descarga de resultados en texto y audio

---

## 🧰 Tecnologías

- Python
- Streamlit
- LangChain
- FAISS
- Sentence Transformers (MiniLM)
- Groq API:
  - Whisper (STT)
  - LLaMA 3.3 70B (LLM)
  - Orpheus TTS
- PyMuPDF

---

## 👥 Público objetivo

- Estudiantes
- Docentes
- Investigadores
- Proyectos académicos y demostrativos de IA generativa

---

## ⚠️ Consideraciones

- Requiere **Groq API Key**
- El contenido se envía al proveedor del modelo durante la inferencia
- No recomendado para documentos con información confidencial
- Proyecto de carácter **educativo y experimental**, no productivo

---

## ✅ Estado del proyecto

- ✔️ Funcional
- ✔️ Modular y extensible
- 🚧 Uso académico / demostrativo

---

## 📌 Conclusión

**QuickStudy Assistant** muestra cómo la IA generativa y el enfoque RAG pueden transformar documentos estáticos en herramientas interactivas de aprendizaje, integrando texto, voz, evaluación y retroalimentación automática en una sola aplicación.


