"""Concept Map Page"""
import streamlit as st
import json


def render():
    st.markdown(
        """
        <div class="page-header">
            <h1>🗺️ Concept Map</h1>
            <p>AI-generated visual knowledge structure from your study material</p>
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

    if st.button("🗺️ Generate Concept Map", type="primary", use_container_width=True):
        with st.spinner("IBM Granite is building your concept map…"):
            from modules.granite_ai import generate_concept_map
            concept_map = generate_concept_map(st.session_state.current_text)
            st.session_state["concept_map"] = concept_map

    concept_map = st.session_state.get("concept_map")
    if not concept_map:
        st.info("Click **Generate Concept Map** to create a visual knowledge structure.")
        return

    central = concept_map.get("central_concept", "Core Concept")
    branches = concept_map.get("branches", [])

    # ── Visual concept map using HTML/SVG-style ────────────────────────────────
    st.markdown(
        f"""
        <div style="text-align:center;margin:20px 0;">
            <div style="display:inline-block;background:linear-gradient(135deg,#4F8BF9,#9B59B6);
                        color:white;padding:14px 28px;border-radius:30px;
                        font-size:1.3rem;font-weight:700;box-shadow:0 4px 20px rgba(79,139,249,0.4);">
                🎯 {central}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if branches:
        # Display in a grid of cards with connections
        cols = st.columns(min(3, len(branches)))
        colors = ["#4F8BF9", "#9B59B6", "#21BA45", "#FF8C00", "#FF4B4B", "#00BCD4"]

        for i, branch in enumerate(branches):
            col = cols[i % len(cols)]
            color = colors[i % len(colors)]
            connections_html = "".join(
                f'<span style="background:rgba(255,255,255,0.1);padding:2px 8px;'
                f'border-radius:10px;font-size:0.8rem;margin:2px;display:inline-block;">{c}</span>'
                for c in branch.get("connections", [])
            )
            col.markdown(
                f"""
                <div style="background:#1A1F2E;border:2px solid {color};border-radius:12px;
                            padding:16px;margin:8px 0;text-align:center;">
                    <div style="color:{color};font-weight:700;font-size:1rem;margin-bottom:8px;">
                        {branch.get('concept','')}
                    </div>
                    <div style="color:#8B9BB4;font-size:0.85rem;margin-bottom:10px;line-height:1.5;">
                        {branch.get('description','')}
                    </div>
                    <div style="margin-top:8px;">
                        {connections_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Relationship table ─────────────────────────────────────────────────────
    if branches:
        st.divider()
        st.markdown("#### 🔗 Concept Relationships")
        import pandas as pd
        rows = []
        for b in branches:
            for conn in b.get("connections", []):
                rows.append({
                    "From": central if not rows else b.get("concept", ""),
                    "Concept": b.get("concept", ""),
                    "Related To": conn,
                    "Description": b.get("description", "")[:80] + "…" if len(b.get("description","")) > 80 else b.get("description",""),
                })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Download as JSON ───────────────────────────────────────────────────────
    st.download_button(
        "⬇️ Download Concept Map (JSON)",
        data=json.dumps(concept_map, indent=2),
        file_name="concept_map.json",
        mime="application/json",
    )
