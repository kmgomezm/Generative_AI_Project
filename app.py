import streamlit as st
import tempfile
import os
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

#MainMenu, footer, header { visibility: hidden; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

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

.tag-ok   { background:#1a3a2e; color:#34d399; border:1px solid #34d399; border-radius:0.4rem; padding:0.2rem 0.6rem; font-size:0.78rem; font-weight:600; display:inline-block; margin:0.15rem 0.2rem; }
.tag-err  { background:#3a1a1a; color:#f87171; border:1px solid #f87171; border-radius:0.4rem; padding:0.2rem 0.6rem; font-size:0.78rem; font-weight:600; }
.tag-warn { background:#3a2e1a; color:#fbbf24; border:1px solid rgba(251,191,36,0.5); border-radius:0.4rem; padding:0.25rem 0.75rem; font-size:0.8rem; display:inline-block; }

.divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
.stSpinner > div { border-top-color: var(--accent) !important; }

.limit-banner {
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.35);
    border-radius: 0.6rem;
    padding: 0.55rem 1rem;
    font-size: 0.82rem;
    color: #fbbf24;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF using PyMuPDF. Returns empty string on failure."""
    import fitz
    if not pdf_bytes:
        return ""
    try:
        text_parts = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text_parts.append(page.get_text())
        return "\n".join(text_parts)
    except Exception as e:
        st.error(f"Error leyendo PDF: {e}")
        return ""


def build_faiss_index(text: str):
    """Chunk text and build a FAISS index with multilingual embeddings."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.create_documents([text])

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    return FAISS.from_documents(chunks, embeddings)


def retrieve_context(index, query: str, k: int = 5) -> str:
    docs = index.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content for d in docs)


def transcribe_audio(audio_bytes: bytes, filename: str, groq_client) -> str:
    """Transcribe audio using Groq Whisper."""
    suffix = Path(filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
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


def ask_groq(groq_client, system_prompt: str, user_prompt: str,
             model: str = "llama-3.3-70b-versatile") -> str:
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

MAX_FILES     = 5
MAX_MB_EACH   = 200   # Streamlit Cloud hard limit per file
WARN_MB_TOTAL = 50    # Soft warning for slow indexing

# ─── Session State ────────────────────────────────────────────────────────────
for _key, _default in [
    ("faiss_index",   None),
    ("pdf_key",       ""),
    ("result",        None),
    ("transcription", None),
]:
    if _key not in st.session_state:
        st.session_state[_key] = _default


# ─── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-title">QuickStudy Assistant</div>
    <div class="hero-sub">Sube tus apuntes · Pregunta por voz · Recibe un resumen y cuestionario al instante</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Obtén tu clave gratuita en console.groq.com",
    )
    st.markdown("---")
    st.markdown("**Modelos**")
    st.markdown("🎙️ `whisper-large-v3-turbo`  \n🧠 `llama-3.3-70b-versatile`  \n📐 `paraphrase-multilingual-MiniLM-L12-v2`")
    st.markdown("---")
    st.markdown("**Stack**  \nGroq · LangChain · FAISS  \nPyMuPDF · HuggingFace")

# ── Columns ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:

    # ── Step 1: PDFs ──────────────────────────────────────────────────────────
    st.markdown('<div class="step-badge">📄 Paso 1 — Documentos</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="limit-banner">
    ⚠️ <strong>Límites de carga:</strong> máx. <strong>{MAX_FILES} archivos</strong>
    · <strong>{MAX_MB_EACH} MB por archivo</strong> (límite de Streamlit Cloud).
    PDFs escaneados sin capa de texto pueden dar resultados limitados.
</div>
""", unsafe_allow_html=True)

    pdf_files = st.file_uploader(
        f"Sube tus apuntes en PDF (hasta {MAX_FILES} archivos)",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Enforce max files
    if pdf_files and len(pdf_files) > MAX_FILES:
        st.warning(f"Seleccionaste {len(pdf_files)} archivos. Solo se procesarán los primeros {MAX_FILES}.")
        pdf_files = pdf_files[:MAX_FILES]

    # Cache key = sorted "name:size" — detects any file change without re-reading bytes
    pdf_key = "|".join(
        f"{f.name}:{f.size}" for f in sorted(pdf_files, key=lambda x: x.name)
    ) if pdf_files else ""

    if pdf_files:
        total_mb = sum(f.size for f in pdf_files) / (1024 * 1024)

        if total_mb > WARN_MB_TOTAL:
            st.markdown(
                f'<span class="tag-warn">⏳ {total_mb:.1f} MB en total — la indexación puede tardar unos minutos</span>',
                unsafe_allow_html=True,
            )

        # Re-index only when the set of files actually changes
        if st.session_state.pdf_key != pdf_key:
            with st.spinner(f"Indexando {len(pdf_files)} PDF(s)…"):
                all_text_parts = []
                for f in pdf_files:
                    raw = f.read()          # ← read ONCE per file; bytes stored in memory
                    txt = extract_text_from_pdf(raw)
                    if txt.strip():
                        all_text_parts.append(txt)
                    else:
                        st.warning(f"⚠️ No se extrajo texto de **{f.name}** (¿PDF escaneado sin OCR?).")

                combined_text = "\n\n".join(all_text_parts)
                if combined_text.strip():
                    st.session_state.faiss_index   = build_faiss_index(combined_text)
                    st.session_state.pdf_key        = pdf_key
                    st.session_state.result         = None
                    st.session_state.transcription  = None
                else:
                    st.error("No se pudo extraer texto de ningún PDF.")

        # Show one green tag per indexed file (no second read needed)
        tags_html = "".join(f'<span class="tag-ok">✓ {f.name}</span>' for f in pdf_files)
        st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Step 2: Question ──────────────────────────────────────────────────────
    st.markdown('<div class="step-badge">🎙️ Paso 2 — Tu pregunta</div>', unsafe_allow_html=True)

    audio_file = st.file_uploader(
        "Nota de voz (mp3, wav, m4a, ogg, webm, flac)",
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

    # ── Run button ────────────────────────────────────────────────────────────
    run_disabled = (
        not groq_api_key
        or st.session_state.faiss_index is None
        or (not audio_file and not text_question.strip())
    )

    if st.button("🚀 Analizar y resumir", disabled=run_disabled):
        from groq import Groq
        groq_client = Groq(api_key=groq_api_key)

        question = text_question.strip()

        if audio_file:
            with st.spinner("Transcribiendo nota de voz…"):
                question = transcribe_audio(audio_file.read(), audio_file.name, groq_client)
                st.session_state.transcription = question

        if not question:
            st.warning("No se detectó texto en el audio. Escribe tu pregunta manualmente.")
        else:
            with st.spinner("Buscando fragmentos relevantes…"):
                context = retrieve_context(st.session_state.faiss_index, question)

            with st.spinner("Generando resumen y cuestionario…"):
                user_prompt = f"PREGUNTA DEL ALUMNO:\n{question}\n\nFRAGMENTOS DEL DOCUMENTO:\n{context}"
                answer = ask_groq(groq_client, SYSTEM_STUDY, user_prompt)
                st.session_state.result = {"question": question, "answer": answer}

    # Helper hints
    if not groq_api_key:
        st.caption("⬅️ Ingresa tu Groq API Key en el panel lateral.")
    elif st.session_state.faiss_index is None:
        st.caption("📄 Primero sube al menos un PDF.")
    elif not audio_file and not text_question.strip():
        st.caption("🎙️ Sube una nota de voz o escribe tu pregunta.")


# ── Results column ────────────────────────────────────────────────────────────
with col2:
    st.markdown('<div class="step-badge">✨ Paso 3 — Resultados</div>', unsafe_allow_html=True)

    if st.session_state.result:
        result = st.session_state.result

        if st.session_state.transcription:
            st.markdown(
                f'<div class="result-box"><h4>🎙️ Transcripción</h4>{st.session_state.transcription}</div>',
                unsafe_allow_html=True,
            )

        answer_md = result["answer"]

        if "### 📌 Resumen" in answer_md and "### ❓ Cuestionario rápido" in answer_md:
            parts        = answer_md.split("### ❓ Cuestionario rápido")
            summary_part = parts[0].replace("### 📌 Resumen", "").strip()
            quiz_part    = parts[1].strip() if len(parts) > 1 else ""

            st.markdown('<div class="result-box"><h4>📌 Resumen</h4>', unsafe_allow_html=True)
            st.markdown(summary_part)
            st.markdown('</div>', unsafe_allow_html=True)

            if quiz_part:
                st.markdown('<div class="result-box"><h4>❓ Cuestionario rápido</h4>', unsafe_allow_html=True)
                st.markdown(quiz_part)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-box">{answer_md}</div>', unsafe_allow_html=True)

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
