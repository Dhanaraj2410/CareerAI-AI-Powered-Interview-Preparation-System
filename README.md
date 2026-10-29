# CareerAI - AI-Powered Mock Interview & Career Assessment System

CareerAI is a **Python + Django + AI/ML + NLP** enterprise platform designed for candidate assessment, AI mock interviews, resume skill extraction, ATS scoring, and machine learning hiring readiness prediction.
---
## 🌟 Key Features

1. **AI Mock Interview Engine**:
   - Role-based curriculum sections (Python Developer, Data Scientist, ML Engineer, Data Analyst, Django Developer).
   - Per-question timer (60s / 120s / 180s) and progress tracker.
   - Web Speech API Voice-to-Text speech recognition with real-time transcript persistence.
   - Multi-Factor Answer Evaluator:
     $$\text{Final Score} = (0.50 \times \text{Similarity}) + (0.25 \times \text{Keyword}) + (0.15 \times \text{Completeness}) + (0.10 \times \text{Confidence})$$
   - 4-Tier Feedback Levels (`Excellent`, `Good`, `Average`, `Needs Improvement`).
   - Missing technical term extraction, conceptual hints, and reference answer explanations.
   - Section completion scorecards and **Targeted Revision Mode** for weak topics ($< 60\%$).

2. **Aptitude Learning & Solution Review**:
   - Randomized question selection across Quantitative, Reasoning, Verbal, and Data Interpretation.
   - Question-by-question solution review displaying exact option text (e.g. `60 km/h` instead of choice letter `B`).
   - Step-by-step math calculations, formulas, and `[ 🔄 Retry Wrong Questions ]` mode.

3. **Resume NLP Analyzer**:
   - PDF text extraction (`pdfplumber`/`pypdf`).
   - SpaCy / TF-IDF skill extraction and ATS match scoring against target role requirements.

4. **ML Candidate Performance Prediction Engine**:
   - Random Forest Classifier model trained on candidate assessment metrics.
   - Evaluated model accuracy ($83.00\%$), precision ($80.36\%$), recall ($88.24\%$), F1 score ($84.11\%$).
   - Computes weighted readiness labels (`EXCELLENT PROFILE`, `HIGH READINESS`, `MODERATE READINESS`, `NEEDS IMPROVEMENT`).

5. **Google Gemini AI Career Feedback**:
   - Synthesizes candidate test scores and interview performance into personalized 7-day study plans.

---

## 🔒 Security & Environment Setup

To keep API keys and secrets secure, **never commit `.env` files to GitHub**.

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your Google Gemini API Key in `.env`:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ```

---

## 🚀 Quickstart Guide

### 1. Installation
```bash
git clone https://github.com/Dhanaraj2410/CareerAI-AI-Powered-Interview-Preparation-System.git
cd CareerAI-AI-Powered-Interview-Preparation-System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Migrations & Seed Data
```bash
python manage.py makemigrations
python manage.py migrate

# Train ML Random Forest Model
python ml_engine/train_model.py

# Seed Question Banks
python manage.py shell -c "from interview.seed_questions import seed_interview_questions; seed_interview_questions(); from aptitude.seed_questions import seed_aptitude_questions; seed_aptitude_questions()"
```

### 3. Run Development Server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your web browser.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14, Django 5.x ORM
- **Machine Learning & NLP**: Scikit-Learn (Random Forest Classifier), Sentence-Transformers, TF-IDF Vectorizer, TextBlob
- **AI Synthesis**: Google Gemini Generative AI API (`google-generativeai`)
- **Frontend / Theme**: High-Contrast Slate & Neon Emerald GUI (`static/css/careerai-gui.css`)
- **Database**: SQLite3 (default) / MySQL supported
