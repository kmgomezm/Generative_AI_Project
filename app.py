import streamlit as st
import tempfile
import os
import base64
from pathlib import Path
import re

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuickStudy Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS (igual que antes, pero lo incluyo completo para evitar errores) ───
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
    --error:   #f87171;
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

.hero { text-align:center; padding:1.8rem 1rem 0.8rem; }
.hero-title {
    font-family:'Syne',sans-serif; font-size:2.6rem; font-weight:800;
    background:linear-gradient(135deg,#7c6af7,#a78bfa,#c4b5fd);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; line-height:1.1; margin-bottom:0.3rem;
}
.hero-sub { font-size:0.95rem; color:var(--muted); font-weight:300; }

.step-badge {
    display:inline-flex; align-items:center; gap:0.4rem;
    background:var(--surface2); border:1px solid var(--border);
    border-radius:2rem; padding:0.3rem 0.9rem;
    font-size:0.76rem; font-weight:600; color:var(--accent2);
    font-family:'Syne',sans-serif; letter-spacing:0.05em;
    text-transform:uppercase; margin-bottom:0.6rem;
}

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
    border-color:var(--accent) !important;
    box-shadow:0 0 0 2px rgba(124,106,247,0.25) !important;
}

.stButton > button {
    background:linear-gradient(135deg,#7c6af7,#a78bfa) !important;
    color:white !important; border:none !important;
    border-radius:0.6rem !important;
    font-family:'Syne',sans-serif !important; font-weight:700 !important;
    font-size:0.92rem !important; padding:0.6rem 1.2rem !important;
    letter-spacing:0.03em !important; width:100%;
}
.stButton > button:disabled { opacity:0.35 !important; }

.result-box {
    background:var(--surface2); border-left:3px solid var(--accent);
    border-radius:0 0.75rem 0.75rem 0;
    padding:1.1rem 1.4rem; margin-bottom:0.9rem; line-height:1.7;
}
.result-box h4 {
    font-family:'Syne',sans-serif; color:var(--accent2);
    font-size:0.8rem; text-transform:uppercase;
    letter-spacing:0.08em; margin-bottom:0.45rem;
}

.quiz-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:0.85rem; padding:1rem 1.2rem; margin-bottom:0.8rem;
}
.quiz-num {
    font-family:'Syne',sans-serif; font-size:0.72rem;
    color:var(--accent2); text-transform:uppercase; letter-spacing:0.07em;
    margin-bottom:0.3rem;
}
.quiz-q { font-weight:500; font-size:0.97rem; margin-bottom:0.6rem; }

.fb-correct {
    background:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.4);
    border-radius:0.6rem; padding:0.7rem 1rem; margin-top:0.5rem;
    color:#34d399; font-size:0.88rem; line-height:1.6;
}
.fb-wrong {
    background:rgba(248,113,113,0.1); border:1px solid rgba(248,113,113,0.35);
    border-radius:0.6rem; padding:0.7rem 1rem; margin-top:0.5rem;
    color:#fca5a5; font-size:0.88rem; line-height:1.6;
}
.fb-partial {
    background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.35);
    border-radius:0.6rem; padding:0.7rem 1rem; margin-top:0.5rem;
    color:#fde68a; font-size:0.88rem; line-height:1.6;
}

