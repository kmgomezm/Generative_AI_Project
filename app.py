import streamlit as st
import tempfile
import os
import json
from pathlib import Path

# --- Page Config ---
st.set_page_config(
    page_title="QuickStudy Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg: #0d0f1a;
    --surface: #161827;
    --surface2: #1e2035;
    --accent: #7c6af7;
    --accent2: #a78bfa;
    --text: #e8e9f0;
    --muted: #8b8fa8;
    --success: #34d399;
    --warning: #fbbf24;
    --border: rgba(124, 106, 247, 0.2);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Headings */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Hero */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c6af7, #a78bfa, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* Step badges */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 2rem;
    padding: 0.35rem 1rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent2);
    font-family: 'Syne', sans-serif;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Streamlit widgets override */
.stFileUploader > div {
    background: var(--surface2) !important;
    border: 1.5px dashed var(--accent) !important;
    border-radius: 0.75rem !important;
}
.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0.6rem !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    background: linear-gradient(135deg, #7c6af7, #a78bfa) !important;
    color: white !important;
    border: none !important;
    border-radius: 0.6rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.2s !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Result boxes */
.result-box {
    background: var(--surface2);
    border-left: 3px solid var(--accent);
    border-radius: 0 0.75rem 0.75rem 0;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    line-height: 1.7;
}
.result-box h4 {
    font-family: 'Syne', sans-serif;
    color: var(--accent2);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

/* Quiz item */
.quiz-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.quiz-q {
    font-weight: 500;
    margin-bottom: 0.4rem;
    color: var(--text);
}
.quiz-a {
    font-size: 0.88rem;
    color: var(--success);
    font-style: italic;
}

/* Status tag */
.tag-ok  { background:#1a3a2e; color:#34d399; border:1px solid #34d399; border-radius:0.4rem; padding:0.2rem 0.6rem; font-size:0.78rem; font-weight:600; }
.tag-err { background:#3a1a1a; color:#f87171; border:1px solid #f87171; border-radius:0.4rem; padding:0.2rem 0.6rem; font-size:0.78rem; font-weight:600; }

/* Divider */
.divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* Spinner text */
.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    import fitz  # PyMuPDF
    text_parts = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def build_faiss_index(text: str):
    """Chunk text and build a FAISS index with sentence-transformers embeddings."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.create_documents([text])

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    index = FAISS.from_documents(chunks, embeddings)
    return index


def retrieve_context(index, query: str, k: int = 5) -> str:
    """Return the top-k most relevant chunks for a query."""
    docs = index.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content for d in docs)


def transcribe_audio(audio_bytes: bytes, filename: str, groq_client) -> str:
    """Transcribe audio using Groq Whisper."""
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(filename).suffix or ".wav"
    ) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                file=(Path(tmp_path).name, f.read()),
                model="whisper-large-v3-turbo",
                response_format="text",
            )
        return transcription if isinstance(transcription, str) else transcription.text
    finally:
        os.unlink(tmp_path)


def ask_groq(groq_client, system_prompt: str, user_prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """Call Groq chat completions."""
    response = groq_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=2048,
    )
    return response.choices[0].message.content


SYSTEM_STUDY = """Eres QuickStudy, un asistente de estudio experto y conciso.
Respondes SIEMPRE en el mismo idioma de la pregunta del usuario.
Recibes fragmentos de un documento de estudio y una pregunta del alumno.
Tu respuesta tiene DOS partes con estos títulos exactos:
### 📌 Resumen
(3-5 puntos clave, concisos, en bullets)

### ❓ Cuestionario rápido
(Exactamente 3 preguntas con sus respuestas en formato:
**P1:** pregunta
**R:** respuesta breve)

Solo usa la información del contexto proporcionado. Si no hay información suficiente, indícalo.
"""

# ─── App State ────────────────────────────────────────────────────────────────

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "result" not in st.session_state:
    st.session_state.result = None
if "transcription" not in st.session_state:
    st.session_state.transcription = None


# ─── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-title">QuickStudy Assistant</div>
    <div class="hero-sub">Sube tus apuntes · Pregunta por voz · Recibe un resumen y cuestionario al instante</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: API Key ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Obtén tu clave gratuita en console.groq.com",
    )
    st.markdown("---")
    st.markdown("**Modelos usados**")
    st.markdown("🎙️ `whisper-large-v3-turbo`  \n🧠 `llama-3.3-70b-versatile`  \n📐 `paraphrase-multilingual-MiniLM-L12-v2`")
    st.markdown("---")
    st.markdown("**Stack**  \nGroq · LangChain · FAISS  \nPyMuPDF · HuggingFace")

# ── Main columns ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    # Step 1 — PDF
    st.markdown('<div class="step-badge">📄 Paso 1 — Documento</div>', unsafe_allow_html=True)
    pdf_file = st.file_uploader(
        "Sube tus apuntes en PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if pdf_file:
        if st.session_state.pdf_name != pdf_file.name:
            with st.spinner("Indexando el PDF…"):
                pdf_bytes = pdf_file.read()
                raw_text = extract_text_from_pdf(pdf_bytes)
                st.session_state.faiss_index = build_faiss_index(raw_text)
                st.session_state.pdf_name = pdf_file.name
                st.session_state.result = None
                st.session_state.transcription = None

        chars = len(extract_text_from_pdf(pdf_file.read())) if pdf_file else 0
        st.markdown(
            f'<span class="tag-ok">✓ {pdf_file.name}</span>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Step 2 — Audio / Text question
    st.markdown('<div class="step-badge">🎙️ Paso 2 — Tu pregunta</div>', unsafe_allow_html=True)

    audio_file = st.file_uploader(
        "Sube una nota de voz (mp3, wav, m4a, ogg, webm)",
        type=["mp3", "wav", "m4a", "ogg", "webm", "flac"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<p style="text-align:center;color:var(--muted);font-size:0.85rem;margin:0.5rem 0;">— o escribe tu pregunta —</p>',
        unsafe_allow_html=True,
    )
    text_question = st.text_area(
        "Pregunta escrita",
        placeholder="Ej: ¿Cuál es la idea principal del capítulo 2?",
        height=90,
        label_visibility="collapsed",
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Run button
    run_disabled = not groq_api_key or st.session_state.faiss_index is None or (not audio_file and not text_question.strip())

    if st.button("🚀 Analizar y resumir", disabled=run_disabled):
        from groq import Groq
        groq_client = Groq(api_key=groq_api_key)

        # Transcribe if audio provided
        question = text_question.strip()
        if audio_file:
            with st.spinner("Transcribiendo tu nota de voz…"):
                question = transcribe_audio(audio_file.read(), audio_file.name, groq_client)
                st.session_state.transcription = question

        if not question:
            st.warning("No se detectó texto en el audio. Escribe tu pregunta manualmente.")
        else:
            # RAG retrieval
            with st.spinner("Buscando en el documento…"):
                context = retrieve_context(st.session_state.faiss_index, question)

            # LLM call
            with st.spinner("Generando resumen y cuestionario…"):
                user_prompt = f"PREGUNTA DEL ALUMNO:\n{question}\n\nFRAGMENTOS DEL DOCUMENTO:\n{context}"
                answer = ask_groq(groq_client, SYSTEM_STUDY, user_prompt)
                st.session_state.result = {"question": question, "answer": answer}

    # Hints when button is disabled
    if not groq_api_key:
        st.caption("⬅️ Ingresa tu Groq API Key en el panel lateral.")
    elif st.session_state.faiss_index is None:
        st.caption("📄 Primero sube un PDF.")
    elif not audio_file and not text_question.strip():
        st.caption("🎙️ Sube una nota de voz o escribe tu pregunta.")


# ── Results column ────────────────────────────────────────────────────────────
with col2:
    st.markdown('<div class="step-badge">✨ Paso 3 — Resultados</div>', unsafe_allow_html=True)

    if st.session_state.result:
        result = st.session_state.result

        # Show transcription if from audio
        if st.session_state.transcription:
            st.markdown(
                f'<div class="result-box"><h4>🎙️ Transcripción</h4>{st.session_state.transcription}</div>',
                unsafe_allow_html=True,
            )

        # Parse and render answer
        answer_md = result["answer"]

        # Split into summary and quiz sections
        if "### 📌 Resumen" in answer_md and "### ❓ Cuestionario rápido" in answer_md:
            parts = answer_md.split("### ❓ Cuestionario rápido")
            summary_part = parts[0].replace("### 📌 Resumen", "").strip()
            quiz_part = parts[1].strip() if len(parts) > 1 else ""

            st.markdown('<div class="result-box"><h4>📌 Resumen</h4>', unsafe_allow_html=True)
            st.markdown(summary_part)
            st.markdown('</div>', unsafe_allow_html=True)

            if quiz_part:
                st.markdown('<div class="result-box"><h4>❓ Cuestionario rápido</h4>', unsafe_allow_html=True)
                st.markdown(quiz_part)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Fallback: render as-is
            st.markdown(
                f'<div class="result-box">{answer_md}</div>',
                unsafe_allow_html=True,
            )

        # Download button
        st.download_button(
            label="⬇️ Descargar resultado (.txt)",
            data=f"PREGUNTA:\n{result['question']}\n\n{result['answer']}",
            file_name="quickstudy_resultado.txt",
            mime="text/plain",
        )

    else:
        st.markdown("""
<div style="
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    min-height:340px; opacity:0.4; text-align:center; gap:1rem;
">
    <div style="font-size:3.5rem;">🎓</div>
    <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;">
        Tus resultados aparecerán aquí
    </div>
    <div style="font-size:0.88rem; max-width:260px; line-height:1.6;">
        Sube un PDF y hazle una pregunta por voz o texto para comenzar.
    </div>
</div>
""", unsafe_allow_html=True)
