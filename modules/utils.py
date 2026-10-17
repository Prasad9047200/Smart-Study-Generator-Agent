"""
Utility / Helper Module
File parsing, text extraction, session state helpers
"""

import io
import re
import json
import datetime
import streamlit as st

# ── Optional imports ──────────────────────────────────────────────────────────
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ── Text Extraction ───────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    if not PDF_AVAILABLE:
        return "PyPDF2 not installed. Please install it to process PDFs."
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n\n".join(pages)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    if not DOCX_AVAILABLE:
        return "python-docx not installed. Please install it to process DOCX files."
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from a plain text file."""
    try:
        return file_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error reading TXT: {str(e)}"


def extract_text_from_upload(uploaded_file) -> str:
    """Route uploaded file to the correct extractor."""
    if uploaded_file is None:
        return ""
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".txt") or name.endswith(".md"):
        return extract_text_from_txt(file_bytes)
    else:
        # Try as plain text
        return extract_text_from_txt(file_bytes)


# ── Session State Helpers ─────────────────────────────────────────────────────

def init_session_state():
    """Initialize all required session state keys."""
    defaults = {
        # Study material
        "current_text": "",
        "current_filename": "",
        "topic_analysis": None,
        # Flashcards
        "flashcards": [],
        "current_card_index": 0,
        "card_flipped": False,
        "cards_reviewed": set(),
        "cards_known": set(),
        # Quiz
        "quiz_questions": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        "quiz_score": 0,
        # Study plan
        "study_plan": None,
        "study_topics": [],
        # Progress tracking
        "study_sessions": [],
        "total_cards_reviewed": 0,
        "quiz_history": [],
        "topics_studied": [],
        # Chat / Q&A
        "chat_history": [],
        # Navigation
        "active_page": "Home",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def log_study_session(activity: str, score: float = None, topic: str = ""):
    """Log a study activity to session history."""
    session = {
        "timestamp": datetime.datetime.now().isoformat(),
        "activity": activity,
        "topic": topic,
        "score": score,
    }
    st.session_state.study_sessions.append(session)
    if topic and topic not in st.session_state.topics_studied:
        st.session_state.topics_studied.append(topic)


def get_progress_stats() -> dict:
    """Compute overall progress statistics."""
    sessions = st.session_state.get("study_sessions", [])
    quiz_history = st.session_state.get("quiz_history", [])
    cards_reviewed = len(st.session_state.get("cards_reviewed", set()))
    cards_known = len(st.session_state.get("cards_known", set()))

    total_quizzes = len(quiz_history)
    avg_score = 0.0
    if quiz_history:
        avg_score = sum(q.get("score", 0) for q in quiz_history) / total_quizzes

    return {
        "total_sessions": len(sessions),
        "topics_studied": len(st.session_state.get("topics_studied", [])),
        "cards_reviewed": cards_reviewed,
        "cards_known": cards_known,
        "card_mastery": round((cards_known / max(cards_reviewed, 1)) * 100, 1),
        "total_quizzes": total_quizzes,
        "avg_quiz_score": round(avg_score, 1),
        "study_streak": _calculate_streak(sessions),
    }


def _calculate_streak(sessions: list) -> int:
    """Calculate current study streak in days."""
    if not sessions:
        return 0
    dates = set()
    for s in sessions:
        try:
            d = datetime.datetime.fromisoformat(s["timestamp"]).date()
            dates.add(d)
        except Exception:
            pass
    if not dates:
        return 0
    today = datetime.date.today()
    streak = 0
    check = today
    while check in dates:
        streak += 1
        check -= datetime.timedelta(days=1)
    return streak


# ── Text Helpers ──────────────────────────────────────────────────────────────

def truncate_text(text: str, max_chars: int = 200) -> str:
    """Truncate text to a preview length."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text else 0


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """Split large text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ── UI Helpers ────────────────────────────────────────────────────────────────

def priority_badge(priority: str) -> str:
    """Return a styled HTML badge for priority level."""
    colors = {
        "high": ("#FF4B4B", "#FFE0E0"),
        "medium": ("#FF8C00", "#FFF3E0"),
        "low": ("#21BA45", "#E8F5E9"),
    }
    fg, bg = colors.get(priority.lower(), ("#999", "#EEE"))
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:600;">'
        f'{priority.upper()}</span>'
    )


def format_date_friendly(iso_str: str) -> str:
    """Format ISO date string to friendly format."""
    try:
        dt = datetime.datetime.fromisoformat(iso_str)
        return dt.strftime("%b %d, %Y %H:%M")
    except Exception:
        return iso_str
