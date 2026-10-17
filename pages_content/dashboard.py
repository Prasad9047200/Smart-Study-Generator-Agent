"""Progress Dashboard Page"""
import streamlit as st
import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from modules.utils import get_progress_stats, log_study_session


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>📊 Learning Progress Dashboard</h1>
            <p>Real-time learning milestones, weak area analysis, and performance forecasts</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = get_progress_stats()

    # ── Top KPI Cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        ("📚", "Topics Studied", stats["topics_studied"], "#4F8BF9"),
        ("🃏", "Cards Reviewed", stats["cards_reviewed"], "#9B59B6"),
        ("🏆", "Card Mastery", f"{stats['card_mastery']}%", "#21BA45"),
        ("📝", "Quizzes Taken", stats["total_quizzes"], "#FF8C00"),
        ("🔥", "Study Streak", f"{stats['study_streak']}d", "#FF4B4B"),
    ]
    for col, (icon, label, value, color) in zip([c1, c2, c3, c4, c5], kpis):
        col.markdown(
            f"""
            <div class="metric-card" style="border-top:3px solid {color};">
                <div style="font-size:1.5rem;">{icon}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(" ")

    # ── Charts Row 1 ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 📈 Quiz Performance Over Time")
        quiz_history = st.session_state.get("quiz_history", [])

        if quiz_history:
            df_quiz = pd.DataFrame(quiz_history)
            df_quiz.index = range(1, len(df_quiz) + 1)
            df_quiz.index.name = "Attempt"

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(df_quiz.index),
                y=df_quiz["score"],
                mode="lines+markers",
                name="Score %",
                line=dict(color="#4F8BF9", width=3),
                marker=dict(size=8, color="#4F8BF9"),
                fill="tozeroy",
                fillcolor="rgba(79,139,249,0.1)",
            ))
            # Passing line
            fig.add_hline(y=60, line_dash="dash", line_color="#FF8C00",
                          annotation_text="Pass (60%)", annotation_position="bottom right")
            fig.add_hline(y=80, line_dash="dash", line_color="#21BA45",
                          annotation_text="Good (80%)", annotation_position="bottom right")

            fig.update_layout(
                plot_bgcolor="#1A1F2E",
                paper_bgcolor="#1A1F2E",
                font_color="#FAFAFA",
                xaxis=dict(title="Quiz Attempt", gridcolor="#2D3748", color="#8B9BB4"),
                yaxis=dict(title="Score %", range=[0, 100], gridcolor="#2D3748", color="#8B9BB4"),
                margin=dict(t=20, b=20, l=20, r=20),
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            _empty_chart("Take quizzes to see performance trends", height=280)

    with col_right:
        st.markdown("#### 🃏 Flashcard Mastery")
        cards_known = len(st.session_state.get("cards_known", set()))
        cards_reviewed = len(st.session_state.get("cards_reviewed", set()))
        total_cards = len(st.session_state.get("flashcards", []))
        unreviewed = max(0, total_cards - cards_reviewed)
        needs_review = max(0, cards_reviewed - cards_known)

        if total_cards > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Known ✅", "Needs Review 🔄", "Unreviewed ⬜"],
                values=[cards_known, needs_review, unreviewed],
                hole=0.55,
                marker=dict(colors=["#21BA45", "#FF8C00", "#2D3748"]),
                textfont=dict(color="#FAFAFA"),
            )])
            fig_pie.update_layout(
                plot_bgcolor="#1A1F2E",
                paper_bgcolor="#1A1F2E",
                font_color="#FAFAFA",
                legend=dict(font=dict(color="#FAFAFA"), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=20, b=20, l=20, r=20),
                height=280,
                annotations=[dict(text=f"{stats['card_mastery']}%<br>Mastery",
                                  x=0.5, y=0.5, font_size=16, showarrow=False,
                                  font_color="#FAFAFA")],
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            _empty_chart("Generate flashcards to see mastery breakdown", height=280)

    # ── Charts Row 2 ──────────────────────────────────────────────────────────
    col_l2, col_r2 = st.columns([1, 1])

    with col_l2:
        st.markdown("#### 🗓️ Study Activity Heatmap")
        sessions = st.session_state.get("study_sessions", [])

        if sessions:
            # Count activities per day
            day_counts: dict[str, int] = {}
            for s in sessions:
                try:
                    d = datetime.datetime.fromisoformat(s["timestamp"]).strftime("%Y-%m-%d")
                    day_counts[d] = day_counts.get(d, 0) + 1
                except Exception:
                    pass

            # Build last 30 days
            today = datetime.date.today()
            days = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
            counts = [day_counts.get(d, 0) for d in days]
            labels = [(today - datetime.timedelta(days=i)).strftime("%b %d") for i in range(29, -1, -1)]

            fig_bar = go.Figure(go.Bar(
                x=labels,
                y=counts,
                marker_color=["#4F8BF9" if c > 0 else "#2D3748" for c in counts],
                text=[str(c) if c > 0 else "" for c in counts],
                textposition="outside",
                textfont=dict(color="#8B9BB4", size=9),
            ))
            fig_bar.update_layout(
                plot_bgcolor="#1A1F2E",
                paper_bgcolor="#1A1F2E",
                font_color="#FAFAFA",
                xaxis=dict(tickangle=-45, tickfont=dict(size=9), gridcolor="#2D3748", color="#8B9BB4"),
                yaxis=dict(title="Activities", gridcolor="#2D3748", color="#8B9BB4"),
                margin=dict(t=20, b=60, l=20, r=20),
                height=280,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            _empty_chart("Start studying to see your activity history", height=280)

    with col_r2:
        st.markdown("#### 🎯 Topic Coverage Radar")
        topics_studied = st.session_state.get("topics_studied", [])

        if len(topics_studied) >= 3:
            # Score each topic based on quiz/flashcard activity
            quiz_topics = {q.get("topic", ""): q.get("score", 0) for q in st.session_state.get("quiz_history", [])}
            scores = []
            for t in topics_studied[:8]:
                sc = quiz_topics.get(t, 50)  # default 50 if no quiz data
                scores.append(min(100, sc))

            categories = [t[:20] for t in topics_studied[:8]]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(79,139,249,0.2)",
                line=dict(color="#4F8BF9", width=2),
                marker=dict(size=6, color="#4F8BF9"),
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#1A1F2E",
                    radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor="#2D3748", color="#8B9BB4"),
                    angularaxis=dict(gridcolor="#2D3748", color="#8B9BB4"),
                ),
                paper_bgcolor="#1A1F2E",
                font_color="#FAFAFA",
                margin=dict(t=20, b=20, l=40, r=40),
                height=280,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            _empty_chart("Study 3+ topics to see coverage radar", height=280)

    # ── Performance Forecast ───────────────────────────────────────────────────
    st.markdown("#### 🔮 Performance Forecast")
    quiz_history = st.session_state.get("quiz_history", [])

    if len(quiz_history) >= 2:
        scores = [q.get("score", 0) for q in quiz_history]
        # Simple linear trend forecast
        n = len(scores)
        avg_gain = (scores[-1] - scores[0]) / max(n - 1, 1)
        forecast = [min(100, scores[-1] + avg_gain * i) for i in range(1, 4)]

        fig_forecast = go.Figure()
        x_actual = list(range(1, n + 1))
        x_forecast = list(range(n, n + 4))

        fig_forecast.add_trace(go.Scatter(
            x=x_actual, y=scores,
            name="Actual",
            line=dict(color="#4F8BF9", width=3),
            marker=dict(size=8),
        ))
        fig_forecast.add_trace(go.Scatter(
            x=x_forecast, y=[scores[-1]] + forecast,
            name="Forecast",
            line=dict(color="#9B59B6", width=2, dash="dot"),
            marker=dict(size=6),
        ))
        fig_forecast.add_hline(y=80, line_dash="dash", line_color="#21BA45",
                               annotation_text="Target (80%)")
        fig_forecast.update_layout(
            plot_bgcolor="#1A1F2E",
            paper_bgcolor="#1A1F2E",
            font_color="#FAFAFA",
            xaxis=dict(title="Quiz Attempt", gridcolor="#2D3748", color="#8B9BB4"),
            yaxis=dict(title="Score %", range=[0, 105], gridcolor="#2D3748", color="#8B9BB4"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#FAFAFA")),
            margin=dict(t=10, b=20, l=20, r=20),
            height=250,
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        # Forecast insight
        if forecast[-1] >= 80:
            st.success(f"🚀 Based on your trend, you're on track to reach **{forecast[-1]:.0f}%** in the next 3 quizzes!")
        elif forecast[-1] >= 60:
            st.warning(f"📈 Trend shows improvement. Keep studying to reach your 80% target.")
        else:
            st.error("📚 Your scores need improvement. Focus on reviewing weak areas and retaking quizzes.")
    else:
        st.info("Take at least 2 quizzes to generate a performance forecast.")

    # ── Weak Areas ────────────────────────────────────────────────────────────
    st.markdown("#### ⚠️ Weak Areas & Action Items")
    quiz_history = st.session_state.get("quiz_history", [])

    if quiz_history:
        low_scores = [q for q in quiz_history if q.get("score", 100) < 70]
        if low_scores:
            for q in low_scores[-3:]:
                st.markdown(
                    f"""
                    <div class="alert-high">
                        <strong>⚠️ {q.get('topic','Unknown Topic')}</strong>
                        — Score: {q.get('score',0):.0f}% ({q.get('correct',0)}/{q.get('total',0)} correct)
                        <br>
                        <span style="color:#8B9BB4;font-size:0.85rem;">
                            💡 Recommendation: Re-read the material, review flashcards, and retake the quiz.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ Great work! No significant weak areas detected based on your quiz performance.")
    else:
        st.info("Complete quizzes to identify your weak areas.")

    # ── Activity Log ──────────────────────────────────────────────────────────
    with st.expander("📋 Full Activity Log"):
        sessions = st.session_state.get("study_sessions", [])
        if sessions:
            log_data = []
            for s in reversed(sessions[-20:]):
                log_data.append({
                    "Time": s.get("timestamp", "")[:16].replace("T", " "),
                    "Activity": s.get("activity", "").replace("_", " ").title(),
                    "Topic": s.get("topic", "—"),
                    "Score": f"{s['score']:.0f}%" if s.get("score") is not None else "—",
                })
            st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
        else:
            st.info("No activity recorded yet. Start studying!")

    # ── Demo data button ───────────────────────────────────────────────────────
    st.divider()
    if st.button("🎭 Load Demo Data (showcase dashboard)", use_container_width=True):
        _load_demo_data()
        st.rerun()


def _empty_chart(message: str, height: int = 280):
    """Render an empty state placeholder."""
    st.markdown(
        f"""
        <div style="height:{height}px;display:flex;align-items:center;justify-content:center;
                    background:#1A1F2E;border:1px dashed #2D3748;border-radius:12px;
                    color:#555;font-size:0.9rem;text-align:center;padding:20px;">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _load_demo_data():
    """Populate session state with demo data for showcase."""
    import random
    import datetime as dt

    # Quiz history
    demo_topics = ["Neural Networks", "Gradient Descent", "Backpropagation", "CNNs", "Transformers"]
    st.session_state.quiz_history = [
        {"score": 45, "correct": 2, "total": 5, "topic": "Neural Networks"},
        {"score": 60, "correct": 3, "total": 5, "topic": "Gradient Descent"},
        {"score": 72, "correct": 4, "total": 5, "topic": "Backpropagation"},
        {"score": 80, "correct": 4, "total": 5, "topic": "CNNs"},
        {"score": 88, "correct": 5, "total": 5, "topic": "Transformers"},
    ]

    # Flashcard data
    st.session_state.flashcards = [{"question": f"Q{i}", "answer": f"A{i}"} for i in range(15)]
    st.session_state.cards_reviewed = set(range(12))
    st.session_state.cards_known = set(range(9))
    st.session_state.topics_studied = demo_topics

    # Sessions across last 7 days
    base = dt.datetime.now()
    activities = ["uploaded_file", "generated_flashcards", "completed_quiz", "analyzed_material", "generated_summary"]
    sessions = []
    for i in range(18):
        day_offset = random.randint(0, 6)
        ts = (base - dt.timedelta(days=day_offset, minutes=random.randint(0, 180))).isoformat()
        sessions.append({
            "timestamp": ts,
            "activity": random.choice(activities),
            "topic": random.choice(demo_topics),
            "score": random.randint(55, 95) if "quiz" in activities[0] else None,
        })
    st.session_state.study_sessions = sessions

    st.session_state.current_filename = "Machine Learning Notes"
    st.session_state.current_text = "Demo content loaded for dashboard showcase."
