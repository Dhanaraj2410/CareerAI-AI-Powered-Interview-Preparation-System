"""
CareerAI Resume NLP & AI Utilities - Skill Extraction & ATS Scoring
-------------------------------------------------------------------
Extracts text from PDFs, identifies technical skills, computes TF-IDF
based ATS match scores, and leverages Gemini AI for deep ATS analysis.
"""

import re
import os
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from careerai.gemini_service import is_gemini_configured, analyze_ai_resume_deep

logger = logging.getLogger('careerai.resumes')

# Comprehensive tech/domain skills vocabulary
KNOWN_SKILLS = [
    'python', 'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql', 'mongodb', 'sqlite',
    'javascript', 'typescript', 'react', 'node.js', 'express', 'html', 'css', 'bootstrap', 'tailwind', 'git', 'github',
    'machine learning', 'deep learning', 'nlp', 'natural language processing', 'computer vision',
    'data analysis', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'keras',
    'pytorch', 'scipy', 'matplotlib', 'seaborn', 'power bi', 'tableau', 'excel',
    'rest api', 'graphql', 'aws', 'docker', 'kubernetes', 'linux', 'data science',
    'statistics', 'linear algebra', 'oop', 'data structures', 'algorithms',
    'rag', 'langchain', 'generative ai', 'llm', 'transformers', 'huggingface',
    'ci/cd', 'agile', 'scrum', 'redis', 'celery'
]

ROLE_REQUIREMENTS = {
    'Python Developer': [
        'python', 'django', 'flask', 'sql', 'mysql', 'postgresql', 'rest api', 'git', 'oop', 'data structures'
    ],
    'Data Scientist': [
        'python', 'machine learning', 'data analysis', 'pandas', 'numpy', 'scikit-learn', 'statistics', 'sql', 'nlp', 'data science'
    ],
    'Machine Learning Engineer': [
        'python', 'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'sql', 'docker', 'algorithms'
    ],
    'Data Analyst': [
        'python', 'sql', 'data analysis', 'pandas', 'numpy', 'tableau', 'power bi', 'excel', 'statistics'
    ],
    'Web Developer': [
        'javascript', 'html', 'css', 'react', 'node.js', 'express', 'django', 'bootstrap', 'git', 'rest api'
    ]
}

def extract_resume_text(file_path):
    """
    Extract raw text from PDF or text resume using PyMuPDF (fitz), pdfplumber, or pypdf.
    """
    text = ""
    if not os.path.exists(file_path):
        return ""

    # Try PyMuPDF (fitz) - fastest and most reliable
    try:
        import fitz
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # Fallback to pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # If it's a plain text file
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception:
        pass

    return text.strip()

def analyze_resume_nlp(resume_text, target_role='Python Developer'):
    """
    Analyze resume text via NLP and Gemini AI:
    - Extracts technical skills
    - Calculates TF-IDF cosine similarity against target role
    - Identifies missing skills and weak sections
    - Generates actionable improvement suggestions
    """
    clean_text = resume_text.lower() if resume_text else ""
    
    # 1. Skill Extraction
    extracted = []
    for skill in KNOWN_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, clean_text):
            extracted.append(skill.title())

    # Direct Role Match & TF-IDF
    required_skills = ROLE_REQUIREMENTS.get(target_role, ROLE_REQUIREMENTS['Python Developer'])
    expected_doc = " ".join(required_skills)
    resume_doc = " ".join([s.lower() for s in extracted]) if extracted else clean_text

    if not resume_doc.strip():
        resume_doc = clean_text or "entry level candidate"

    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([expected_doc, resume_doc])
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        tfidf_score = round(similarity * 100, 1)
    except Exception:
        tfidf_score = 60.0

    matched_count = sum(1 for req in required_skills if req in [s.lower() for s in extracted])
    coverage_score = round((matched_count / len(required_skills)) * 100, 1) if required_skills else 50.0

    final_score = round(0.5 * tfidf_score + 0.5 * coverage_score, 1)
    if resume_text and final_score < 45.0:
        final_score = 55.0
    if final_score > 98.0:
        final_score = 98.0

    missing = [req.title() for req in required_skills if req not in [s.lower() for s in extracted]]

    # 2. Check if Gemini Deep Analysis is available
    gemini_data = None
    if is_gemini_configured() and resume_text:
        try:
            gemini_data = analyze_ai_resume_deep(resume_text, target_role=target_role)
        except Exception as e:
            logger.warning("Gemini deep resume analysis failed: %s", str(e))

    if gemini_data:
        # Merge Gemini insights
        ai_score = gemini_data.get('ats_score')
        if ai_score:
            final_score = round((final_score * 0.4) + (float(ai_score) * 0.6), 1)

        ai_extracted = gemini_data.get('extracted_skills', [])
        for s in ai_extracted:
            if s.title() not in extracted:
                extracted.append(s.title())

        ai_missing = gemini_data.get('missing_skills', [])
        for m in ai_missing:
            if m.title() not in missing:
                missing.append(m.title())

        weak_sections = gemini_data.get('weak_sections', [
            "Project outcome metrics could be more quantified",
            "Certifications or continuous learning section is sparse"
        ])
        suggestions = gemini_data.get('improvement_suggestions', [
            f"Add clear bullet points detailing your hands-on experience with {', '.join(missing[:3])}.",
            "Use the STAR method (Situation, Task, Action, Result) with measurable metrics.",
            "Tailor project descriptions to highlight software design and architecture choices."
        ])
        role_suitability = gemini_data.get('role_suitability', f"Candidate possesses foundational skills for {target_role}.")
        recommended_roles = gemini_data.get('recommended_roles', ['Software Engineer', 'Full Stack Developer'])
    else:
        # High-quality heuristic recommendations
        weak_sections = []
        if 'project' not in clean_text:
            weak_sections.append("Projects Section: Lack of detailed technical project descriptions")
        if 'experience' not in clean_text and 'work' not in clean_text:
            weak_sections.append("Work Experience: Lacks quantified deliverables or responsibilities")
        if not weak_sections:
            weak_sections.append("Action Metrics: Quantify accomplishments with % improvement or scale numbers")
            weak_sections.append("Technical Breadth: Highlight modern CI/CD, cloud, or testing frameworks")

        suggestions = [
            f"Integrate essential keywords for {target_role}: {', '.join(missing[:4])}." if missing else "Continue emphasizing specialized domain keywords.",
            "Incorporate measurable outcomes (e.g. 'Reduced latency by 35%', 'Engineered 12 REST endpoints').",
            "Ensure education and project tech stacks are clearly listed in dedicated sections."
        ]
        role_suitability = f"Candidate profile aligns {final_score}% with industry expectations for {target_role}."
        recommended_roles = [target_role, "Backend Developer", "Software Engineer"]

    return {
        'extracted_skills': extracted,
        'resume_score': final_score,
        'missing_skills': missing,
        'coverage_score': coverage_score,
        'tfidf_score': tfidf_score,
        'weak_sections': weak_sections,
        'suggestions': suggestions,
        'role_suitability': role_suitability,
        'recommended_roles': recommended_roles,
    }
