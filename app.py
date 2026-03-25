import streamlit as st
import tempfile
import os
from pathlib import Path

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuickStudy Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg:      #0d0f1a;
    --surface: #161827;
    --surface2:#1e2035;
    --accent:  #7c6af7;
    --accent2: #a78bfa;
    --text:    #e8e9f0;
    --muted:   #8b8fa8;
    --success: #34d399;
    --border:  rgba(124,106,247,0.2);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background-color: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

.hero { text-align:center; padding:2rem 1rem 1rem; }
.hero-title {
    font-family:'Syne',sans-serif; font-size:2.8rem; font-weight:800;
    background:linear-gradient(135deg,#7c6af7,#a78bfa,#c4b5fd);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; line-height:1.1; margin-bottom:0.4rem;
}
.hero-sub { font-size:1rem; color:var(--muted); font-weight:300; }

.step-badge {
    display:inline-flex; align-items:center; gap:0.4rem;
    background:var(--surface2); border:1px solid var(--border);
    border-radius:2rem; padding:0.3rem 0.9rem;
    font-size:0.78rem; font-weight:600; color:var(--accent2);
    font-family:'Syne',sans-serif; letter-spacing:0.05em;
    text-transform:uppercase; margin-bottom:0.6rem;
}

/* inputs */
.stFileUploader > div {
    background:var(--surface2) !important;
    border:1.5px dashed var(--accent) !important;
    border-radius:0.75rem !important;
}
.stTextInput input, .stTextArea textarea {
    background:var(--surface2) !important;
    border:1px solid var(--border) !important;
    border-radius:0.6rem !important;
    color:var(--text) !important;
    font-family:'DM Sans',sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.25) !important;
}

