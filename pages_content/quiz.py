"""Quiz Page"""
import streamlit as st
from modules.utils import log_study_session


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>📝 Practice Quiz</h1>
            <p>AI-generated multiple-choice quizzes to test your understanding</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.current_text:
        st.warning("📤 Please upload study material first from the **Study Material** page.")
        if st.button("Go to Study Material"):
            st.session_state.active_page = "Study Material"
            st.rerun()
        return

    # ── Generation Controls ────────────────────────────────────────────────────
    with st.expander("⚙️ Quiz Settings", expanded=not bool(st.session_state.quiz_questions)):
        c1, c2, c3 = st.columns(3)
        with c1:
            num_q = st.slider("Number of questions", 3, 15, 5)
        with c2:
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
        with c3:
            st.markdown(" ")
            gen_btn = st.button("🚀 Generate Quiz", type="primary", use_container_width=True)

        if gen_btn:
            with st.spinner("IBM Granite is crafting quiz questions…"):
                from modules.granite_ai import generate_quiz
                questions = generate_quiz(
                    st.session_state.current_text,
                    num_questions=num_q,
                    difficulty=difficulty,
                )
            if questions:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = 0
                log_study_session("generated_quiz", topic=st.session_state.current_filename)
                st.success(f"✅ Generated **{len(questions)}** questions!")
                st.rerun()
            else:
                st.error("Could not generate quiz questions. Please try again.")

    if not st.session_state.quiz_questions:
        st.info("Configure and generate a quiz above.")
        return

    questions = st.session_state.quiz_questions
    submitted = st.session_state.quiz_submitted

    # ── Quiz Form ─────────────────────────────────────────────────────────────
    if not submitted:
        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                st.markdown(
                    f"""
                    <div class="study-card">
                        <div style="color:#4F8BF9;font-size:0.8rem;font-weight:600;margin-bottom:6px;">
                            QUESTION {i+1} of {len(questions)}
                        </div>
                        <div style="font-size:1.05rem;font-weight:600;color:#FAFAFA;">
                            {q.get('question','')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                options = q.get("options", [])
                if options:
                    choice = st.radio(
                        f"Select answer for Q{i+1}",
                        options=list(range(len(options))),
                        format_func=lambda x, opts=options: f"{chr(65+x)}. {opts[x]}",
                        key=f"q_{i}",
                        label_visibility="collapsed",
                    )
                    st.session_state.quiz_answers[i] = choice
                st.markdown(" ")

            submitted_btn = st.form_submit_button(
                "✅ Submit Quiz",
                use_container_width=True,
                type="primary",
            )
            if submitted_btn:
                # Score it
                score = 0
                for i, q in enumerate(questions):
                    user_ans = st.session_state.quiz_answers.get(i)
                    if user_ans == q.get("correct"):
                        score += 1
                pct = round(score / len(questions) * 100, 1)
                st.session_state.quiz_score = pct
                st.session_state.quiz_submitted = True
                quiz_record = {
                    "score": pct,
                    "total": len(questions),
                    "correct": score,
                    "topic": st.session_state.current_filename,
                }
                st.session_state.quiz_history.append(quiz_record)
                log_study_session("completed_quiz", score=pct, topic=st.session_state.current_filename)
                st.rerun()

    else:
        # ── Results ────────────────────────────────────────────────────────────
        score_pct = st.session_state.quiz_score
        correct_count = sum(
            1 for i, q in enumerate(questions)
            if st.session_state.quiz_answers.get(i) == q.get("correct")
        )

        # Score banner
        if score_pct >= 80:
            grade_color, grade_emoji, grade_text = "#21BA45", "🏆", "Excellent!"
        elif score_pct >= 60:
            grade_color, grade_emoji, grade_text = "#FF8C00", "👍", "Good job!"
        else:
            grade_color, grade_emoji, grade_text = "#FF4B4B", "📚", "Keep studying!"

        st.markdown(
            f"""
            <div style="text-align:center;background:linear-gradient(135deg,#1A1F2E,#242B3D);
                        border:2px solid {grade_color};border-radius:16px;padding:30px;margin:16px 0;">
                <div style="font-size:3rem;">{grade_emoji}</div>
                <div style="font-size:2.5rem;font-weight:800;color:{grade_color};">{score_pct}%</div>
                <div style="font-size:1.2rem;color:#FAFAFA;margin-top:8px;">{grade_text}</div>
                <div style="color:#8B9BB4;margin-top:4px;">{correct_count} / {len(questions)} correct</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Detailed review
        st.markdown("### 📋 Answer Review")
        for i, q in enumerate(questions):
            user_ans = st.session_state.quiz_answers.get(i)
            correct_ans = q.get("correct", 0)
            is_correct = user_ans == correct_ans
            options = q.get("options", [])

            icon = "✅" if is_correct else "❌"
            border = "#21BA45" if is_correct else "#FF4B4B"

            st.markdown(
                f"""
                <div style="background:#1A1F2E;border:1px solid {border};border-radius:12px;
                            padding:16px;margin:10px 0;">
                    <div style="font-weight:600;color:#FAFAFA;margin-bottom:10px;">
                        {icon} Q{i+1}: {q.get('question','')}
                    </div>
                """,
                unsafe_allow_html=True,
            )
            for j, opt in enumerate(options):
                if j == correct_ans:
                    opt_style = "color:#21BA45;font-weight:600;"
                    opt_icon = "✅"
                elif j == user_ans and not is_correct:
                    opt_style = "color:#FF4B4B;text-decoration:line-through;"
                    opt_icon = "❌"
                else:
                    opt_style = "color:#8B9BB4;"
                    opt_icon = "  "
                st.markdown(
                    f'<div style="{opt_style};padding:3px 0;">{opt_icon} {chr(65+j)}. {opt}</div>',
                    unsafe_allow_html=True,
                )

            explanation = q.get("explanation", "")
            if explanation:
                st.markdown(
                    f'<div style="margin-top:8px;padding:8px 12px;background:rgba(79,139,249,0.1);'
                    f'border-radius:6px;color:#8B9BB4;font-size:0.88rem;">💡 {explanation}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Retry
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_score = 0
            st.rerun()

        if st.button("📝 Generate New Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()
