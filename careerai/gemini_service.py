"""
CareerAI Centralized Google Gemini AI Service
---------------------------------------------
Powered by the official Google Gen AI Python SDK (`google-genai`).
Handles authentication, request construction, structured JSON generation,
rate limits, error handling, logging, and graceful offline fallback.
"""

import os
import re
import json
import time
import logging
from django.conf import settings

logger = logging.getLogger('careerai.gemini')

# Read configuration from environment with sensible defaults
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
DEFAULT_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash').strip()

# Dummy/placeholder keys that should not be used for actual remote calls
PLACEHOLDER_KEYS = {
    '', 'your_actual_api_key', 'your_google_gemini_api_key_here',
    'your-google-gemini-api-key-here', 'your_api_key_here', 'dummy'
}

def get_api_key():
    """Retrieve and sanitize Gemini API key from environment."""
    key = os.environ.get('GEMINI_API_KEY', '').strip()
    return key

def get_active_model():
    """Retrieve active Gemini model name from environment."""
    return os.environ.get('GEMINI_MODEL', DEFAULT_MODEL).strip()

def is_gemini_configured():
    """Check if a valid, non-placeholder Gemini API key is configured."""
    key = get_api_key()
    return bool(key and key not in PLACEHOLDER_KEYS and len(key) > 15)

def get_gemini_client():
    """
    Instantiate official google-genai Client.
    Returns Client instance or None if not configured.
    """
    if not is_gemini_configured():
        return None
    try:
        from google import genai
        return genai.Client(api_key=get_api_key())
    except Exception as exc:
        logger.error("Failed to initialize google-genai Client: %s", str(exc))
        return None

def check_gemini_health():
    """
    Administrator API health-check mechanism.
    Verifies configuration, connectivity, and model response.
    Never exposes API key in response or logs.
    """
    configured = is_gemini_configured()
    model_name = get_active_model()
    
    if not configured:
        return {
            'configured': False,
            'status': 'unconfigured',
            'model': model_name,
            'latency_ms': None,
            'message': 'Gemini API key is not configured or uses a placeholder. Using intelligent local fallback engines.'
        }
        
    start_time = time.time()
    try:
        client = get_gemini_client()
        if not client:
            return {
                'configured': True,
                'status': 'error',
                'model': model_name,
                'latency_ms': None,
                'message': 'Failed to instantiate google-genai Client.'
            }

        response = client.models.generate_content(
            model=model_name,
            contents="Hello! Respond with: {'status': 'healthy'}"
        )
        latency_ms = round((time.time() - start_time) * 1000, 1)

        return {
            'configured': True,
            'status': 'healthy',
            'model': model_name,
            'latency_ms': latency_ms,
            'sample_response': (response.text or '')[:120].strip(),
            'message': f"Gemini API is operational (Model: {model_name}, Latency: {latency_ms}ms)."
        }
    except Exception as exc:
        latency_ms = round((time.time() - start_time) * 1000, 1)
        err_msg = str(exc)
        # Sanitize error message to avoid secret leakage
        sanitized_msg = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_API_KEY]', err_msg)
        logger.warning("Gemini health check error: %s", sanitized_msg)
        return {
            'configured': True,
            'status': 'error',
            'model': model_name,
            'latency_ms': latency_ms,
            'message': f"Gemini API error: {sanitized_msg[:200]}"
        }

def clean_json_response(raw_text):
    """Clean markdown code fences from JSON output."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()

def generate_gemini_text(prompt, system_instruction=None, json_mode=False):
    """
    Base helper to query Gemini with standard error handling.
    Returns (response_text, error_message).
    """
    if not is_gemini_configured():
        return None, "Gemini API key not configured"

    client = get_gemini_client()
    if not client:
        return None, "Unable to initialize Gemini client"

    model_name = get_active_model()
    try:
        from google.genai import types
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction
        if json_mode:
            config.response_mime_type = "application/json"

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        return (response.text or "").strip(), None
    except Exception as exc:
        sanitized_err = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_KEY]', str(exc))
        logger.warning("Gemini generation failed: %s", sanitized_err)
        return None, sanitized_err

# -------------------------------------------------------------------
# Domain Feature 1: AI Mock Interview Generation & Evaluation
# -------------------------------------------------------------------

def generate_ai_interview_questions(role="Python Developer", difficulty="Intermediate", interview_type="Technical", count=5):
    """
    Generates dynamic interview questions tailored to the chosen role,
    difficulty, and interview type (Technical, HR, Coding, Mixed).
    """
    prompt = f"""
