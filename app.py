"""
Smart Study Generator Agent — Main Application
IBM watsonx.ai Powered Study Companion (Llama 3.3 70B Instruct)
"""

import streamlit as st
from modules.utils import init_session_state

# ── Page configuration (must be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="Smart Study Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Base ── */
    .stApp { background-color: #0E1117; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1F2E 0%, #0E1117 100%);
        border-right: 1px solid #2D3748;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #4F8BF9;
    }

    /* ── Cards / Containers ── */
    .study-card {
        background: #1A1F2E;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: border-color 0.2s;
    }
    .study-card:hover { border-color: #4F8BF9; }

    .metric-card {
        background: linear-gradient(135deg, #1A1F2E, #242B3D);
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4F8BF9;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8B9BB4;
        margin-top: 4px;
    }

    /* ── Flashcard ── */
    .flashcard {
        background: linear-gradient(135deg, #1A1F2E 0%, #1E2A45 100%);
        border: 2px solid #4F8BF9;
        border-radius: 16px;
        padding: 40px 30px;
        text-align: center;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #FAFAFA;
    }

    /* ── Alert badges ── */
    .alert-high {
        background: rgba(255,75,75,0.12);
        border-left: 4px solid #FF4B4B;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    .alert-medium {
        background: rgba(255,140,0,0.12);
        border-left: 4px solid #FF8C00;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    .alert-low {
        background: rgba(33,186,69,0.12);
        border-left: 4px solid #21BA45;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    /* ── Progress bar ── */
    .stProgress > div > div { border-radius: 8px; }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #1A1F2E, #242B3D);
        border: 1px solid #2D3748;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        border-left: 4px solid #4F8BF9;
    }
    .page-header h1 { margin: 0; color: #FAFAFA; font-size: 1.8rem; }
    .page-header p  { margin: 6px 0 0; color: #8B9BB4; }

    /* ── IBM Badge ── */
    .ibm-badge {
        background: linear-gradient(135deg, #0530AD, #0f62fe);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* ── Chat bubbles ── */
    .chat-user {
        background: #1E2A45;
        border-radius: 12px 12px 4px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-left: 20%;
        color: #FAFAFA;
    }
    .chat-bot {
        background: #1A1F2E;
        border: 1px solid #2D3748;
        border-radius: 12px 12px 12px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-right: 20%;
        color: #FAFAFA;
    }

    /* ── Quiz option ── */
    .quiz-correct { color: #21BA45; font-weight: 600; }
    .quiz-wrong   { color: #FF4B4B; font-weight: 600; }

    /* ── Hide default Streamlit elements ── */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state init ────────────────────────────────────────────────────────
init_session_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:16px 0 8px;">
            <div style="font-size:2.5rem;">🎓</div>
            <div style="font-size:1.3rem;font-weight:700;color:#FAFAFA;">Smart Study</div>
            <div style="font-size:1rem;color:#8B9BB4;">Generator Agent</div>
            <div style="margin-top:8px;">
                <span class="ibm-badge">IBM Granite</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    pages = {
        "🏠 Home": "Home",
        "📚 Study Material": "Study Material",
        "🃏 Flashcards": "Flashcards",
        "📝 Quiz": "Quiz",
        "🗺️ Concept Map": "Concept Map",
        "📅 Study Plan": "Study Plan",
        "💬 Ask Tutor": "Ask Tutor",
        "📊 Dashboard": "Dashboard",
    }

    st.markdown("**Navigation**")
    for label, page_id in pages.items():
        is_active = st.session_state.active_page == page_id
        if st.button(
            label,
            key=f"nav_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = page_id
            st.rerun()

    st.divider()

    # Quick stats in sidebar
    from modules.utils import get_progress_stats
    stats = get_progress_stats()
    st.markdown("**Quick Stats**")
    c1, c2 = st.columns(2)
    c1.metric("Cards", stats["cards_reviewed"])
    c2.metric("Quizzes", stats["total_quizzes"])
    c1.metric("Streak", f"{stats['study_streak']}d")
    c2.metric("Score", f"{stats['avg_quiz_score']}%")

    st.divider()
    st.markdown(
        '<div style="text-align:center;font-size:11px;color:#555;">'
        'Powered by <strong style="color:#0f62fe;">IBM watsonx.ai</strong><br>'
        'Model: Llama 3.3 70B Instruct'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Page Router ───────────────────────────────────────────────────────────────
active = st.session_state.active_page

if active == "Home":
    from pages_content.home import render
    render()
elif active == "Study Material":
    from pages_content.study_material import render
    render()
elif active == "Flashcards":
    from pages_content.flashcards import render
    render()
elif active == "Quiz":
    from pages_content.quiz import render
    render()
elif active == "Concept Map":
    from pages_content.concept_map import render
    render()
elif active == "Study Plan":
    from pages_content.study_plan import render
    render()
elif active == "Ask Tutor":
    from pages_content.ask_tutor import render
    render()
elif active == "Dashboard":
    from pages_content.dashboard import render
    render()
