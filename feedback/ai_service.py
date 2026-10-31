"""
CareerAI AI Feedback Service - Integrated Gemini AI & ML Evaluation
-------------------------------------------------------------------
Generates personalized career recommendations using Google Gemini API
via the central `careerai.gemini_service` module.
"""

import os
import json
import logging
from careerai.gemini_service import is_gemini_configured, generate_gemini_text, clean_json_response

logger = logging.getLogger('careerai.feedback')

def generate_ai_career_feedback(aptitude_score, resume_score, technical_score, communication_score, target_role="Python Developer"):
    """
    Generate structured personalized feedback via Gemini API with intelligent local fallback.
    """
    prompt = f"""
You are an expert AI Career Coach evaluating a candidate preparing for a {target_role} role.

Candidate Metrics:
- Aptitude Score: {aptitude_score}%
- Resume NLP Match Score: {resume_score}%
- Technical Interview Score: {technical_score}%
- Communication & Confidence Score: {communication_score}%

Generate a comprehensive feedback report in valid JSON format with the following keys:
"overall_rating": float between 1.0 and 10.0,
"strengths": list of 3 concise strings describing specific strengths,
"areas_for_improvement": list of 3 concise strings describing areas to improve,
"recommendation": concise summary paragraph advising candidate on career readiness.

Respond ONLY with valid JSON.
"""
    if is_gemini_configured():
        text, err = generate_gemini_text(
            prompt,
            system_instruction="You are an expert executive career coach. Return strict JSON only.",
            json_mode=True
        )
        if text and not err:
            try:
                cleaned = clean_json_response(text)
                data = json.loads(cleaned)
                return {
                    'overall_rating': float(data.get('overall_rating', 8.0)),
                    'strengths': "\n".join([f"✓ {s.lstrip('✓').strip()}" for s in data.get('strengths', [])]),
                    'areas_for_improvement': "\n".join([f"⚠ {a.lstrip('⚠').strip()}" for a in data.get('areas_for_improvement', [])]),
                    'recommendation': data.get('recommendation', 'Candidate demonstrates strong career readiness.')
                }
            except Exception as e:
                logger.warning("Feedback JSON parsing fallback: %s", str(e))

    # Heuristic Intelligent Fallback
    avg_score = (aptitude_score + resume_score + technical_score + communication_score) / 4.0
    rating = round(min(9.8, max(4.0, (avg_score / 10.0))), 1)

    strengths = []
    if technical_score >= 75:
        strengths.append(f"✓ Strong technical problem-solving & core conceptual knowledge in {target_role}.")
    else:
        strengths.append(f"✓ Demonstrates solid foundational effort in the technical domain.")

    if resume_score >= 70:
        strengths.append("✓ Resume is well-structured with clear industry skill alignment.")
    else:
        strengths.append("✓ Good core background credentials listed in profile.")

    if aptitude_score >= 75:
        strengths.append("✓ High quantitative & logical analytical reasoning capability.")
    else:
        strengths.append("✓ Clear communication style during interview responses.")

    improvements = []
    if technical_score < 75:
        improvements.append("⚠ Deepen knowledge in complex framework mechanisms and advanced data structures.")
    if resume_score < 75:
        improvements.append("⚠ Add key industry terms and missing domain skills to boost resume NLP match.")
    if communication_score < 75:
        improvements.append("⚠ Practice structured articulation and confident delivery for behavioral questions.")
    if not improvements:
        improvements.append("⚠ Maintain continuous practice with mock interviews and time management.")

    recommendation = (
        f"Candidate shows solid preparation for an entry to mid-level {target_role} role. "
        f"By addressing the key areas above, interview selection probability will increase significantly."
    )

    return {
        'overall_rating': rating,
        'strengths': "\n".join(strengths),
        'areas_for_improvement': "\n".join(improvements),
        'recommendation': recommendation
    }