You are an expert technical interviewer at a top technology company.
Generate {count} distinct, realistic interview questions for a candidate applying for the role of '{role}'.
Interview Difficulty Level: {difficulty}
Interview Question Type: {interview_type} (e.g. Technical deep-dive, HR behavioral/situational, Coding logic/syntax, or Mixed).

Return a strict JSON list of {count} question objects with this schema:
[
  {{
    "question_text": "Clear, realistic interview question prompt",
    "topic": "Core topic name (e.g. Memory Management, System Design, REST APIs, STAR Behavioral)",
    "expected_concepts": "Key theoretical concepts and technical points the candidate should address",
    "keywords": "comma, separated, key, technical, terms",
    "hint": "Helpful conceptual hint to guide the candidate if they get stuck",
    "explanation": "Comprehensive reference answer and architectural explanation"
  }}
]

Return ONLY raw valid JSON array.
"""
    system_inst = "You are an elite enterprise interviewer. Output strictly valid JSON."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst, json_mode=True)

    if text and not err:
        try:
            cleaned = clean_json_response(text)
            data = json.loads(cleaned)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception as e:
            logger.warning("Failed to parse Gemini generated questions JSON: %s", str(e))

    # Curated High-Quality Fallbacks by Role
    fallbacks = {
        "Python Developer": [
            {
                "question_text": "Explain Python's memory management model, including the GIL, memory allocation via PyMalloc, and garbage collection via reference counting.",
                "topic": "Python Internals",
                "expected_concepts": "Global Interpreter Lock (GIL), PyMalloc allocator, reference counting, cyclic garbage collection, generational GC.",
                "keywords": "GIL, reference counting, cyclic garbage collection, pymalloc, memory allocation",
                "hint": "Think about CPython's execution model and how circular references are handled.",
                "explanation": "CPython uses reference counting as its primary mechanism and a cyclic garbage collector to detect unreachable reference cycles across three generations."
            },
            {
                "question_text": "What are Python generators and iterators? How does the 'yield' keyword differ from 'return' in terms of execution context and memory footprint?",
                "topic": "Generators & Iterators",
                "expected_concepts": "Iterator protocol (__iter__ and __next__), lazy evaluation, suspended execution state, lower memory usage.",
                "keywords": "generator, yield, iterator, __iter__, __next__, lazy evaluation, memory efficiency",
                "hint": "Consider what happens to local stack frames when yield produces a value.",
                "explanation": "Generators implement the iterator protocol using 'yield', pausing execution and retaining state between calls without allocating memory for an entire collection."
            },
            {
                "question_text": "How does Django's ORM handle database relationships? Explain the performance difference between select_related and prefetch_related.",
                "topic": "Django ORM Optimization",
                "expected_concepts": "SQL JOIN vs separate queries with Python-side joining, N+1 query problem, ForeignKey vs ManyToManyField.",
                "keywords": "select_related, prefetch_related, SQL JOIN, N+1 problem, ForeignKey, ManyToMany",
                "hint": "One performs a SQL JOIN for single-valued relations, while the other handles multi-valued relations via separate queries.",
                "explanation": "select_related performs a SQL JOIN suitable for single-valued relationships (ForeignKey, OneToOne). prefetch_related executes an additional query and joins in Python, ideal for ManyToMany and reverse relations."
            },
            {
                "question_text": "Explain Python decorators. How would you write a parameterized decorator that logs function execution time and caches return values?",
                "topic": "Advanced Decorators",
                "expected_concepts": "First-class functions, closures, functools.wraps, three levels of nested functions for decorators with arguments.",
                "keywords": "decorator, closure, wraps, functools, higher-order functions",
                "hint": "Remember that a decorator taking arguments requires an outer factory function returning the actual decorator.",
                "explanation": "Decorators wrap functions using closures. A parameterized decorator takes configuration args in an outer function, which returns a decorator that returns the wrapped function."
            },
            {
                "question_text": "How do you design a thread-safe singleton in Python? What are the trade-offs compared to module-level singletons or metaclasses?",
                "topic": "Design Patterns",
                "expected_concepts": "__new__ override, threading.Lock, double-checked locking, Python module caching as natural singleton.",
                "keywords": "singleton, __new__, threading.Lock, double-checked locking, metaclass",
                "hint": "Python modules are already singletons by nature due to sys.modules caching.",
                "explanation": "A thread-safe singleton locks execution during the first instantiation via threading.Lock or uses Python module-level instantiation which is inherently a singleton."
            }
        ]
    }

    # Return role-specific or generic fallback slice
    return fallbacks.get(role, fallbacks["Python Developer"])[:count]

def evaluate_ai_interview_answer(role, question_text, user_answer, expected_concepts="", keywords=""):
    """
    Evaluates candidate's interview answer using Gemini.
    Provides numerical score (0-100), detailed feedback, strengths,
    weaknesses, and an improved ideal answer.
    """
    if not user_answer or not user_answer.strip():
        return {
            "score": 0.0,
            "feedback": "No answer was provided. Please explain the answer in your own words.",
            "strengths": ["None identified (empty response)"],
            "weaknesses": ["Candidate did not provide an answer"],
            "improved_answer": expected_concepts or "A thorough answer should clearly explain the core concepts.",
            "status_tier": "Needs Improvement",
            "tier_badge": "danger"
        }

    prompt = f"""
