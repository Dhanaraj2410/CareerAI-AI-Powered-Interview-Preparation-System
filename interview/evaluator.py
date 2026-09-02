"""
CareerAI Interview Multi-Factor NLP Evaluator Engine
---------------------------------------------------
Calculates similarity, keyword overlap, length completeness, and sentiment confidence.
Extrapolates 4-tier feedback levels and missing technical keywords.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

# Global cache for heavy SentenceTransformer model
_sentence_model = None

def get_sentence_model():
    """
    Lazy loader for SentenceTransformer ('all-MiniLM-L6-v2') embeddings.
    Returns model instance or None if library is unavailable.
    """
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            _sentence_model = False
    return _sentence_model if _sentence_model is not False else None

def evaluate_answer(expected_concepts, user_answer):
    """
    Calculates semantic cosine similarity between expected concepts and candidate response.
    Uses SentenceTransformer embeddings when available, falling back to TF-IDF vectorization.
    """
    if not user_answer or not user_answer.strip():
        return 0.0, "No response provided."

    st_model = get_sentence_model()
    score = 0.0
    evaluation_method = "TF-IDF Similarity"

    if st_model is not None:
        try:
            embeddings = st_model.encode([expected_concepts, user_answer])
            sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            score = float(sim) * 100.0
            evaluation_method = "Sentence Embedding Semantic Similarity"
        except Exception:
            st_model = None

    if st_model is None:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            vectors = vectorizer.fit_transform([expected_concepts, user_answer])
            sim = cosine_similarity(vectors[0], vectors[1])[0][0]
            score = float(sim) * 100.0
        except Exception:
            exp_words = set(expected_concepts.lower().split())
            usr_words = set(user_answer.lower().split())
            overlap = exp_words.intersection(usr_words)
            score = (len(overlap) / max(len(exp_words), 1)) * 100.0

    score = round(score, 2)
    feedback = f"[{evaluation_method}] Similarity Score: {score}%"
    return score, feedback

def analyze_sentiment(text):
    """
    Analyzes sentiment polarity and subjectivity using TextBlob.
    Maps polarity to communication confidence score (0 - 100%).
    """
    if not text or not text.strip():
        return "Uncertain", 0.0, 40.0

    if TextBlob is not None:
        try:
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            if polarity > 0.1:
                category = "Positive / Confident"
                conf_score = min(98.0, 75.0 + (polarity * 20.0))
            elif polarity < -0.1:
                category = "Negative / Uncertain"
                conf_score = max(40.0, 60.0 - (abs(polarity) * 20.0))
            else:
                category = "Neutral / Clear"
                conf_score = 70.0 + (subjectivity * 10.0)
                
            return category, round(polarity, 2), round(conf_score, 1)
        except Exception:
            pass

    words = text.lower().split()
    hesitancies = ['not sure', 'maybe', 'think', 'guess', 'dont know', "don't know"]
    if any(h in text.lower() for h in hesitancies):
        return "Negative / Uncertain", -0.2, 50.0
    return "Positive / Confident", 0.3, 80.0

def get_feedback_tier(score):
    """
    Maps percentage score to 4 feedback levels:
    - 80 to 100: Excellent (pass)
    - 60 to 79: Good (pass)
    - 40 to 59: Average (warn)
    - 0 to 39: Needs Improvement (danger)
    """
    if score >= 80:
        return "Excellent", "pass"
    elif score >= 60:
        return "Good", "pass"
    elif score >= 40:
        return "Average", "warn"
    else:
        return "Needs Improvement", "danger"

def get_missing_keywords(user_answer, keywords_str):
    """
    Extracts key technical terms missing from the candidate's answer.
    """
    kw_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
    if not kw_list:
        return []

    user_ans_lower = user_answer.lower()
    missing = [kw for kw in kw_list if kw.lower() not in user_ans_lower]
    return missing

def evaluate_answer_learning(expected_concepts, keywords_str, user_answer, hint_used=False):
    """
    Core Evaluation Formula:
    Final Score = (0.50 * Similarity) + (0.25 * Keyword) + (0.15 * Completeness) + (0.10 * Confidence)
    Applies 10% hint adjustment if candidate requested a hint.
    """
    if not user_answer or not user_answer.strip():
        return {
            "similarity_score": 0.0,
            "keyword_score": 0.0,
            "completeness_score": 0.0,
            "confidence_score": 0.0,
            "final_score": 0.0,
            "missing_keywords": keywords_str.split(','),
            "status_tier": "Needs Improvement",
            "tier_badge": "danger",
            "sentiment": "Uncertain",
            "feedback": "No response recorded. Please review the key concepts and try explaining the answer in your own words."
        }

    # 1. Similarity Score (50%)
    similarity_score, _ = evaluate_answer(expected_concepts, user_answer)

    # 2. Keyword Match (25%) & Missing Keywords
    kw_list = [k.strip() for k in keywords_str.split(',') if k.strip()]
    missing = get_missing_keywords(user_answer, keywords_str)
    
    if kw_list:
        matched = len(kw_list) - len(missing)
        keyword_score = round((matched / len(kw_list) * 100.0), 2)
    else:
        keyword_score = 50.0

    # 3. Completeness & Word Length (15%)
    word_count = len(user_answer.split())
    if word_count >= 30:
        completeness_score = 100.0
    elif word_count >= 15:
        completeness_score = 75.0
    elif word_count >= 8:
        completeness_score = 50.0
    else:
        completeness_score = 25.0

    # 4. Sentiment & Confidence (10%)
    sentiment_label, _, confidence_score = analyze_sentiment(user_answer)

    # Weighted Multi-Factor Calculation
    raw_final = (
        (similarity_score * 0.50) +
        (keyword_score * 0.25) +
        (completeness_score * 0.15) +
        (confidence_score * 0.10)
    )

    # Apply 10% Hint adjustment if hint was used
    if hint_used:
        raw_final = raw_final * 0.90

    final_score = round(min(100.0, max(0.0, raw_final)), 2)
    status_tier, tier_badge = get_feedback_tier(final_score)

    # Generate Tier-Specific Feedback Guidance
    if status_tier == "Excellent":
        feedback = "Excellent response! You accurately covered the core technical concepts. Try adding a real-world production example to make your answer even stronger."
    elif status_tier == "Good":
        feedback = f"Good response! You identified the main concept well. Try including these missing keywords for a complete answer: {', '.join(missing[:3])}."
    elif status_tier == "Average":
        feedback = f"Partially correct answer. You missed important technical terms ({', '.join(missing[:4])}). Review the reference answer below and expand your explanation."
    else:
        feedback = f"Needs improvement. Your answer missed several critical concepts ({', '.join(missing[:4]) if missing else 'definitions'}). Study the reference answer and key points below."

    return {
        "similarity_score": similarity_score,
        "keyword_score": keyword_score,
        "completeness_score": completeness_score,
        "confidence_score": confidence_score,
        "final_score": final_score,
        "missing_keywords": missing,
        "status_tier": status_tier,
        "tier_badge": tier_badge,
        "sentiment": sentiment_label,
        "feedback": feedback
    }

def get_adaptive_difficulty(score):
    """
    Determines difficulty for subsequent questions based on score:
    - score >= 80 -> hard
    - score >= 50 -> medium
    - score < 50 -> easy
    """
    if score >= 80:
        return "hard"
    elif score >= 50:
        return "medium"
    return "easy"