.score-bar-wrap {
    background:var(--surface2); border-radius:0.5rem;
    height:10px; margin:0.5rem 0; overflow:hidden;
}
.score-bar-fill {
    height:100%; border-radius:0.5rem;
    background:linear-gradient(90deg,#7c6af7,#34d399);
    transition:width 0.6s ease;
}

.tag-ok   { background:#1a3a2e;color:#34d399;border:1px solid #34d399;border-radius:0.4rem;padding:0.18rem 0.55rem;font-size:0.76rem;font-weight:600;display:inline-block;margin:0.12rem 0.15rem; }
.tag-warn { background:#3a2e1a;color:#fbbf24;border:1px solid rgba(251,191,36,0.5);border-radius:0.4rem;padding:0.22rem 0.65rem;font-size:0.78rem;display:inline-block; }

.limit-banner {
    background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.3);
    border-radius:0.6rem;padding:0.45rem 0.85rem;
    font-size:0.78rem;color:#fbbf24;margin-bottom:0.7rem;
}
.api-banner {
    background:rgba(124,106,247,0.08);border:1px solid rgba(124,106,247,0.3);
    border-radius:0.6rem;padding:0.45rem 0.85rem;
    font-size:0.78rem;color:var(--accent2);margin-bottom:0.5rem;
}
.divider { border:none;border-top:1px solid var(--border);margin:1.1rem 0; }
.tts-banner {
    background:rgba(52,211,153,0.07);border:1px solid rgba(52,211,153,0.25);
    border-radius:0.6rem;padding:0.45rem 0.85rem;
    font-size:0.78rem;color:#34d399;margin-bottom:0.5rem;
}

.recorder-wrap {
    background:var(--surface2); border:1.5px solid var(--border);
    border-radius:0.85rem; padding:1rem; text-align:center;
    margin-bottom:0.75rem;
}

.stTabs [data-baseweb="tab-list"] {
    background:var(--surface2) !important;
    border-radius:0.7rem !important;
    padding:0.2rem !important;
    gap:0.2rem !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important;
    color:var(--muted) !important;
    border-radius:0.5rem !important;
    font-family:'Syne',sans-serif !important;
    font-size:0.82rem !important;
    font-weight:600 !important;
}
.stTabs [aria-selected="true"] {
    background:var(--accent) !important;
    color:white !important;
}
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


def generate_tts_audio(groq_client, text: str) -> bytes:
    """Generate speech from text using Groq Orpheus TTS."""
    import re
    # Strip markdown symbols for cleaner audio
    clean = re.sub(r'[#*`_~•]', '', text)
    clean = re.sub(r'\n+', '. ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    response = groq_client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice="diana",   # <--- CORRECCIÓN: voz válida
        input=clean[:4000],
        response_format="wav",
    )
    return response.read()


def play_audio_bytes(audio_bytes: bytes, label: str = "🔊 Escuchar resumen"):
    """Embed audio player inline."""
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""
        <div class="tts-banner">
            {label} ↓
        </div>
        <audio controls style="width:100%;border-radius:0.6rem;margin-bottom:0.5rem;">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True,
    )


def parse_quiz(answer_md: str) -> tuple[str, list[dict]]:
    """
    Parse LLM output into (summary_text, list_of_questions).
    Each question dict: {num, question, answer}
    """
    summary = ""
    questions = []

    if "### 📌 Resumen" in answer_md and "### ❓ Cuestionario rápido" in answer_md:
        parts = answer_md.split("### ❓ Cuestionario rápido")
        summary = parts[0].replace("### 📌 Resumen", "").strip()
        quiz_raw = parts[1].strip() if len(parts) > 1 else ""
    else:
        return answer_md, []

    # Parse P1/R1 pairs robustly
    import re
    # Match **P1:** ... **R:**
    blocks = re.split(r'\*\*P\d+:\*\*', quiz_raw)
    for i, block in enumerate(blocks[1:], start=1):
        # Split on **R:**
        sub = re.split(r'\*\*R:\*\*', block, maxsplit=1)
        q_text = sub[0].strip().rstrip(':').strip()
        a_text = sub[1].strip().split('\n')[0].strip() if len(sub) > 1 else ""
        if q_text:
            questions.append({"num": i, "question": q_text, "answer": a_text})

    return summary, questions


def generate_quiz_from_context(client, question, context, num_questions=3):
    """
    Genera un cuestionario con `num_questions` preguntas y respuestas,
    basado en la pregunta original y el contexto recuperado.
    """
    system_prompt = f"""Eres QuickStudy, un asistente de estudio experto y conciso.
Respondes SIEMPRE en el mismo idioma de la pregunta del usuario.
Recibes fragmentos de un documento y una pregunta del alumno.
Tu respuesta debe contener EXACTAMENTE {num_questions} preguntas con sus respuestas.
Usa el formato:

### ❓ Cuestionario rápido
**P1:** pregunta
**R:** respuesta breve
**P2:** pregunta
**R:** respuesta breve
... (hasta P{num_questions} y R{num_questions})

Solo usa la información del contexto. Si no hay suficiente, indícalo.
"""
    user_prompt = f"PREGUNTA DEL ALUMNO:\n{question}\n\nFRAGMENTOS DEL DOCUMENTO:\n{context}"
    answer = ask_groq(client, system_prompt, user_prompt)
    # Extraer preguntas
    questions = []
    blocks = re.split(r'\*\*P\d+:\*\*', answer)
    for i, block in enumerate(blocks[1:], start=1):
        if i > num_questions:
            break
        sub = re.split(r'\*\*R:\*\*', block, maxsplit=1)
        q_text = sub[0].strip().rstrip(':').strip()
        a_text = sub[1].strip().split('\n')[0].strip() if len(sub) > 1 else ""
        if q_text:
            questions.append({"num": i, "question": q_text, "answer": a_text})
    return questions


SYSTEM_STUDY = """Eres QuickStudy, un asistente de estudio experto y conciso.
Respondes SIEMPRE en el mismo idioma de la pregunta del usuario.
Recibes fragmentos de un documento y una pregunta del alumno.
Tu respuesta tiene DOS partes con estos títulos exactos:

### 📌 Resumen
(3-5 puntos clave en bullets)

### ❓ Cuestionario rápido
(Exactamente 3 preguntas con respuestas:
**P1:** pregunta
**R:** respuesta breve
**P2:** pregunta
**R:** respuesta breve
**P3:** pregunta
**R:** respuesta breve)

Solo usa la información del contexto. Si no hay suficiente, indícalo.
"""

SYSTEM_GRADER = """Eres un tutor académico que evalúa respuestas de estudiantes con empatía y precisión.
Se te da:
- La pregunta original
- La respuesta correcta de referencia
- La respuesta del estudiante

Evalúa si el estudiante respondió correctamente. Sé justo: no se exige literalidad, solo que la idea sea correcta.

Responde en el mismo idioma del estudiante. Tu respuesta tiene este formato exacto:

VEREDICTO: [CORRECTO / PARCIAL / INCORRECTO]
EXPLICACIÓN: (1-2 oraciones: di qué estuvo bien, qué faltó o qué fue incorrecto)
CONSEJO: (1 oración: cómo mejorar o qué repasar)
"""

MAX_FILES     = 5
MAX_MB_EACH   = 200
WARN_MB_TOTAL = 50

# ─── Session State ────────────────────────────────────────────────────────────
for _k, _v in [
    ("faiss_index",     None),
    ("pdf_key",         ""),
    ("result",          None),
    ("transcription",   None),
    ("groq_api_key",    ""),
    ("summary_text",    ""),
    ("quiz_questions",  []),
    ("quiz_answers",    {}),
    ("quiz_feedback",   {}),
    ("summary_audio",   None),
    ("last_question",   ""),
    ("last_context",    ""),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">QuickStudy Assistant</div>
    <div class="hero-sub">PDF → Pregunta por voz o texto → Resumen · Audio · Cuestionario interactivo</div>
</div>
""", unsafe_allow_html=True)

# ─── API Key ──────────────────────────────────────────────────────────────────
st.markdown('<div class="api-banner">🔑 <strong>Paso 0 — Groq API Key</strong> (gratuita en <a href="https://console.groq.com" target="_blank" style="color:var(--accent2);">console.groq.com</a>)</div>', unsafe_allow_html=True)

api_input = st.text_input(
    "Groq API Key",
    type="password",
    placeholder="gsk_...",
    value=st.session_state.groq_api_key,
    label_visibility="collapsed",
)
if api_input:
    st.session_state.groq_api_key = api_input
groq_api_key = st.session_state.groq_api_key

if groq_api_key:
    st.markdown('<span class="tag-ok">✓ API Key lista</span>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─── Main Layout ──────────────────────────────────────────────────────────────
col_in, col_out = st.columns([1, 1], gap="large")

# ══ LEFT: Inputs ══════════════════════════════════════════════════════════════
with col_in:

    # ── Step 1: PDFs ──────────────────────────────────────────────────────────
    st.markdown('<div class="step-badge">📄 Paso 1 — Documentos PDF</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="limit-banner">⚠️ Máx. <strong>{MAX_FILES} archivos · {MAX_MB_EACH} MB</strong> por archivo · PDFs escaneados sin OCR pueden no funcionar.</div>', unsafe_allow_html=True)

    pdf_files = st.file_uploader(
        f"Sube tus apuntes (hasta {MAX_FILES} PDFs)",
        type=["pdf"], accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if pdf_files and len(pdf_files) > MAX_FILES:
        st.warning(f"Se usarán solo los primeros {MAX_FILES}.")
        pdf_files = pdf_files[:MAX_FILES]

    pdf_key = "|".join(
        f"{f.name}:{f.size}" for f in sorted(pdf_files, key=lambda x: x.name)
    ) if pdf_files else ""

    if pdf_files:
        total_mb = sum(f.size for f in pdf_files) / 1024 / 1024
        if total_mb > WARN_MB_TOTAL:
            st.markdown(f'<span class="tag-warn">⏳ {total_mb:.1f} MB — indexación puede tardar 1-2 min</span>', unsafe_allow_html=True)

        if st.session_state.pdf_key != pdf_key:
            with st.status("Indexando documentos…", expanded=True) as s:
                parts = []
                for f in pdf_files:
                    st.write(f"📄 Leyendo {f.name}…")
                    raw = f.read()
                    txt = extract_text_from_pdf(raw)
                    if txt.strip():
                        parts.append(txt)
                        st.write(f"✅ {f.name} — {len(txt):,} caracteres")
                    else:
                        st.write(f"⚠️ {f.name} — sin texto extraíble")
                combined = "\n\n".join(parts)
                if combined.strip():
                    st.write("🔧 Construyendo índice vectorial FAISS…")
                    st.session_state.faiss_index   = build_faiss_index(combined)
                    st.session_state.pdf_key        = pdf_key
                    st.session_state.result         = None
                    st.session_state.transcription  = None
                    st.session_state.summary_text   = ""
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_answers   = {}
                    st.session_state.quiz_feedback  = {}
                    st.session_state.summary_audio  = None
                    st.session_state.last_question  = ""
                    st.session_state.last_context   = ""
                    s.update(label="✅ Listo", state="complete", expanded=False)
                else:
                    s.update(label="❌ Sin texto extraíble", state="error")

        if st.session_state.faiss_index:
            st.markdown(
                "".join(f'<span class="tag-ok">✓ {f.name}</span>' for f in pdf_files),
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Step 2: Question (recorder + upload + text) ───────────────────────────
    st.markdown('<div class="step-badge">🎙️ Paso 2 — Tu pregunta</div>', unsafe_allow_html=True)

    # --- Audio input (record or upload) ---
    recorded_bytes = None
    rec_audio = st.audio_input("🎙️ Graba tu pregunta (o sube un archivo)")
    if rec_audio:
        recorded_bytes = rec_audio.getvalue()
        st.audio(recorded_bytes, format="audio/wav")
        st.markdown('<span class="tag-ok">✓ Audio listo para enviar</span>', unsafe_allow_html=True)

    st.markdown("— o sube un archivo de audio —")
    uploaded_audio = st.file_uploader(
        "Nota de voz (mp3, wav, m4a, ogg, webm, flac)",
        type=["mp3", "wav", "m4a", "ogg", "webm", "flac"],
        label_visibility="collapsed",
    )
    if uploaded_audio:
        st.markdown(f'<span class="tag-ok">✓ {uploaded_audio.name}</span>', unsafe_allow_html=True)

    st.markdown('<p style="text-align:center;color:var(--muted);font-size:0.82rem;margin:0.5rem 0;">— o escribe directamente —</p>', unsafe_allow_html=True)
    text_question = st.text_area(
        "Pregunta",
        placeholder="Ej: ¿Cuál es la idea principal del capítulo 2?",
        height=80,
        label_visibility="collapsed",
    )

    # Determine what audio to use (recorded takes priority)
    audio_bytes_to_use = None
    audio_name_to_use = ""
    if recorded_bytes:
        audio_bytes_to_use = recorded_bytes
        audio_name_to_use = rec_audio.name  # default name like "audio.wav"
    elif uploaded_audio:
        audio_bytes_to_use = uploaded_audio.read()
        audio_name_to_use = uploaded_audio.name

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── TTS option ────────────────────────────────────────────────────────────
    generate_audio = st.checkbox("🔊 Generar audio del resumen (Groq TTS)", value=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Run ───────────────────────────────────────────────────────────────────
    ready = (
        bool(groq_api_key)
        and st.session_state.faiss_index is not None
        and (bool(audio_bytes_to_use) or bool(text_question.strip()))
    )

    if not groq_api_key:
        st.caption("🔑 Ingresa tu Groq API Key arriba.")
    elif st.session_state.faiss_index is None:
        st.caption("📄 Sube al menos un PDF (Paso 1).")
    elif not audio_bytes_to_use and not text_question.strip():
        st.caption("🎙️ Graba, sube audio o escribe tu pregunta (Paso 2).")

    if st.button("🚀 Analizar y resumir", disabled=not ready):
    from groq import Groq
    client = Groq(api_key=groq_api_key)

    # --- Resetear estados previos ---
    st.session_state.transcription = None
    st.session_state.summary_audio = None  # Limpiar audio anterior

    with st.status("Procesando…", expanded=True) as s:
        # 1. Transcribe
        question = text_question.strip()
        if audio_bytes_to_use:
            st.write("🎙️ Transcribiendo con Whisper…")
            try:
                question = transcribe_audio(audio_bytes_to_use, audio_name_to_use, client)
                st.session_state.transcription = question
                st.write(f"✅ *{question[:100]}{'…' if len(question)>100 else ''}*")
            except Exception as e:
                s.update(label="❌ Error en transcripción", state="error")
                st.error(str(e)); st.stop()
        # else: ya está en None por el reset

        if not question:
            s.update(label="❌ Sin pregunta", state="error")
            st.error("Sin texto para procesar."); st.stop()

        # 2. RAG
        st.write("🔍 Buscando fragmentos relevantes…")
        context = retrieve_context(st.session_state.faiss_index, question)

        # Guardar para regenerar cuestionario después
        st.session_state.last_question = question
        st.session_state.last_context = context

        # 3. LLM para resumen y cuestionario inicial
        st.write("🧠 Generando resumen y cuestionario con LLaMA 3.3 70B…")
        try:
            user_prompt = f"PREGUNTA DEL ALUMNO:\n{question}\n\nFRAGMENTOS DEL DOCUMENTO:\n{context}"
            answer = ask_groq(client, SYSTEM_STUDY, user_prompt)
        except Exception as e:
            s.update(label="❌ Error LLM", state="error")
            st.error(str(e)); st.stop()

        summary, questions = parse_quiz(answer)
        st.session_state.result         = {"question": question, "answer": answer}
        st.session_state.summary_text   = summary
        st.session_state.quiz_questions = questions
        st.session_state.quiz_answers   = {}
        st.session_state.quiz_feedback  = {}

        # 4. TTS (optional)
        if generate_audio and summary:
            st.write("🔊 Generando audio del resumen con Groq TTS…")
            try:
                st.session_state.summary_audio = generate_tts_audio(client, summary)
                st.write("✅ Audio listo")
            except Exception as e:
                st.write(f"⚠️ TTS no disponible: {e}")
                # Dejamos summary_audio como None (no habrá reproductor)
        else:
            # Si no se generó automáticamente, aseguramos que no quede audio antiguo
            st.session_state.summary_audio = None

        s.update(label="✅ ¡Listo! Revisa los resultados →", state="complete", expanded=False)


# ══ RIGHT: Results ════════════════════════════════════════════════════════════
with col_out:
    st.markdown('<div class="step-badge">✨ Paso 3 — Resultados</div>', unsafe_allow_html=True)

    if not st.session_state.result:
        st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
            min-height:360px;opacity:0.32;text-align:center;gap:1rem;">
    <div style="font-size:3.5rem;">🎓</div>
    <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;">
        Tus resultados aparecerán aquí
    </div>
    <div style="font-size:0.83rem;max-width:230px;line-height:1.6;">
        Completa los pasos 0 → 1 → 2 y presiona el botón.
    </div>
</div>""", unsafe_allow_html=True)
    else:
        tab_sum, tab_quiz = st.tabs(["📌 Resumen", "❓ Cuestionario interactivo"])

        # ── Tab 1: Summary ────────────────────────────────────────────────────
        with tab_sum:
            if st.session_state.transcription:
                st.markdown(
                    f'<div class="result-box"><h4>🎙️ Pregunta transcrita</h4>{st.session_state.transcription}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<div class="result-box"><h4>📌 Resumen</h4>', unsafe_allow_html=True)
            st.markdown(st.session_state.summary_text or st.session_state.result["answer"])
            st.markdown('</div>', unsafe_allow_html=True)

            # Audio player
            if st.session_state.summary_audio:
                play_audio_bytes(st.session_state.summary_audio, "🔊 Escuchar resumen")
                st.download_button(
                    "⬇️ Descargar audio (.wav)",
                    data=st.session_state.summary_audio,
                    file_name="resumen_audio.wav",
                    mime="audio/wav",
                )
            elif not st.session_state.summary_audio and st.session_state.groq_api_key:
                if st.button("🔊 Generar audio del resumen ahora"):
                    from groq import Groq
                    client = Groq(api_key=st.session_state.groq_api_key)
                    with st.spinner("Generando audio…"):
                        try:
                            st.session_state.summary_audio = generate_tts_audio(
                                client, st.session_state.summary_text
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"TTS falló: {e}")

            st.download_button(
                "⬇️ Descargar resumen (.txt)",
                data=f"PREGUNTA:\n{st.session_state.result['question']}\n\n{st.session_state.result['answer']}",
                file_name="quickstudy_resumen.txt",
                mime="text/plain",
            )

        # ── Tab 2: Interactive Quiz (con regeneración) ─────────────────────────
        with tab_quiz:
            # Si existe last_question y last_context, mostramos controles para regenerar
            if st.session_state.last_question and st.session_state.last_context:
                with st.expander("🎲 Opciones del cuestionario", expanded=False):
                    num_q = st.slider(
                        "Número de preguntas",
                        min_value=1, max_value=5, value=len(st.session_state.quiz_questions) or 3,
                        key="num_questions_slider"
                    )
                    if st.button("🔄 Generar nuevo cuestionario"):
                        from groq import Groq
                        client = Groq(api_key=st.session_state.groq_api_key)
                        with st.spinner("Generando nuevo conjunto de preguntas..."):
                            new_questions = generate_quiz_from_context(
                                client,
                                st.session_state.last_question,
                                st.session_state.last_context,
                                num_q
                            )
                            if new_questions:
                                st.session_state.quiz_questions = new_questions
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_feedback = {}
                                st.success(f"✅ Nuevo cuestionario generado con {len(new_questions)} preguntas.")
                                st.rerun()
                            else:
                                st.error("No se pudieron generar preguntas. Intenta de nuevo.")
                st.markdown("---")

            # Mostrar preguntas actuales (pueden ser las iniciales o las regeneradas)
            questions = st.session_state.quiz_questions

            if not questions:
                st.info("No hay preguntas disponibles. Genera el resumen primero o presiona 'Generar nuevo cuestionario'.")
            else:
                # Score header
                answered = len([k for k, v in st.session_state.quiz_feedback.items() if v])
                total_q  = len(questions)
                correct  = sum(
                    1 for v in st.session_state.quiz_feedback.values()
                    if v.get("verdict") == "CORRECTO"
                )
                partial  = sum(
                    1 for v in st.session_state.quiz_feedback.values()
                    if v.get("verdict") == "PARCIAL"
                )

                if answered > 0:
                    score_pct = int((correct + 0.5 * partial) / total_q * 100)
                    st.markdown(f"""
<div style="margin-bottom:0.8rem;">
    <div style="display:flex;justify-content:space-between;font-size:0.82rem;color:var(--muted);margin-bottom:0.25rem;">
        <span>Progreso: {answered}/{total_q} respondidas</span>
        <span>Puntuación: {score_pct}%</span>
    </div>
    <div class="score-bar-wrap">
        <div class="score-bar-fill" style="width:{score_pct}%;"></div>
    </div>
</div>""", unsafe_allow_html=True)

                # Render each question
                for q in questions:
                    num  = q["num"]
                    fb   = st.session_state.quiz_feedback.get(num, {})

                    st.markdown(f"""
<div class="quiz-card">
    <div class="quiz-num">Pregunta {num} de {total_q}</div>
    <div class="quiz-q">{q['question']}</div>
</div>""", unsafe_allow_html=True)

                    # If already graded, show answer + feedback locked
                    if fb:
                        verdict = fb.get("verdict", "")
                        color_map = {"CORRECTO": "fb-correct", "PARCIAL": "fb-partial", "INCORRECTO": "fb-wrong"}
                        icon_map  = {"CORRECTO": "✅", "PARCIAL": "🟡", "INCORRECTO": "❌"}
                        css_class = color_map.get(verdict, "fb-partial")
                        icon      = icon_map.get(verdict, "🟡")

                        st.markdown(f"**Tu respuesta:** {st.session_state.quiz_answers.get(num, '')}")
                        st.markdown(f"""
<div class="{css_class}">
    {icon} <strong>{verdict}</strong><br>
    {fb.get('explanation','')}<br>
    <em>💡 {fb.get('tip','')}</em>
</div>""", unsafe_allow_html=True)
                        st.markdown(f"*Respuesta de referencia: {q['answer']}*")

                    else:
                        # Input box
                        user_ans = st.text_area(
                            f"Tu respuesta #{num}",
                            key=f"ans_{num}",
                            placeholder="Escribe tu respuesta aquí…",
                            height=75,
                            label_visibility="collapsed",
                        )

                        if st.button(f"✔️ Verificar pregunta {num}", key=f"verify_{num}"):
                            if not user_ans.strip():
                                st.warning("Escribe algo antes de verificar.")
                            else:
                                with st.spinner("Calificando tu respuesta…"):
                                    from groq import Groq
                                    client = Groq(api_key=st.session_state.groq_api_key)
                                    grade_prompt = (
                                        f"PREGUNTA: {q['question']}\n"
                                        f"RESPUESTA CORRECTA DE REFERENCIA: {q['answer']}\n"
                                        f"RESPUESTA DEL ESTUDIANTE: {user_ans.strip()}"
                                    )
                                    raw_fb = ask_groq(client, SYSTEM_GRADER, grade_prompt)

                                # Parse feedback
                                verdict_m = re.search(r'VEREDICTO:\s*(CORRECTO|PARCIAL|INCORRECTO)', raw_fb, re.I)
                                expl_m    = re.search(r'EXPLICACIÓN:\s*(.+?)(?=CONSEJO:|$)', raw_fb, re.S)
                                tip_m     = re.search(r'CONSEJO:\s*(.+)', raw_fb)

                                st.session_state.quiz_answers[num] = user_ans.strip()
                                st.session_state.quiz_feedback[num] = {
                                    "verdict":     verdict_m.group(1).upper() if verdict_m else "PARCIAL",
                                    "explanation": expl_m.group(1).strip() if expl_m else raw_fb,
                                    "tip":         tip_m.group(1).strip() if tip_m else "",
                                }
                                st.rerun()

                    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

                # Reset quiz button
                if st.session_state.quiz_feedback:
                    if st.button("🔄 Reintentar cuestionario"):
                        st.session_state.quiz_answers  = {}
                        st.session_state.quiz_feedback = {}
                        st.rerun()

    # Footer
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.72rem;color:var(--muted);text-align:center;">'
        '🎙️ Whisper large-v3-turbo &nbsp;·&nbsp; 🧠 LLaMA 3.3 70B &nbsp;·&nbsp; '
        '🔊 Groq TTS (PlayAI) &nbsp;·&nbsp; 📐 MiniLM-L12-v2 &nbsp;·&nbsp; FAISS · LangChain · PyMuPDF'
        '</p>',
        unsafe_allow_html=True,
    )