You are a Senior Principal Interviewer assessing a candidate for a '{role}' position.

Question Asked:
"{question_text}"

Expected Concepts:
"{expected_concepts}"

Important Keywords:
"{keywords}"

Candidate's Actual Answer:
"{user_answer}"

Evaluate the candidate's answer constructively, fairly, and accurately.
Return a strict JSON object with these keys:
{{
  "score": float between 0.0 and 100.0,
  "feedback": "Concise 2-3 sentence evaluative summary of candidate's response",
  "strengths": ["Bullet point 1", "Bullet point 2"],
  "weaknesses": ["Constructive gap 1", "Constructive gap 2"],
  "improved_answer": "A model answer demonstrating high technical clarity and depth",
  "status_tier": "Excellent" | "Good" | "Average" | "Needs Improvement"
}}

Return ONLY valid JSON.
"""
    system_inst = "You are an expert technical interviewer. Return strict JSON only."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst, json_mode=True)

    if text and not err:
        try:
            cleaned = clean_json_response(text)
            data = json.loads(cleaned)
            score = float(data.get("score", 70.0))
            status_tier = data.get("status_tier", "Good")
            
            # Ensure tier_badge
            tier_badge = "pass" if score >= 60 else ("warn" if score >= 40 else "danger")
            
            return {
                "score": score,
                "feedback": data.get("feedback", "Good effort demonstrating relevant understanding."),
                "strengths": data.get("strengths", ["Addressed core topic concepts"]),
                "weaknesses": data.get("weaknesses", ["Could provide deeper architectural context"]),
                "improved_answer": data.get("improved_answer", expected_concepts),
                "status_tier": status_tier,
                "tier_badge": tier_badge
            }
        except Exception as e:
            logger.warning("Failed to parse Gemini evaluation JSON: %s", str(e))

    # Smart fallback evaluation based on word count & keyword overlap
    words = user_answer.lower().split()
    kw_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
    matched = [k for k in kw_list if k in user_answer.lower()]
    kw_ratio = (len(matched) / max(len(kw_list), 1)) if kw_list else 0.5
    length_ratio = min(1.0, len(words) / 45.0)

    score = round((kw_ratio * 60.0) + (length_ratio * 40.0), 1)
    if score >= 80:
        tier, badge = "Excellent", "pass"
    elif score >= 60:
        tier, badge = "Good", "pass"
    elif score >= 40:
        tier, badge = "Average", "warn"
    else:
        tier, badge = "Needs Improvement", "danger"

    strengths = []
    if matched:
        strengths.append(f"Successfully incorporated key terms: {', '.join(matched[:4])}")
    if len(words) >= 30:
        strengths.append("Provided a substantive explanation with descriptive depth.")
    else:
        strengths.append("Demonstrated foundational familiarity with the topic.")

    weaknesses = []
    missing_kw = [k for k in kw_list if k not in user_answer.lower()]
    if missing_kw:
        weaknesses.append(f"Missing core technical concepts: {', '.join(missing_kw[:4])}")
    if len(words) < 25:
        weaknesses.append("Response is brief. Consider elaborating with practical architectural examples.")

    return {
        "score": score,
        "feedback": f"Your response addressed key elements with {score}% conceptual alignment. Review the model answer to deepen technical precision.",
        "strengths": strengths or ["Good direct attempt at the question."],
        "weaknesses": weaknesses or ["Continue practicing complete end-to-end explanations."],
        "improved_answer": expected_concepts or "A complete answer covers the core architecture, edge cases, and performance considerations.",
        "status_tier": tier,
        "tier_badge": badge
    }

# -------------------------------------------------------------------
# Domain Feature 2: AI Resume Summary & Deep ATS Analysis
# -------------------------------------------------------------------

def generate_ai_resume_summary(name, target_role, skills, experience, education=""):
    """
    Generates a high-impact, professional executive resume summary using Gemini.
    """
    prompt = f"""
