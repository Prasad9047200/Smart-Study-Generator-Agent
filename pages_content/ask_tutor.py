"""Ask Tutor — AI Q&A Chat Page"""
import streamlit as st
from modules.utils import log_study_session


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>💬 AI Tutor Chat</h1>
            <p>Ask anything — IBM Granite answers your study questions with context from your material</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Context selector
    with st.expander("⚙️ Tutor Settings", expanded=False):
        use_context = st.checkbox(
            "📚 Use my uploaded study material as context",
            value=bool(st.session_state.current_text),
            help="When enabled, the AI will answer based on your uploaded study material.",
        )
        st.caption(
            f"Current material: **{st.session_state.current_filename or 'None'}**"
            + (f" ({len(st.session_state.current_text):,} chars)" if st.session_state.current_text else "")
        )

        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

    # ── Chat history display ───────────────────────────────────────────────────
    chat_history = st.session_state.chat_history

    if not chat_history:
        st.markdown(
            """
            <div style="text-align:center;padding:40px;color:#555;">
                <div style="font-size:3rem;">🤖</div>
                <div style="font-size:1.1rem;margin-top:12px;">
                    Hi! I'm your IBM Granite-powered study tutor.
                </div>
                <div style="font-size:0.9rem;margin-top:8px;">
                    Ask me anything about your study material or any academic topic.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Suggested questions
        st.markdown("#### 💡 Try asking:")
        suggestions = [
            "Summarize the key concepts from my notes",
            "Explain the difference between supervised and unsupervised learning",
            "What are the most important topics I should focus on?",
            "Create a mnemonic to help me remember the key steps",
            "What is likely to be tested in an exam on this topic?",
        ]
        cols = st.columns(2)
        for i, sug in enumerate(suggestions):
            if cols[i % 2].button(f"💬 {sug}", key=f"sug_{i}", use_container_width=True):
                _ask_question(sug, use_context)
                st.rerun()
    else:
        # Render chat bubbles
        for msg in chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user">👤 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bot">🤖 <strong style="color:#4F8BF9;">IBM Granite</strong><br><br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

    # ── Input area ─────────────────────────────────────────────────────────────
    st.divider()
    col_input, col_send = st.columns([5, 1])
    with col_input:
        question = st.text_input(
            "Ask your question",
            placeholder="Type your question and press Enter or click Ask…",
            label_visibility="collapsed",
            key="tutor_input",
        )
    with col_send:
        send_btn = st.button("Ask 🚀", type="primary", use_container_width=True)

    if send_btn and question.strip():
        _ask_question(question.strip(), use_context)
        st.rerun()
    elif send_btn:
        st.warning("Please type a question.")

    # ── Voice note tip ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="margin-top:12px;padding:10px 16px;background:#1A1F2E;border:1px solid #2D3748;
                    border-radius:8px;color:#555;font-size:0.83rem;">
            🎙️ <strong>Voice queries:</strong> Use your browser's speech-to-text (microphone icon in the text field)
            to dictate your questions hands-free.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Quick action buttons ───────────────────────────────────────────────────
    if st.session_state.current_text:
        st.divider()
        st.markdown("**⚡ Quick Actions**")
        qa1, qa2, qa3, qa4 = st.columns(4)
        if qa1.button("📝 Summarize my notes", use_container_width=True):
            _ask_question("Please summarize the key points from my study material.", use_context=True)
            st.rerun()
        if qa2.button("🎯 Exam tips", use_container_width=True):
            _ask_question("What are the most important topics likely to appear in an exam based on my study material?", use_context=True)
            st.rerun()
        if qa3.button("🔍 Explain key terms", use_container_width=True):
            _ask_question("List and explain the most important technical terms and definitions from my study material.", use_context=True)
            st.rerun()
        if qa4.button("🧩 Practice problem", use_container_width=True):
            _ask_question("Give me a challenging practice problem or scenario based on my study material, then explain the solution.", use_context=True)
            st.rerun()


def _ask_question(question: str, use_context: bool = False):
    """Add user question to history and generate AI response."""
    chat_history = st.session_state.chat_history
    chat_history.append({"role": "user", "content": question})

    context = st.session_state.current_text if use_context else ""

    with st.spinner("IBM Granite is thinking…"):
        from modules.granite_ai import answer_study_question
        answer = answer_study_question(question, context=context)

    if answer:
        chat_history.append({"role": "assistant", "content": answer})
        log_study_session("asked_tutor", topic=question[:50])
    else:
        chat_history.append({
            "role": "assistant",
            "content": "I'm sorry, I couldn't generate a response. Please check your IBM watsonx.ai connection and try again.",
        })

    st.session_state.chat_history = chat_history
