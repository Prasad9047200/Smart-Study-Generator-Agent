"""Home / Landing Page"""
import streamlit as st


def render():
    # Hero section
    st.markdown(
        """
        <div style="text-align:center;padding:40px 20px 30px;">
            <div style="font-size:4rem;">🎓</div>
            <h1 style="font-size:2.8rem;font-weight:800;background:linear-gradient(135deg,#4F8BF9,#9B59B6);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;">
                Smart Study Generator
            </h1>
            <p style="color:#8B9BB4;font-size:1.15rem;margin-top:8px;">
                AI-powered personalized study companion — powered by <strong style="color:#0f62fe;">IBM Granite</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature cards
    cols = st.columns(4)
    features = [
        ("📚", "Fuse Resources", "Upload notes, PDFs, textbooks. Get instant AI summaries and structured study material."),
        ("🃏", "Flashcards & Quiz", "Auto-generate flashcards and adaptive quizzes from any study content."),
        ("📅", "Smart Study Plan", "Personalized AI study plans with exam alerts and priority topic recommendations."),
        ("📊", "Progress Dashboard", "Real-time learning milestones, weak area detection, and performance forecasts."),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        col.markdown(
            f"""
            <div class="study-card" style="text-align:center;">
                <div style="font-size:2rem;">{icon}</div>
                <h3 style="color:#4F8BF9;margin:10px 0 6px;">{title}</h3>
                <p style="color:#8B9BB4;font-size:0.88rem;line-height:1.6;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Quick start
    st.markdown("### 🚀 Quick Start")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="study-card">
                <h4 style="color:#4F8BF9;">Step 1: Upload Material</h4>
                <p style="color:#8B9BB4;font-size:0.9rem;">
                    Go to <strong>Study Material</strong> and upload your notes, 
                    PDFs, or paste text to get started.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📚 Go to Study Material", use_container_width=True):
            st.session_state.active_page = "Study Material"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="study-card">
                <h4 style="color:#9B59B6;">Step 2: Generate Content</h4>
                <p style="color:#8B9BB4;font-size:0.9rem;">
                    Create flashcards, quizzes, concept maps and 
                    get AI-powered summaries instantly.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🃏 Go to Flashcards", use_container_width=True):
            st.session_state.active_page = "Flashcards"
            st.rerun()

    with col3:
        st.markdown(
            """
            <div class="study-card">
                <h4 style="color:#21BA45;">Step 3: Track Progress</h4>
                <p style="color:#8B9BB4;font-size:0.9rem;">
                    Monitor your learning milestones, identify weak areas, 
                    and view performance forecasts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📊 View Dashboard", use_container_width=True):
            st.session_state.active_page = "Dashboard"
            st.rerun()

    st.divider()

    # Current material status
    if st.session_state.current_text:
        st.markdown("### 📖 Current Study Material")
        from modules.utils import word_count, truncate_text
        wc = word_count(st.session_state.current_text)
        st.success(
            f"✅ **{st.session_state.current_filename or 'Pasted Text'}** loaded — "
            f"{wc:,} words"
        )
        with st.expander("Preview"):
            st.write(truncate_text(st.session_state.current_text, 500))
    else:
        st.info("💡 No study material loaded yet. Head to **Study Material** to upload content.")

    # IBM tech stack badge
    st.divider()
    st.markdown(
        """
        <div style="text-align:center;padding:16px;">
            <p style="color:#555;font-size:0.8rem;">Powered by</p>
            <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;">
                <span style="background:#0530AD;color:white;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;">IBM watsonx.ai</span>
                <span style="background:#1A1F2E;border:1px solid #2D3748;color:#4F8BF9;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;">Llama 3.3 70B Instruct</span>
                <span style="background:#1A1F2E;border:1px solid #2D3748;color:#FF4B4B;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;">Streamlit</span>
                <span style="background:#1A1F2E;border:1px solid #2D3748;color:#21BA45;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;">IBM Cloud</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