You are an executive resume writer and career coach.
Craft a compelling, modern 3-4 sentence professional summary for a candidate's resume.

Candidate Information:
- Candidate Name: {name}
- Target Role: {target_role}
- Core Skills: {skills}
- Experience / Background: {experience}
- Education: {education}

Write a persuasive, ATS-friendly summary emphasizing technical expertise, problem-solving impact, and readiness.
Do not use bullet points or markdown headings; return only the polished summary paragraph.
"""
    system_inst = "You are a professional executive resume writer. Output plain text paragraph."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst)
    if text and not err:
        return text.strip()

    # Fallback professional summary template
    return (
        f"Results-oriented {target_role} with proven proficiency in {skills or 'modern software engineering'}. "
        f"Experienced in developing scalable applications, optimizing algorithmic performance, and applying software design patterns. "
        f"Committed to clean code quality, collaborative team delivery, and accelerating product innovation in fast-paced engineering environments."
    )

def analyze_ai_resume_deep(resume_text, target_role="Python Developer"):
    """
    Conducts deep ATS resume analysis using Gemini, extracting skills,
    identifying weak sections, missing high-demand skills, and actionable suggestions.
    """
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and Senior Technical Hiring Manager.
Analyze the following resume text specifically for the target role of '{target_role}'.

Resume Content:
\"\"\"
{resume_text[:4000]}
\"\"\"

Perform a deep ATS assessment and return a strict JSON object with:
{{
  "ats_score": integer between 30 and 98 representing ATS suitability score,
  "extracted_skills": ["List", "of", "technical", "skills", "found"],
  "missing_skills": ["List", "of", "high-priority", "skills", "missing", "for", "{target_role}"],
  "weak_sections": ["Section 1 needing improvement", "Section 2 needing improvement"],
  "improvement_suggestions": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3"
  ],
  "role_suitability": "Short 1-2 sentence assessment of candidate alignment with {target_role}",
  "recommended_roles": ["Alternative Role 1", "Alternative Role 2"]
}}

Return ONLY valid JSON.
"""
    system_inst = "You are an ATS parser and senior recruiter. Return strictly valid JSON."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst, json_mode=True)

    if text and not err:
        try:
            cleaned = clean_json_response(text)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.warning("Failed to parse Gemini resume analysis JSON: %s", str(e))

    return None

# -------------------------------------------------------------------
# Domain Feature 3: Group Discussion (GD) Generation & Evaluation
# -------------------------------------------------------------------

