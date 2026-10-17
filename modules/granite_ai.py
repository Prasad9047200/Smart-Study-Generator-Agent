"""
IBM watsonx.ai Integration Module
Connects to IBM watsonx.ai using ibm-watsonx-ai SDK
"""

import os
import json
import re
import streamlit as st
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ── Configuration ─────────────────────────────────────────────────────────────
# Reads from Streamlit secrets (Cloud deploy) with fallback to env vars / defaults
import os

def _cfg(key: str, default: str = "") -> str:
    """Read from st.secrets first, then os.environ, then default."""
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, default)

IBM_API_KEY     = _cfg("IBM_API_KEY",     "")
IBM_PROJECT_ID  = _cfg("IBM_PROJECT_ID",  "")
IBM_URL         = _cfg("IBM_URL",         "https://us-south.ml.cloud.ibm.com")

# Supported model IDs for this watsonx.ai project
GRANITE_INSTRUCT = "meta-llama/llama-3-3-70b-instruct"   # primary — high quality
GRANITE_FAST     = "meta-llama/llama-3-1-8b"              # fast fallback


@st.cache_resource(show_spinner=False)
def get_granite_model(model_id: str = GRANITE_INSTRUCT) -> ModelInference:
    """Initialize and cache the IBM Granite model client."""
    credentials = Credentials(
        api_key=IBM_API_KEY,
        url=IBM_URL,
    )
    model = ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=IBM_PROJECT_ID,
        params={
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.TEMPERATURE: 0.3,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        },
    )
    return model


