# 🎓 Smart Study Generator Agent

An AI-powered study companion built with **Streamlit** and **IBM watsonx.ai** (Meta Llama 3.3 70B Instruct).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📚 **Study Material** | Upload PDF, DOCX, images (OCR), or paste text |
| 🃏 **Flashcards** | AI-generated Q&A cards from your content |
| 📝 **Quiz** | Multiple-choice quizzes with difficulty levels |
| 🗺️ **Concept Map** | Visual knowledge graph of topics |
| 📅 **Study Plan** | Personalised schedule based on exam date |
| 💬 **Ask Tutor** | Conversational AI tutor with material context |
| 📊 **Dashboard** | Progress tracking with charts |
| 🔔 **Exam Alerts** | AI-driven topic priority predictions |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Prasad9047200/smart-study-generator-agent.git
cd smart-study-generator-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure credentials

Create `.streamlit/secrets.toml`:
```toml
IBM_API_KEY = "your-ibm-watsonx-api-key"
IBM_PROJECT_ID = "your-project-id"
IBM_URL = "https://us-south.ml.cloud.ibm.com"
```

> **Note:** Never commit your `secrets.toml`. It is already in `.gitignore`.

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🏗️ Project Structure

```
smart-study-generator-agent/
├── app.py                      # Main Streamlit app & router
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml             # Theme & server config
├── modules/
│   ├── granite_ai.py           # IBM watsonx.ai integration
│   └── utils.py                # Session state & helpers
└── pages_content/
    ├── home.py
    ├── study_material.py
    ├── flashcards.py
    ├── quiz.py
    ├── concept_map.py
    ├── study_plan.py
    ├── ask_tutor.py
    └── dashboard.py
```

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch `main`, and entry file `app.py`.
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   IBM_API_KEY = "your-ibm-watsonx-api-key"
   IBM_PROJECT_ID = "your-project-id"
   IBM_URL = "https://us-south.ml.cloud.ibm.com"
   ```
5. Click **Deploy**.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io) ≥ 1.32
- **AI Model:** Meta Llama 3.3 70B Instruct via [IBM watsonx.ai](https://www.ibm.com/watsonx)
- **PDF Parsing:** PyPDF2
- **OCR:** pytesseract + Pillow
- **Charts:** Plotly
- **Speech:** SpeechRecognition

---

## 📄 License

MIT License — feel free to use and adapt.

---

*Powered by IBM watsonx.ai · Model: Llama 3.3 70B Instruct*