def generate_ai_gd_topic(category="Tech Trends"):
    """
    Generates a thought-provoking Group Discussion topic with context,
    key perspectives, and evaluation guidance.
    """
    prompt = f"""
You are a corporate hiring panelist conducting Group Discussion (GD) rounds for top tech employers.
Generate a contemporary Group Discussion topic for category: '{category}'.

Return a strict JSON object:
{{
  "title": "Clear, engaging GD topic statement",
  "category": "{category}",
  "description": "2-3 sentences explaining the background, context, and modern significance of this debate",
  "pro_arguments": ["Strong point in favor 1", "Strong point in favor 2"],
  "con_arguments": ["Strong counter-argument 1", "Strong counter-argument 2"],
  "key_discussion_points": ["Key sub-theme 1", "Key sub-theme 2", "Key sub-theme 3"]
}}

Return ONLY valid JSON.
"""
    system_inst = "You are an expert GD moderator. Return strictly valid JSON."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst, json_mode=True)

    if text and not err:
        try:
            cleaned = clean_json_response(text)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning("Failed to parse Gemini GD topic JSON: %s", str(e))

    # Curated GD Topic Fallbacks
    topics = [
        {
            "title": "Artificial Intelligence in Hiring: Efficiency vs. Algorithmic Bias",
            "category": "AI & Ethics",
            "description": "Automated AI resume screeners and algorithmic interview tools promise speed and scalability, but critics highlight perpetuation of demographic bias and dehumanization.",
            "pro_arguments": ["Reduces human recruiter cognitive fatigue", "Processes massive candidate pipelines objectively", "Identifies non-traditional candidates based on skills"],
            "con_arguments": ["Historic training data replicates past biases", "Lack of transparency in black-box models", "Misses nuanced human empathy and creative culture-fit"],
            "key_discussion_points": ["Auditability of ML algorithms", "Human-in-the-loop governance", "Candidate privacy and data protection"]
        },
        {
            "title": "Remote Work vs. Return-to-Office: The Future of Engineering Culture",
            "category": "Corporate Culture",
            "description": "Tech companies are split between distributed async remote work and mandatory in-office collaboration for software development teams.",
            "pro_arguments": ["Global talent access without geographic borders", "Reduced commute stress and improved developer focus", "Lower real-estate overhead for organizations"],
            "con_arguments": ["Impromptu hallway problem-solving is diminished", "Onboarding junior developers requires higher overhead", "Risk of isolation and blurred work-life boundaries"],
            "key_discussion_points": ["Hybrid workspace models", "Async documentation standards", "Measuring developer output vs presence"]
        },
        {
            "title": "Open Source vs. Proprietary AI Models: The Battle for Innovation Control",
            "category": "Tech Trends",
            "description": "The rapid democratization of open weights LLMs challenges closed proprietary AI ecosystems in terms of safety, transparency, and commercial advantage.",
            "pro_arguments": ["Enables transparent security auditing and customization", "Prevents monopoly lock-in by hyper-scalers", "Accelerates academic research and global accessibility"],
            "con_arguments": ["Higher risk of unregulated misuse without safety filters", "Lack of commercial support and sustained compute funding", "Potential IP copyright complexities"],
            "key_discussion_points": ["Model licensing and safety guardrails", "On-premise enterprise deployment", "Cost-benefit of fine-tuning open models"]
        }
    ]
    import random
    return random.choice(topics)

