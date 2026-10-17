"""Flashcards Page"""
import streamlit as st
from modules.utils import log_study_session


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>🃏 Flashcard Study</h1>
            <p>AI-generated flashcards from your study material — flip, review, and master</p>
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
    with st.expander("⚙️ Generate Flashcards", expanded=not bool(st.session_state.flashcards)):
        col1, col2 = st.columns([2, 1])
        with col1:
            num_cards = st.slider("Number of flashcards", 5, 20, 10)
        with col2:
            st.markdown(" ")
            gen_btn = st.button("✨ Generate Flashcards", type="primary", use_container_width=True)

        if gen_btn:
            with st.spinner("IBM Granite is creating flashcards…"):
                from modules.granite_ai import generate_flashcards
                cards = generate_flashcards(st.session_state.current_text, num_cards=num_cards)
            if cards:
                st.session_state.flashcards = cards
                st.session_state.current_card_index = 0
                st.session_state.card_flipped = False
                st.session_state.cards_reviewed = set()
                st.session_state.cards_known = set()
                log_study_session("generated_flashcards", topic=st.session_state.current_filename)
                st.success(f"✅ Generated **{len(cards)}** flashcards!")
                st.rerun()
            else:
                st.error("Could not generate flashcards. Please try again.")

    if not st.session_state.flashcards:
        st.info("Click **Generate Flashcards** above to create cards from your study material.")
        return

    cards = st.session_state.flashcards
    total = len(cards)
    idx = st.session_state.current_card_index
    reviewed = st.session_state.cards_reviewed
    known = st.session_state.cards_known

    # ── Progress bar ───────────────────────────────────────────────────────────
    progress = len(reviewed) / total if total else 0
    st.markdown(f"**Progress: {len(reviewed)}/{total} cards reviewed · {len(known)} known**")
    st.progress(progress)

    # ── Flashcard display ──────────────────────────────────────────────────────
    card = cards[idx]
    is_flipped = st.session_state.card_flipped
    card_num_display = f"Card {idx + 1} of {total}"

    side_label = "💡 Answer" if is_flipped else "❓ Question"
    side_content = card["answer"] if is_flipped else card["question"]
    side_color = "#21BA45" if is_flipped else "#4F8BF9"

    st.markdown(
        f"""
        <div class="flashcard">
            <div>
                <div style="color:{side_color};font-size:0.85rem;font-weight:600;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
                    {side_label}
                </div>
                <div style="font-size:1.15rem;line-height:1.7;">{side_content}</div>
                <div style="color:#555;font-size:0.75rem;margin-top:16px;">{card_num_display}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Controls ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])

    with c1:
        if st.button("⬅️ Prev", use_container_width=True, disabled=(idx == 0)):
            st.session_state.current_card_index = max(0, idx - 1)
            st.session_state.card_flipped = False
            st.rerun()

    with c2:
        if st.button("🔄 Flip", use_container_width=True, type="primary"):
            st.session_state.card_flipped = not is_flipped
            reviewed.add(idx)
            st.session_state.cards_reviewed = reviewed
            st.rerun()

    with c3:
        col_know, col_skip = st.columns(2)
        with col_know:
            if st.button("✅ Know It", use_container_width=True):
                known.add(idx)
                reviewed.add(idx)
                st.session_state.cards_known = known
                st.session_state.cards_reviewed = reviewed
                # Advance
                if idx < total - 1:
                    st.session_state.current_card_index = idx + 1
                    st.session_state.card_flipped = False
                else:
                    st.session_state.total_cards_reviewed += len(reviewed)
                    log_study_session(
                        "completed_flashcards",
                        score=round(len(known) / total * 100, 1),
                        topic=st.session_state.current_filename,
                    )
                st.rerun()
        with col_skip:
            if st.button("❌ Review Again", use_container_width=True):
                reviewed.add(idx)
                st.session_state.cards_reviewed = reviewed
                if idx < total - 1:
                    st.session_state.current_card_index = idx + 1
                    st.session_state.card_flipped = False
                st.rerun()

    with c4:
        if st.button("➡️ Next", use_container_width=True, disabled=(idx >= total - 1)):
            st.session_state.current_card_index = min(total - 1, idx + 1)
            st.session_state.card_flipped = False
            reviewed.add(idx)
            st.session_state.cards_reviewed = reviewed
            st.rerun()

    with c5:
        if st.button("🔀 Shuffle", use_container_width=True):
            import random
            random.shuffle(st.session_state.flashcards)
            st.session_state.current_card_index = 0
            st.session_state.card_flipped = False
            st.rerun()

    # ── All cards table ────────────────────────────────────────────────────────
    st.divider()
    with st.expander("📋 View All Flashcards"):
        for i, c in enumerate(cards):
            status = "✅" if i in known else ("👁️" if i in reviewed else "⬜")
            with st.container():
                st.markdown(
                    f"""
                    <div class="study-card" style="padding:12px 16px;">
                        <div style="display:flex;gap:12px;align-items:flex-start;">
                            <span style="font-size:1.2rem;min-width:28px;">{status}</span>
                            <div style="flex:1;">
                                <div style="color:#4F8BF9;font-weight:600;margin-bottom:4px;">
                                    Q{i+1}: {c['question']}
                                </div>
                                <div style="color:#8B9BB4;font-size:0.9rem;">
                                    {c['answer']}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── Session summary ────────────────────────────────────────────────────────
    if reviewed:
        mastery = round(len(known) / total * 100, 1)
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Cards Reviewed", len(reviewed))
        col_b.metric("Cards Known", len(known))
        col_c.metric("Mastery", f"{mastery}%")
