"""Study Plan & Recommendations Page"""
import streamlit as st
import datetime
from modules.utils import log_study_session


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>📅 Personalized Study Plan</h1>
            <p>AI-generated adaptive study plan with exam alerts and priority recommendations</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📅 Study Plan", "🎯 Exam Predictions", "💡 Recommendations"])

    # ── Tab 1: Study Plan ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("#### ⚙️ Configure Your Study Plan")

        col1, col2 = st.columns(2)
        with col1:
            exam_date = st.date_input(
                "📆 Exam Date",
                value=datetime.date.today() + datetime.timedelta(days=14),
                min_value=datetime.date.today(),
            )
            hours_per_day = st.slider("⏱️ Study hours per day", 1.0, 10.0, 3.0, 0.5)

        with col2:
            # Pre-fill from analysis if available
            default_topics = ""
            if st.session_state.get("study_topics"):
                default_topics = "\n".join(st.session_state.study_topics[:8])
            elif st.session_state.current_filename:
                default_topics = st.session_state.current_filename

            topics_input = st.text_area(
                "📌 Topics to cover (one per line)",
                value=default_topics,
                height=120,
                placeholder="e.g.\nNeural Networks\nGradient Descent\nBackpropagation",
            )
            weak_areas_input = st.text_area(
                "⚠️ Known weak areas (one per line, optional)",
                height=80,
                placeholder="e.g.\nCalculus\nMatrix operations",
            )

        if st.button("🚀 Generate Study Plan", type="primary", use_container_width=True):
            topics = [t.strip() for t in topics_input.split("\n") if t.strip()]
            weak_areas = [w.strip() for w in weak_areas_input.split("\n") if w.strip()]

            if not topics:
                st.warning("Please enter at least one topic.")
            else:
                with st.spinner("IBM Granite is crafting your personalized study plan…"):
                    from modules.granite_ai import generate_study_plan
                    plan = generate_study_plan(
                        topics=topics,
                        exam_date=exam_date.strftime("%B %d, %Y"),
                        hours_per_day=hours_per_day,
                        weak_areas=weak_areas if weak_areas else None,
                    )
                    st.session_state.study_plan = plan
                    log_study_session("generated_study_plan", topic=", ".join(topics[:3]))
                st.success("✅ Your personalized study plan is ready!")
                st.rerun()

        # Display plan
        plan = st.session_state.get("study_plan")
        if plan:
            st.divider()

            # Summary metrics
            days_until = (exam_date - datetime.date.today()).days
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(
                f'<div class="metric-card"><div class="metric-value">{days_until}</div>'
                f'<div class="metric-label">Days Until Exam</div></div>',
                unsafe_allow_html=True,
            )
            c2.markdown(
                f'<div class="metric-card"><div class="metric-value">{hours_per_day}h</div>'
                f'<div class="metric-label">Daily Study Time</div></div>',
                unsafe_allow_html=True,
            )
            c3.markdown(
                f'<div class="metric-card"><div class="metric-value">'
                f'{round(days_until * hours_per_day)}h</div>'
                f'<div class="metric-label">Total Study Hours</div></div>',
                unsafe_allow_html=True,
            )
            readiness = plan.get("predicted_readiness", "Calculating…")
            c4.markdown(
                f'<div class="metric-card"><div class="metric-value" style="font-size:1.2rem;">'
                f'{readiness[:20] if isinstance(readiness, str) else readiness}</div>'
                f'<div class="metric-label">Predicted Readiness</div></div>',
                unsafe_allow_html=True,
            )

            st.markdown(" ")

            # Priority topics
            priority = plan.get("priority_topics", [])
            if priority:
                st.markdown("#### 🔥 Priority Topics")
                cols = st.columns(min(4, len(priority)))
                for i, topic in enumerate(priority):
                    cols[i % len(cols)].markdown(
                        f"""
                        <div style="background:rgba(255,75,75,0.1);border:1px solid #FF4B4B;
                                    border-radius:8px;padding:10px 14px;text-align:center;
                                    color:#FF4B4B;font-weight:600;margin:4px 0;">
                            🎯 {topic}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Daily schedule
            daily = plan.get("daily_schedule", [])
            if daily:
                st.markdown("#### 📆 Daily Schedule")
                for day_plan in daily[:14]:  # cap at 2 weeks display
                    day_label = day_plan.get("day", "")
                    date_label = day_plan.get("date", "")
                    hours = day_plan.get("hours", hours_per_day)
                    day_topics = day_plan.get("topics", [])
                    activities = day_plan.get("activities", [])

                    with st.expander(f"📅 {day_label} {f'— {date_label}' if date_label else ''} ({hours}h)"):
                        col_t, col_a = st.columns(2)
                        with col_t:
                            st.markdown("**Topics:**")
                            for t in day_topics:
                                st.markdown(f"- {t}")
                        with col_a:
                            st.markdown("**Activities:**")
                            for a in activities:
                                st.markdown(f"- {a}")

            # Study tips
            tips = plan.get("study_tips", [])
            if tips:
                st.markdown("#### 💡 Study Tips")
                for tip in tips:
                    st.markdown(
                        f'<div style="background:rgba(79,139,249,0.1);border-left:3px solid #4F8BF9;'
                        f'padding:8px 14px;border-radius:4px;margin:4px 0;color:#FAFAFA;">💡 {tip}</div>',
                        unsafe_allow_html=True,
                    )

            # Milestones
            milestones = plan.get("weekly_milestones", [])
            if milestones:
                st.markdown("#### 🏆 Weekly Milestones")
                for i, m in enumerate(milestones):
                    st.markdown(
                        f'<div style="background:#1A1F2E;border:1px solid #2D3748;'
                        f'padding:10px 16px;border-radius:8px;margin:4px 0;color:#FAFAFA;">'
                        f'<span style="color:#21BA45;font-weight:700;">Week {i+1}:</span> {m}</div>',
                        unsafe_allow_html=True,
                    )

    # ── Tab 2: Exam Predictions ────────────────────────────────────────────────
    with tab2:
        st.markdown("#### 🎯 AI Exam Prediction Alerts")
        st.caption("IBM Granite predicts high-frequency exam topics based on your study material.")

        topics_for_pred = st.session_state.get("study_topics", [])
        subject = ""
        if st.session_state.get("topic_analysis"):
            subject = st.session_state.topic_analysis.get("subject_area", "")

        if not topics_for_pred and st.session_state.current_text:
            st.info("Run **AI Analysis** on your study material first to get better predictions.")

        if st.button("🔮 Generate Exam Predictions", type="primary", use_container_width=True):
            if not topics_for_pred and not st.session_state.current_text:
                st.warning("Please upload study material first.")
            else:
                if not topics_for_pred:
                    # Extract topics on the fly
                    from modules.granite_ai import analyze_topics
                    with st.spinner("Analyzing topics…"):
                        ana = analyze_topics(st.session_state.current_text)
                        topics_for_pred = ana.get("main_topics", []) + ana.get("exam_likely_topics", [])

                with st.spinner("IBM Granite is generating exam predictions…"):
                    from modules.granite_ai import get_exam_predictions
                    predictions = get_exam_predictions(topics_for_pred, subject=subject)
                    st.session_state["exam_predictions"] = predictions

        predictions = st.session_state.get("exam_predictions", [])
        if predictions:
            for pred in predictions:
                priority = pred.get("priority", "medium").lower()
                css_class = f"alert-{priority}"
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🔵")
                st.markdown(
                    f"""
                    <div class="{css_class}">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div>
                                <div style="font-weight:700;color:#FAFAFA;margin-bottom:4px;">
                                    {icon} {pred.get('topic','')}
                                </div>
                                <div style="color:#FAFAFA;font-size:0.95rem;">{pred.get('alert','')}</div>
                                <div style="color:#8B9BB4;font-size:0.85rem;margin-top:4px;">
                                    💡 {pred.get('tip','')}
                                </div>
                            </div>
                            <span style="font-size:0.75rem;font-weight:600;
                                        color:{'#FF4B4B' if priority=='high' else '#FF8C00' if priority=='medium' else '#21BA45'};">
                                {priority.upper()}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── Tab 3: Recommendations ─────────────────────────────────────────────────
    with tab3:
        st.markdown("#### 🤖 Personalized Recommendations")

        stats = st.session_state.get("quiz_history", [])
        cards_known = len(st.session_state.get("cards_known", set()))
        cards_total = len(st.session_state.get("flashcards", []))

        # Dynamic recommendations based on progress
        recs = []

        if not st.session_state.current_text:
            recs.append({
                "icon": "📤",
                "title": "Upload Study Material",
                "desc": "Start by uploading your lecture notes, PDF, or pasting study text.",
                "action": "Study Material",
                "priority": "high",
            })

        if st.session_state.current_text and not st.session_state.flashcards:
            recs.append({
                "icon": "🃏",
                "title": "Create Flashcards",
                "desc": "Generate AI-powered flashcards from your study material for active recall.",
                "action": "Flashcards",
                "priority": "high",
            })

        if st.session_state.flashcards and cards_total > 0:
            mastery = cards_known / cards_total * 100
            if mastery < 70:
                recs.append({
                    "icon": "📖",
                    "title": "Review Flashcards",
                    "desc": f"Your flashcard mastery is {mastery:.0f}%. Review until you reach 70%+.",
                    "action": "Flashcards",
                    "priority": "medium",
                })

        if not st.session_state.quiz_questions:
            recs.append({
                "icon": "📝",
                "title": "Take a Practice Quiz",
                "desc": "Test your understanding with an AI-generated quiz.",
                "action": "Quiz",
                "priority": "medium",
            })

        if stats:
            avg = sum(q.get("score", 0) for q in stats) / len(stats)
            if avg < 60:
                recs.append({
                    "icon": "⚠️",
                    "title": "Low Quiz Score — Review Material",
                    "desc": f"Your average quiz score is {avg:.0f}%. Re-read the material and retry.",
                    "action": "Study Material",
                    "priority": "high",
                })

        if not st.session_state.get("study_plan"):
            recs.append({
                "icon": "📅",
                "title": "Generate a Study Plan",
                "desc": "Create an AI-powered personalized study schedule for your exam.",
                "action": "Study Plan",
                "priority": "low",
            })

        recs.append({
            "icon": "💬",
            "title": "Ask the AI Tutor",
            "desc": "Have questions? Ask the AI tutor anything about your study material.",
            "action": "Ask Tutor",
            "priority": "low",
        })

        for rec in recs:
            p = rec["priority"]
            color = {"high": "#FF4B4B", "medium": "#FF8C00", "low": "#4F8BF9"}.get(p, "#4F8BF9")
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="study-card" style="border-left:3px solid {color};padding:14px 18px;">
                        <div style="display:flex;gap:10px;align-items:flex-start;">
                            <span style="font-size:1.4rem;">{rec['icon']}</span>
                            <div>
                                <div style="font-weight:700;color:#FAFAFA;">{rec['title']}</div>
                                <div style="color:#8B9BB4;font-size:0.88rem;margin-top:2px;">{rec['desc']}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_btn:
                st.markdown(" ")
                if st.button(f"Go →", key=f"rec_{rec['action']}", use_container_width=True):
                    st.session_state.active_page = rec["action"]
                    st.rerun()
