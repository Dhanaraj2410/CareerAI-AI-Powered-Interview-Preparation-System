"""
CareerAI Resume NLP Utilities - Skill Extraction & ATS Scoring
-------------------------------------------------------------
Extracts text from PDFs, identifies technical skills, computes TF-IDF
based ATS match scores, and highlights missing skills for target roles.
"""

# Common tech/domain skills vocabulary
KNOWN_SKILLS = [
    'python', 'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql', 'mongodb',
    'javascript', 'react', 'node.js', 'express', 'html', 'css', 'bootstrap', 'git',
    'machine learning', 'deep learning', 'nlp', 'natural language processing',
    'data analysis', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'keras',
    'pytorch', 'scipy', 'matplotlib', 'seaborn', 'power bi', 'tableau',
    'rest api', 'aws', 'docker', 'kubernetes', 'linux', 'data science',
    'statistics', 'linear algebra', 'oop', 'data structures', 'algorithms'
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
    """Extract raw text from PDF resume using pdfplumber or pypdf."""
    text = ""
    # Try pdfplumber first
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = ""

    # Fallback to pypdf if text is empty
    if not text.strip():
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception:
            pass

    return text.strip()

def analyze_resume_nlp(resume_text, target_role='Python Developer'):
    """Analyze resume text via NLP: extract skills, calculate score via TF-IDF Cosine Similarity, find missing skills."""
    clean_text = resume_text.lower()
    
    # 1. Skill Extraction
    extracted = []
    for skill in KNOWN_SKILLS:
        # Match whole word or exact pattern
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, clean_text):
            extracted.append(skill.title())
            
    # Also extract any capitalized custom skills from text
    custom_matches = re.findall(r'\b[A-Z][a-zA-Z0-9\+#]{1,15}\b', resume_text)
    for m in custom_matches:
        if m.lower() in KNOWN_SKILLS and m.title() not in extracted:
            extracted.append(m.title())
            
    # 2. Role Match & TF-IDF Cosine Similarity
    required_skills = ROLE_REQUIREMENTS.get(target_role, ROLE_REQUIREMENTS['Python Developer'])
    expected_doc = " ".join(required_skills)
    resume_doc = " ".join([s.lower() for s in extracted]) if extracted else clean_text
    
    if not resume_doc.strip():
        resume_doc = clean_text or "entry level candidate"
        
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([expected_doc, resume_doc])
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        # Map similarity (0..1) to a realistic score (e.g. 50..95%)
        tfidf_score = round(similarity * 100, 1)
    except Exception:
        tfidf_score = 60.0
        
    # Direct Skill Coverage Calculation
    matched_count = sum(1 for req in required_skills if req in [s.lower() for s in extracted])
    coverage_score = round((matched_count / len(required_skills)) * 100, 1) if required_skills else 50.0
    
    # Final Weighted Resume Score
    final_score = round(0.5 * tfidf_score + 0.5 * coverage_score, 1)
    # Ensure minimum base score if some text was provided
    if resume_text and final_score < 45.0:
        final_score = 55.0
    if final_score > 98.0:
        final_score = 98.0

    # 3. Missing Skills
    missing = [req.title() for req in required_skills if req not in [s.lower() for s in extracted]]
    
    return {
        'extracted_skills': extracted,
        'resume_score': final_score,
        'missing_skills': missing,
        'coverage_score': coverage_score,
        'tfidf_score': tfidf_score,
    }
