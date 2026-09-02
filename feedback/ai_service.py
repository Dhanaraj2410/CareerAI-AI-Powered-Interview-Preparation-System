import os
import json

def generate_ai_career_feedback(aptitude_score, resume_score, technical_score, communication_score, target_role="Python Developer"):
    """
    Generate structured personalized feedback via Gemini API or intelligent rule-based engine.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

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

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            return {
                'overall_rating': float(data.get('overall_rating', 7.8)),
                'strengths': "\n".join([f"✓ {s}" for s in data.get('strengths', [])]),
                'areas_for_improvement': "\n".join([f"⚠ {a}" for a in data.get('areas_for_improvement', [])]),
                'recommendation': data.get('recommendation', 'Candidate is well-prepared for technical interviews.')
            }
        except Exception as e:
            pass

    # Intelligent Fallback Engine
    avg_score = (aptitude_score + resume_score + technical_score + communication_score) / 4.0
    rating = round(min(9.8, max(4.0, (avg_score / 10.0))), 1)

    strengths = []
    if python_or_tech := (technical_score >= 75):
        strengths.append(f"✓ Strong technical problem-solving & core conceptual knowledge in {target_role}.")
    else:
        strengths.append(f"✓ Demonstrates solid foundational attempt in technical domain.")

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