/* button */
.stButton > button {
    background:linear-gradient(135deg,#7c6af7,#a78bfa) !important;
    color:white !important; border:none !important;
    border-radius:0.6rem !important;
    font-family:'Syne',sans-serif !important; font-weight:700 !important;
    font-size:0.95rem !important; padding:0.65rem 1.5rem !important;
    letter-spacing:0.03em !important; width:100%;
}
.stButton > button:disabled { opacity:0.4 !important; cursor:not-allowed !important; }

/* result boxes */
.result-box {
    background:var(--surface2); border-left:3px solid var(--accent);
    border-radius:0 0.75rem 0.75rem 0;
    padding:1.25rem 1.5rem; margin-bottom:1rem; line-height:1.7;
}
.result-box h4 {
    font-family:'Syne',sans-serif; color:var(--accent2);
    font-size:0.82rem; text-transform:uppercase;
    letter-spacing:0.08em; margin-bottom:0.5rem;
}

/* tags */
.tag-ok   { background:#1a3a2e; color:#34d399; border:1px solid #34d399; border-radius:0.4rem; padding:0.2rem 0.6rem; font-size:0.78rem; font-weight:600; display:inline-block; margin:0.15rem 0.2rem; }
.tag-warn { background:#3a2e1a; color:#fbbf24; border:1px solid rgba(251,191,36,0.5); border-radius:0.4rem; padding:0.25rem 0.75rem; font-size:0.8rem; display:inline-block; }

.limit-banner {
    background:rgba(251,191,36,0.08); border:1px solid rgba(251,191,36,0.3);
    border-radius:0.6rem; padding:0.5rem 0.9rem;
    font-size:0.8rem; color:#fbbf24; margin-bottom:0.75rem;
}
.api-banner {
    background:rgba(124,106,247,0.08); border:1px solid rgba(124,106,247,0.3);
    border-radius:0.6rem; padding:0.5rem 0.9rem;
    font-size:0.8rem; color:var(--accent2); margin-bottom:0.5rem;
}
.divider { border:none; border-top:1px solid var(--border); margin:1.25rem 0; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    import fitz
    if not pdf_bytes:
        return ""
    try:
        parts = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                parts.append(page.get_text())
        return "\n".join(parts)
    except Exception as e:
        st.error(f"Error leyendo PDF: {e}")
        return ""


def build_faiss_index(text: str):
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
    suffix = Path(filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            result = groq_client.audio.transcriptions.create(
                file=(Path(tmp_path).name, f.read()),
                model="whisper-large-v3-turbo",
                response_format="text",
            )
        return result if isinstance(result, str) else result.text
    finally:
        os.unlink(tmp_path)


def ask_groq(groq_client, system_prompt: str, user_prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
Recibes fragmentos de un documento y una pregunta del alumno.
Tu respuesta tiene DOS partes con estos títulos exactos:

### 📌 Resumen
(3-5 puntos clave en bullets)

### ❓ Cuestionario rápido
(Exactamente 3 preguntas con respuestas:
**P1:** pregunta
**R:** respuesta breve)

Solo usa la información del contexto. Si no hay suficiente, indícalo.
"""

MAX_FILES     = 5
MAX_MB_EACH   = 200
WARN_MB_TOTAL = 50

# ─── Session State ────────────────────────────────────────────────────────────
for _k, _v in [
    ("faiss_index",   None),
    ("pdf_key",       ""),
    ("result",        None),
    ("transcription", None),
    ("groq_api_key",  ""),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">QuickStudy Assistant</div>
    <div class="hero-sub">Sube tus apuntes · Pregunta por voz o texto · Recibe resumen + cuestionario</div>
</div>
""", unsafe_allow_html=True)

# ─── API Key (TOP LEVEL — always visible) ─────────────────────────────────────
st.markdown('<div class="api-banner">🔑 <strong>Paso 0:</strong> Ingresa tu Groq API Key para comenzar — <a href="https://console.groq.com" target="_blank" style="color:var(--accent2);">console.groq.com</a> (capa gratuita)</div>', unsafe_allow_html=True)

api_input = st.text_input(
    "Groq API Key",
    type="password",
    placeholder="gsk_...",
    value=st.session_state.groq_api_key,
    label_visibility="collapsed",
)
# Persist in session so it survives reruns triggered by other widgets
if api_input:
    st.session_state.groq_api_key = api_input

groq_api_key = st.session_state.groq_api_key

if groq_api_key:
    st.markdown('<span class="tag-ok">✓ API Key ingresada</span>', unsafe_allow_html=True)
else:
    st.caption("⚠️ Sin API Key el botón de análisis no funcionará.")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─── Columns ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

# ══ LEFT: Inputs ══════════════════════════════════════════════════════════════
with col1:

    # ── Step 1: PDFs ──────────────────────────────────────────────────────────
    st.markdown('<div class="step-badge">📄 Paso 1 — Documentos PDF</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="limit-banner">
    ⚠️ Máx. <strong>{MAX_FILES} archivos</strong> · <strong>{MAX_MB_EACH} MB por archivo</strong>
    (límite de Streamlit Cloud). PDFs escaneados sin OCR pueden dar resultados limitados.
</div>
""", unsafe_allow_html=True)

    pdf_files = st.file_uploader(
        f"Sube tus apuntes (hasta {MAX_FILES} PDFs)",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if pdf_files and len(pdf_files) > MAX_FILES:
        st.warning(f"Se usarán solo los primeros {MAX_FILES} archivos.")
        pdf_files = pdf_files[:MAX_FILES]

    pdf_key = "|".join(
        f"{f.name}:{f.size}" for f in sorted(pdf_files, key=lambda x: x.name)
    ) if pdf_files else ""

    if pdf_files:
        total_mb = sum(f.size for f in pdf_files) / (1024 * 1024)
        if total_mb > WARN_MB_TOTAL:
            st.markdown(
                f'<span class="tag-warn">⏳ {total_mb:.1f} MB total — indexación puede tardar 1-2 min</span>',
                unsafe_allow_html=True,
            )

        if st.session_state.pdf_key != pdf_key:
            with st.status("Indexando documentos…", expanded=True) as s:
                all_parts = []
                for f in pdf_files:
                    st.write(f"📄 Leyendo {f.name}…")
                    raw = f.read()          # read ONCE — bytes kept in memory
                    txt = extract_text_from_pdf(raw)
                    if txt.strip():
                        all_parts.append(txt)
                        st.write(f"✅ {f.name} — {len(txt):,} caracteres extraídos")
                    else:
                        st.write(f"⚠️ {f.name} — sin texto (¿escaneado?)")

                combined = "\n\n".join(all_parts)
                if combined.strip():
                    st.write("🔧 Construyendo índice vectorial…")
                    st.session_state.faiss_index  = build_faiss_index(combined)
                    st.session_state.pdf_key       = pdf_key
                    st.session_state.result        = None
                    st.session_state.transcription = None
                    s.update(label="✅ Documentos indexados", state="complete", expanded=False)
                else:
                    s.update(label="❌ No se extrajo texto", state="error")
                    st.error("Ningún PDF tenía texto extraíble.")

        if st.session_state.faiss_index is not None:
            tags = "".join(f'<span class="tag-ok">✓ {f.name}</span>' for f in pdf_files)
            st.markdown(tags, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Step 2: Question ──────────────────────────────────────────────────────
    st.markdown('<div class="step-badge">🎙️ Paso 2 — Tu pregunta</div>', unsafe_allow_html=True)

    audio_file = st.file_uploader(
        "Nota de voz (mp3, wav, m4a, ogg, webm, flac) — opcional",
        type=["mp3", "wav", "m4a", "ogg", "webm", "flac"],
        label_visibility="collapsed",
    )
    if audio_file:
        st.markdown(f'<span class="tag-ok">✓ Audio: {audio_file.name}</span>', unsafe_allow_html=True)

    st.markdown(
        '<p style="text-align:center;color:var(--muted);font-size:0.83rem;margin:0.6rem 0 0.4rem;">— o escribe tu pregunta directamente —</p>',
        unsafe_allow_html=True,
    )
    text_question = st.text_area(
        "Pregunta",
        placeholder="Ej: ¿Cuál es la idea principal del capítulo 2?",
        height=90,
        label_visibility="collapsed",
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Run ───────────────────────────────────────────────────────────────────
    ready = (
        bool(groq_api_key)
        and st.session_state.faiss_index is not None
        and (bool(audio_file) or bool(text_question.strip()))
    )

    if not groq_api_key:
        st.caption("🔑 Ingresa tu Groq API Key arriba.")
    elif st.session_state.faiss_index is None:
        st.caption("📄 Sube al menos un PDF (Paso 1).")
    elif not audio_file and not text_question.strip():
        st.caption("🎙️ Sube un audio o escribe tu pregunta (Paso 2).")

    if st.button("🚀 Analizar y resumir", disabled=not ready):
        from groq import Groq
        client = Groq(api_key=groq_api_key)

        with st.status("Procesando tu consulta…", expanded=True) as s:

            # 1. Transcribe if audio
            question = text_question.strip()
            if audio_file:
                st.write("🎙️ Transcribiendo nota de voz con Whisper…")
                try:
                    question = transcribe_audio(audio_file.read(), audio_file.name, client)
                    st.session_state.transcription = question
                    st.write(f"✅ Transcripción: *{question[:120]}{'…' if len(question)>120 else ''}*")
                except Exception as e:
                    s.update(label="❌ Error en transcripción", state="error")
                    st.error(f"Whisper falló: {e}")
                    st.stop()
            else:
                st.session_state.transcription = None

            if not question:
                s.update(label="❌ Sin pregunta", state="error")
                st.error("No se detectó texto en el audio. Escribe tu pregunta manualmente.")
                st.stop()

            # 2. RAG retrieval
            st.write("🔍 Buscando fragmentos relevantes en el documento…")
            context = retrieve_context(st.session_state.faiss_index, question)

            # 3. LLM
            st.write("🧠 Generando resumen y cuestionario con LLaMA 3.3 70B…")
            try:
                user_prompt = f"PREGUNTA DEL ALUMNO:\n{question}\n\nFRAGMENTOS DEL DOCUMENTO:\n{context}"
                answer = ask_groq(client, SYSTEM_STUDY, user_prompt)
                st.session_state.result = {"question": question, "answer": answer}
                s.update(label="✅ ¡Listo! Revisa los resultados →", state="complete", expanded=False)
            except Exception as e:
                s.update(label="❌ Error en LLM", state="error")
                st.error(f"Groq LLM falló: {e}")


# ══ RIGHT: Results ════════════════════════════════════════════════════════════
with col2:
    st.markdown('<div class="step-badge">✨ Paso 3 — Resultados</div>', unsafe_allow_html=True)

    if st.session_state.result:
        result = st.session_state.result

        if st.session_state.transcription:
            st.markdown(
                f'<div class="result-box"><h4>🎙️ Pregunta transcrita</h4>{st.session_state.transcription}</div>',
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
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
            min-height:360px;opacity:0.35;text-align:center;gap:1rem;">
    <div style="font-size:3.5rem;">🎓</div>
    <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;">
        Tus resultados aparecerán aquí
    </div>
    <div style="font-size:0.85rem;max-width:240px;line-height:1.6;">
        Completa los pasos 0 → 1 → 2 y presiona el botón.
    </div>
</div>
""", unsafe_allow_html=True)

    # Stack info at bottom
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.75rem;color:var(--muted);text-align:center;">'
        '🎙️ Whisper large-v3-turbo &nbsp;·&nbsp; 🧠 LLaMA 3.3 70B &nbsp;·&nbsp; '
        '📐 paraphrase-multilingual-MiniLM-L12-v2 &nbsp;·&nbsp; FAISS · LangChain · PyMuPDF'
        '</p>',
        unsafe_allow_html=True,
    )