def evaluate_ai_gd_response(topic_title, topic_description, candidate_text):
    """
    Evaluates a candidate's Group Discussion contribution based on
    text communication, relevance, clarity, structure, and balance.
    """
    if not candidate_text or not candidate_text.strip():
        return {
            "overall_score": 0.0,
            "relevance_score": 0.0,
            "clarity_score": 0.0,
            "structure_score": 0.0,
            "feedback": "No contribution was recorded for this discussion.",
            "strengths": ["None identified"],
            "improvements": ["Please provide your perspectives on the discussion topic."],
            "key_takeaway": "Participation is vital in a group discussion."
        }

    prompt = f"""
You are an expert assessor in a corporate recruitment Group Discussion (GD) round.

Topic: "{topic_title}"
Context: "{topic_description}"

Candidate's Submission:
\"\"\"
{candidate_text}
\"\"\"

Assess the candidate's contribution based on textual indicators of communication, argument relevance, reasoning clarity, and balanced perspective. Note: evaluate textual quality only without claiming to measure physiological speaking traits.

Return a strict JSON object:
{{
  "overall_score": float between 0.0 and 100.0,
  "relevance_score": float between 0.0 and 100.0,
  "clarity_score": float between 0.0 and 100.0,
  "structure_score": float between 0.0 and 100.0,
  "feedback": "2-3 sentences evaluating the substance and delivery of candidate's viewpoint",
  "strengths": ["Strong point 1", "Strong point 2"],
  "improvements": ["Constructive suggestion 1", "Constructive suggestion 2"],
  "key_takeaway": "Actionable takeaway for subsequent GD rounds"
}}

Return ONLY valid JSON.
"""
    system_inst = "You are a senior GD evaluator. Return strictly valid JSON."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst, json_mode=True)

    if text and not err:
        try:
            cleaned = clean_json_response(text)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning("Failed to parse Gemini GD evaluation JSON: %s", str(e))

    # Smart fallback GD scoring
    word_count = len(candidate_text.split())
    relevance = min(90.0, max(45.0, word_count * 0.8))
    clarity = min(88.0, 60.0 + (word_count * 0.2))
    structure = 75.0 if any(punct in candidate_text for punct in ['.', '\n', ';']) else 55.0
    overall = round((relevance + clarity + structure) / 3.0, 1)

    return {
        "overall_score": overall,
        "relevance_score": relevance,
        "clarity_score": clarity,
        "structure_score": structure,
        "feedback": f"Demonstrated constructive participation with {word_count} words articulated. Articulation shows relevant perspectives on '{topic_title}'.",
        "strengths": ["Expressed a defined point of view", "Clear grammatical expression"],
        "improvements": ["Incorporate real-world case studies or statistics to strengthen claims", "Acknowledge counter-arguments before concluding"],
        "key_takeaway": "Structure your arguments using the PREP method (Point, Reason, Example, Point)."
    }

# -------------------------------------------------------------------
# Domain Feature 4: AI Learning Assistant / Technical Chatbot
# -------------------------------------------------------------------

CHATBOT_SYSTEM_PROMPT = """
You are 'CareerAI Assistant', an expert AI Technical Career Mentor and Senior Staff Software Engineer.
You specialize in helping candidates master:
- Python & Django (architecture, ORM, REST APIs, concurrency)
- SQL & Databases (indexing, query plans, normalization, transactions)
- Machine Learning & Deep Learning (scikit-learn, PyTorch, evaluation metrics)
- Data Science & Analytics (pandas, numpy, statistics, EDA)
- Generative AI, LLMs & RAG (embeddings, vector databases, prompt engineering)
- Technical Interview Preparation & System Design

Guidelines:
1. Provide accurate, clear, and comprehensive explanations with concise code examples where appropriate.
2. Format your responses with Markdown, using headings, bullet points, and code blocks with syntax highlighting.
3. Be encouraging, professional, and mentor-oriented.
4. If a question is outside technical careers, software engineering, or interview preparation, politely guide the user back to tech topics.
"""

def chat_with_gemini_assistant(user_message, history=None):
    """
    Context-aware technical conversation helper with Gemini.
    `history` is an optional list of dicts: [{'role': 'user'|'model', 'text': '...'}]
    """
    if not is_gemini_configured():
        return (
            "**Gemini API Key Notice:**\n\n"
            "The Gemini API key is currently not configured or is using a placeholder in the `.env` file.\n\n"
            "To activate live AI responses, add your Gemini API key in `.env` as `GEMINI_API_KEY=your_key` and restart the server.\n\n"
            "*In the meantime, you can explore the Aptitude tests, Coding challenges, Resume builder, and Question banks!*",
            None
        )

    client = get_gemini_client()
    if not client:
        return ("Unable to initialize Gemini client. Please check server logs.", "Client error")

    model_name = get_active_model()
    try:
        # Build prompt incorporating recent conversation turns
        prompt_parts = []
        if history:
            for turn in history[-6:]: # keep last 6 turns for context
                role_label = "User" if turn.get('role') == 'user' else "Assistant"
                prompt_parts.append(f"{role_label}: {turn.get('text', '')}")

        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("Assistant:")
        full_prompt = "\n\n".join(prompt_parts)

        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=CHATBOT_SYSTEM_PROMPT,
            temperature=0.7,
        )

        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=config
        )
        return (response.text or "").strip(), None
    except Exception as exc:
        sanitized_err = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED]', str(exc))
        logger.warning("Chatbot query failed: %s", sanitized_err)
        return (
            f"⚠️ An error occurred while communicating with Gemini AI: {sanitized_err[:180]}. "
            "Please check your API quota or network connection.",
            sanitized_err
        )

