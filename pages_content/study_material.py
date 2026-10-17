"""Study Material Processor Page"""
import streamlit as st
from modules.utils import extract_text_from_upload, word_count, log_study_session


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>📚 Study Material Processor</h1>
            <p>Upload your notes, PDFs, textbooks — get AI-powered summaries and analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "🔍 AI Analysis", "💡 Summary"])

    # ── Tab 1: Upload ──────────────────────────────────────────────────────────
    with tab1:
        col_upload, col_paste = st.columns([1, 1])

        with col_upload:
            st.markdown("#### 📎 Upload Files")
            uploaded = st.file_uploader(
                "Drag and drop or click to browse",
                type=["pdf", "txt", "md", "docx"],
                accept_multiple_files=False,
                help="Supports PDF, TXT, MD, DOCX files up to 50MB",
            )
            if uploaded:
                with st.spinner(f"Extracting text from **{uploaded.name}**…"):
                    text = extract_text_from_upload(uploaded)
                if text and not text.startswith("Error"):
                    st.session_state.current_text = text
                    st.session_state.current_filename = uploaded.name
                    st.session_state.topic_analysis = None  # reset
                    log_study_session("uploaded_file", topic=uploaded.name)
                    st.success(f"✅ Extracted **{word_count(text):,}** words from `{uploaded.name}`")
                else:
                    st.error(f"Could not extract text: {text}")

            # Image upload (display only + OCR note)
            st.markdown("#### 🖼️ Upload Image (Textbook Page)")
            img_file = st.file_uploader(
                "Upload a textbook page or handwritten note image",
                type=["png", "jpg", "jpeg", "webp"],
                key="img_upload",
            )
            if img_file:
                try:
                    from PIL import Image
                    img = Image.open(img_file)
                    st.image(img, caption="Uploaded Image", use_container_width=True)
                    st.info("💡 For full OCR text extraction, ensure `pytesseract` + Tesseract are installed. You can also paste the text manually below.")
                except Exception:
                    st.warning("Could not display image. Pillow may not be installed.")

        with col_paste:
            st.markdown("#### ✏️ Paste Text")
            pasted = st.text_area(
                "Paste your notes, lecture text, or any study content here",
                height=300,
                placeholder="Paste lecture notes, textbook excerpts, article content…",
                key="paste_area",
            )
            topic_name = st.text_input("Topic / Subject Name (optional)", placeholder="e.g., Machine Learning — Neural Networks")
            if st.button("📥 Load Pasted Text", use_container_width=True, type="primary"):
                if pasted.strip():
                    st.session_state.current_text = pasted.strip()
                    st.session_state.current_filename = topic_name or "Pasted Text"
                    st.session_state.topic_analysis = None
                    log_study_session("pasted_text", topic=topic_name or "Pasted Text")
                    st.success(f"✅ Loaded **{word_count(pasted):,}** words.")
                    st.rerun()
                else:
                    st.warning("Please paste some text first.")

        # Current material status
        if st.session_state.current_text:
            st.divider()
            st.markdown("#### 📖 Current Material")
            wc = word_count(st.session_state.current_text)
            c1, c2, c3 = st.columns(3)
            c1.metric("Words", f"{wc:,}")
            c2.metric("Characters", f"{len(st.session_state.current_text):,}")
            c3.metric("Est. Read Time", f"{max(1, wc // 200)} min")

            with st.expander("📄 Preview content"):
                st.write(st.session_state.current_text[:2000])
                if len(st.session_state.current_text) > 2000:
                    st.caption(f"… and {len(st.session_state.current_text)-2000:,} more characters")

    # ── Tab 2: AI Analysis ─────────────────────────────────────────────────────
    with tab2:
        if not st.session_state.current_text:
            st.info("📤 Upload or paste study material first.")
            return

        st.markdown("#### 🔍 AI-Powered Topic Analysis")
        st.caption("IBM Granite analyzes your material to identify topics, difficulty, and exam-relevant areas.")

        if st.button("🚀 Analyze Material", type="primary", use_container_width=True):
            with st.spinner("IBM Granite is analyzing your study material…"):
                from modules.granite_ai import analyze_topics
                analysis = analyze_topics(st.session_state.current_text)
                st.session_state.topic_analysis = analysis
                log_study_session("analyzed_material", topic=st.session_state.current_filename)

        if st.session_state.topic_analysis:
            ana = st.session_state.topic_analysis

            c1, c2, c3 = st.columns(3)
            c1.markdown(
                f'<div class="metric-card"><div class="metric-value">'
                f'{ana.get("difficulty_level","N/A").title()}</div>'
                f'<div class="metric-label">Difficulty Level</div></div>',
                unsafe_allow_html=True,
            )
            c2.markdown(
                f'<div class="metric-card"><div class="metric-value">'
                f'{ana.get("estimated_study_time","N/A")}</div>'
                f'<div class="metric-label">Est. Study Time</div></div>',
                unsafe_allow_html=True,
            )
            c3.markdown(
                f'<div class="metric-card"><div class="metric-value">'
                f'{ana.get("subject_area","N/A")}</div>'
                f'<div class="metric-label">Subject Area</div></div>',
                unsafe_allow_html=True,
            )

            st.markdown(" ")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**📌 Main Topics**")
                for t in ana.get("main_topics", []):
                    st.markdown(f"- {t}")

                st.markdown("**🔑 Key Concepts**")
                for c in ana.get("key_concepts", []):
                    st.markdown(f"- {c}")

            with col_b:
                st.markdown("**🎯 Likely Exam Topics**")
                for t in ana.get("exam_likely_topics", []):
                    st.markdown(
                        f'<div style="background:rgba(255,75,75,0.1);border-left:3px solid #FF4B4B;'
                        f'padding:6px 12px;border-radius:4px;margin:4px 0;color:#FAFAFA;">🎯 {t}</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("**📚 Prerequisites**")
                for p in ana.get("prerequisites", []):
                    st.markdown(f"- {p}")

            # Save topics for study plan
            if ana.get("main_topics"):
                st.session_state.study_topics = ana["main_topics"]

    # ── Tab 3: Summary ─────────────────────────────────────────────────────────
    with tab3:
        if not st.session_state.current_text:
            st.info("📤 Upload or paste study material first.")
            return

        st.markdown("#### 💡 AI-Powered Summary")
        style = st.selectbox(
            "Summary Style",
            ["concise", "detailed", "eli5", "exam_ready"],
            format_func=lambda x: {
                "concise": "🎯 Concise (Key Points)",
                "detailed": "📖 Detailed (Full Breakdown)",
                "eli5": "🧒 Simple (ELI5 — Plain Language)",
                "exam_ready": "📝 Exam Ready (Definitions & Facts)",
            }[x],
        )

        if st.button("✨ Generate Summary", type="primary", use_container_width=True):
            with st.spinner("IBM Granite is summarizing your material…"):
                from modules.granite_ai import summarize_content
                summary = summarize_content(st.session_state.current_text, style=style)
                st.session_state[f"summary_{style}"] = summary
                log_study_session("generated_summary", topic=st.session_state.current_filename)

        key = f"summary_{style}"
        if key in st.session_state and st.session_state[key]:
            st.markdown(
                f'<div class="study-card"><h4 style="color:#4F8BF9;">Summary ({style.replace("_"," ").title()})</h4>',
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state[key])
            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                "⬇️ Download Summary",
                data=st.session_state[key],
                file_name=f"summary_{style}.txt",
                mime="text/plain",
            )