def generate_text(prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
    """Generate text from IBM Granite model."""
    try:
        model = get_granite_model()
        params = {
            GenParams.MAX_NEW_TOKENS: max_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        }
        response = model.generate_text(prompt=prompt, params=params)
        return response.strip() if response else ""
    except Exception as e:
        st.error(f"Granite AI Error: {str(e)}")
        return ""


# ── Summarization ─────────────────────────────────────────────────────────────
def summarize_content(text: str, style: str = "concise") -> str:
    """Summarize study material using IBM Granite."""
    style_map = {
        "concise": "Write a concise summary (3-5 bullet points) highlighting the key concepts.",
        "detailed": "Write a detailed, structured summary with main topics, subtopics, and key takeaways.",
        "eli5": "Explain this in simple terms as if explaining to a high school student. Use analogies.",
        "exam_ready": "Create an exam-focused summary highlighting definitions, formulas, and key facts likely to be tested.",
    }
    instruction = style_map.get(style, style_map["concise"])

    prompt = f"""<|system|>
You are an expert academic tutor and study assistant. Help students understand their study material.
<|user|>
{instruction}

Study Material:
{text[:3000]}

<|assistant|>
"""
    return generate_text(prompt, max_tokens=800, temperature=0.3)


# ── Flashcard Generation ──────────────────────────────────────────────────────
def generate_flashcards(text: str, num_cards: int = 10) -> list[dict]:
    """Generate Q&A flashcards from study content."""
    prompt = f"""<|system|>
You are an expert educational content creator. Create clear, exam-relevant flashcards.
<|user|>
Generate exactly {num_cards} flashcards from the study material below.
Return ONLY a valid JSON array. Each object must have "question" and "answer" keys.
Format: [{{"question": "...", "answer": "..."}}]

Study Material:
{text[:3000]}

<|assistant|>
["""
    response = generate_text(prompt, max_tokens=1500, temperature=0.4)
    # Prepend the opening bracket that was part of the prompt
    raw = "[" + response
    # Extract JSON array
    try:
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if match:
            cards = json.loads(match.group())
            return [c for c in cards if "question" in c and "answer" in c]
    except Exception:
        pass
    # Fallback: parse manually
    pairs = re.findall(r'"question"\s*:\s*"([^"]+)".*?"answer"\s*:\s*"([^"]+)"', raw, re.DOTALL)
    return [{"question": q, "answer": a} for q, a in pairs]


# ── Quiz Generation ───────────────────────────────────────────────────────────
def generate_quiz(text: str, num_questions: int = 5, difficulty: str = "medium") -> list[dict]:
    """Generate multiple-choice quiz questions."""
    prompt = f"""<|system|>
You are an expert exam question writer. Create challenging but fair multiple-choice questions.
<|user|>
Create {num_questions} multiple-choice questions at {difficulty} difficulty from the study material.
Return ONLY a valid JSON array. Each object must have:
- "question": the question text
- "options": array of 4 option strings (A, B, C, D)
- "correct": index of correct answer (0-3)
- "explanation": brief explanation of the correct answer

Study Material:
{text[:3000]}

<|assistant|>
["""
    response = generate_text(prompt, max_tokens=2000, temperature=0.4)
    raw = "[" + response
    try:
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if match:
            questions = json.loads(match.group())
            return [q for q in questions if "question" in q and "options" in q and "correct" in q]
    except Exception:
        pass
    return []


# ── Study Plan Generation ─────────────────────────────────────────────────────
def generate_study_plan(
    topics: list[str],
    exam_date: str,
    hours_per_day: float,
    weak_areas: list[str] = None,
) -> dict:
    """Generate a personalized study plan."""
    weak_str = ", ".join(weak_areas) if weak_areas else "none identified"
    topics_str = "\n".join(f"- {t}" for t in topics)

    prompt = f"""<|system|>
You are a professional academic coach who creates personalized, realistic study plans.
<|user|>
Create a detailed personalized study plan with the following parameters:
- Topics to cover: 
{topics_str}
- Exam date: {exam_date}
- Available study hours per day: {hours_per_day}
- Known weak areas: {weak_str}

Provide a JSON response with:
{{
  "daily_schedule": [{{"day": "Day 1", "date": "...", "topics": ["..."], "hours": X, "activities": ["..."]}}],
  "priority_topics": ["topic1", "topic2"],
  "study_tips": ["tip1", "tip2", "tip3"],
  "weekly_milestones": ["milestone1", "milestone2"],
  "predicted_readiness": "percentage and brief assessment"
}}

<|assistant|>
{{"""
    response = generate_text(prompt, max_tokens=2000, temperature=0.5)
    raw = "{" + response
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {
        "daily_schedule": [],
        "priority_topics": topics[:3] if topics else [],
        "study_tips": ["Review notes daily", "Practice past papers", "Use active recall"],
        "weekly_milestones": ["Complete topic review", "Practice quizzes"],
        "predicted_readiness": "Plan generation in progress...",
    }


# ── Topic Analysis & Predictions ──────────────────────────────────────────────
def analyze_topics(text: str) -> dict:
    """Extract and analyze key topics from study material."""
    prompt = f"""<|system|>
You are an expert academic analyst with deep knowledge of exam patterns and study strategies.
<|user|>
Analyze this study material and return a JSON response with:
{{
  "main_topics": ["topic1", "topic2", ...],
  "key_concepts": ["concept1", "concept2", ...],
  "difficulty_level": "beginner/intermediate/advanced",
  "estimated_study_time": "X hours",
  "exam_likely_topics": ["topic1", "topic2", ...],
  "prerequisites": ["prereq1", "prereq2", ...],
  "subject_area": "subject name"
}}

Study Material:
{text[:2000]}

<|assistant|>
{{"""
    response = generate_text(prompt, max_tokens=800, temperature=0.3)
    raw = "{" + response
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {
        "main_topics": [],
        "key_concepts": [],
        "difficulty_level": "intermediate",
        "estimated_study_time": "2-3 hours",
        "exam_likely_topics": [],
        "prerequisites": [],
        "subject_area": "General",
    }


# ── Concept Map ────────────────────────────────────────────────────────────────
def generate_concept_map(text: str) -> dict:
    """Generate a concept map structure from study material."""
    prompt = f"""<|system|>
You are an expert in knowledge visualization and concept mapping.
<|user|>
Create a concept map from the study material. Return JSON:
{{
  "central_concept": "main topic",
  "branches": [
    {{
      "concept": "subtopic",
      "connections": ["related concept 1", "related concept 2"],
      "description": "brief description"
    }}
  ]
}}

Study Material:
{text[:2000]}

<|assistant|>
{{"""
    response = generate_text(prompt, max_tokens=1000, temperature=0.3)
    raw = "{" + response
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"central_concept": "Study Material", "branches": []}


# ── Exam Prediction Alerts ─────────────────────────────────────────────────────
def get_exam_predictions(topics: list[str], subject: str = "") -> list[dict]:
    """Get AI-driven exam prediction alerts."""
    topics_str = ", ".join(topics[:10])
    prompt = f"""<|system|>
You are an expert exam coach with knowledge of common exam patterns and high-frequency topics.
<|user|>
Based on these topics from {subject or 'the subject'}: {topics_str}

Generate exam prediction alerts as JSON array:
[
  {{
    "topic": "topic name",
    "priority": "high/medium/low",
    "alert": "Focus on X — frequently tested in exams",
    "tip": "specific study tip for this topic"
  }}
]

Return 5-7 most important alerts.

<|assistant|>
["""
    response = generate_text(prompt, max_tokens=800, temperature=0.4)
    raw = "[" + response
    try:
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []


# ── Voice Query Processing ─────────────────────────────────────────────────────
def answer_study_question(question: str, context: str = "") -> str:
    """Answer a student's study question with optional context."""
    ctx_section = f"\nRelevant Study Material:\n{context[:1500]}\n" if context else ""
    prompt = f"""<|system|>
You are a knowledgeable, patient, and encouraging academic tutor. 
Provide clear, accurate, and helpful explanations. Use examples where helpful.
<|user|>
{ctx_section}
Student Question: {question}

<|assistant|>
"""
    return generate_text(prompt, max_tokens=600, temperature=0.4)