# -------------------------------------------------------------------
# Domain Feature 5: Job Recommendations & Career Roadmaps
# -------------------------------------------------------------------

def generate_ai_career_roadmap(role="Python Developer", current_skills=""):
    """
    Generates step-by-step career roadmap and skill gap analysis for a target role.
    """
    prompt = f"""
You are a Staff Technical Career Advisor.
Create a comprehensive, step-by-step career development roadmap for an aspiring '{role}'.
Current Skills: {current_skills or 'Basic programming'}

Return a strict JSON object:
{{
  "role": "{role}",
  "overview": "2-3 sentences overview of the role and modern market demand",
  "skill_prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "skills_to_learn": ["High-priority skill 1", "High-priority skill 2", "High-priority skill 3"],
  "roadmap_stages": [
    {{
      "stage": "Phase 1: Foundations",
      "duration": "4-6 Weeks",
      "topics": ["Topic A", "Topic B"],
      "recommended_projects": ["Project 1"]
    }},
    {{
      "stage": "Phase 2: Core Frameworks & Architecture",
      "duration": "6-8 Weeks",
      "topics": ["Topic C", "Topic D"],
      "recommended_projects": ["Project 2"]
    }},
    {{
      "stage": "Phase 3: Production & Interview Readiness",
      "duration": "4 Weeks",
      "topics": ["Topic E", "Topic F"],
      "recommended_projects": ["Project 3"]
    }}
  ],
  "interview_focus_areas": ["Key interview topic 1", "Key interview topic 2"]
}}

Return ONLY valid JSON.
"""
    system_inst = "You are a career engineering director. Return strictly valid JSON."
    text, err = generate_gemini_text(prompt, system_instruction=system_inst, json_mode=True)

    if text and not err:
        try:
            cleaned = clean_json_response(text)
            return json.loads(cleaned)
        except Exception as e:
            logger.warning("Failed to parse Gemini roadmap JSON: %s", str(e))

    # Curated Fallback Roadmap
    return {
        "role": role,
        "overview": f"The {role} role requires solid foundations in algorithmic problem solving, clean application architecture, and hands-on system building.",
        "skill_prerequisites": ["Core Programming Syntax", "Version Control (Git)", "Basic SQL & Data Types"],
        "skills_to_learn": ["Advanced Frameworks (Django / FastAPI)", "RESTful API Design & OpenAPI", "Database Indexing & Query Tuning", "Docker & Containerization"],
        "roadmap_stages": [
            {
                "stage": "Phase 1: Core Fundamentals & OOP",
                "duration": "3-4 Weeks",
                "topics": ["Data Structures & Algorithms", "Object-Oriented Design Patterns", "Unit Testing with PyTest"],
                "recommended_projects": ["CLI Task Manager with persistent SQLite storage"]
            },
            {
                "stage": "Phase 2: Backend Architecture & APIs",
                "duration": "5-6 Weeks",
                "topics": ["Django / DRF Architecture", "Relational Database Design & Migrations", "JWT Authentication & Security Middleware"],
                "recommended_projects": ["Full-Stack E-Commerce or Social API with automated test suite"]
            },
            {
                "stage": "Phase 3: Production Deployment & Scale",
                "duration": "3-4 Weeks",
                "topics": ["Docker & Docker-Compose", "Caching with Redis & Asynchronous Tasks with Celery", "CI/CD Pipeline with GitHub Actions"],
                "recommended_projects": ["Microservice API deployed with Docker and Redis caching"]
            }
        ],
        "interview_focus_areas": ["Memory management & Concurrency", "Database query optimization (N+1 issues)", "System design for scalable web services"]
    }

