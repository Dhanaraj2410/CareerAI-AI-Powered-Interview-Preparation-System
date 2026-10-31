"""
CareerAI Group Discussion (GD) Seed Topics
------------------------------------------
Seeds realistic GD topics across Technology, AI & Ethics, Corporate Culture, and Current Affairs.
"""

from .models import GDTopic

SAMPLE_GD_TOPICS = [
    {
        "title": "Artificial Intelligence in Tech Hiring: Efficiency vs. Algorithmic Bias",
        "category": "AI & Ethics",
        "description": "Automated AI resume screeners and algorithmic interview tools promise speed and scalability, but critics highlight perpetuation of historic bias and dehumanization in corporate hiring pipelines.",
        "pro_arguments": "- Enables objective screening of thousands of applicants based purely on documented skills\n- Eliminates recruiter fatigue and human unconscious biases in initial resume vetting\n- Accelerates hiring turnaround time from weeks to hours",
        "con_arguments": "- AI algorithms trained on historical data risk amplifying pre-existing workforce disparities\n- Lack of transparency in black-box models makes dispute resolution challenging\n- Cannot evaluate creative intuition, leadership temperament, or cultural resilience",
        "key_discussion_points": "Explainable AI (XAI) audits, human-in-the-loop oversight, data privacy regulation, candidate feedback transparency."
    },
    {
        "title": "Remote First vs. Return-to-Office: The Future of Engineering Culture",
        "category": "Corporate Culture",
        "description": "Global technology enterprises are fiercely divided between fully distributed asynchronous work cultures and mandatory return-to-office (RTO) mandates.",
        "pro_arguments": "- Access to top global talent without geographic or relocation constraints\n- Enhanced individual deep-focus developer productivity with fewer office distractions\n- Lower overhead costs and better personal work-life flexibility",
        "con_arguments": "- Reduced spontaneous cross-team whiteboard collaboration\n- Junior engineer onboarding and apprenticeship is significantly more difficult\n- Potential for developer isolation, loneliness, and communication silos",
        "key_discussion_points": "Measuring output vs hours, hybrid schedule effectiveness, async documentation culture, mentorship structures."
    },
    {
        "title": "Open Source vs. Closed Proprietary AI: The Battle for Innovation Control",
        "category": "Tech Trends",
        "description": "As foundation models advance rapidly, the debate between open-weights architectures (e.g. Llama, Mistral) and guarded proprietary APIs (e.g. OpenAI, Anthropic) defines the future of computing sovereignty.",
        "pro_arguments": "- Democratizes AI research for universities, startups, and developing nations\n- Allows comprehensive cybersecurity audits and privacy-preserving on-premise execution\n- Prevents monopolistic pricing and gatekeeping by big tech platforms",
        "con_arguments": "- Open weights models cannot be revoked or patched once malicious fine-tunes occur\n- Massive training compute costs require commercial revenue models to sustain\n- Safety guardrails can be bypassed more readily by adversaries",
        "key_discussion_points": "Responsible AI disclosure, sovereign computing, commercial sustainability, dual-use technology controls."
    },
    {
        "title": "Will Generative AI Replace Junior Developers or Elevate Them?",
        "category": "Tech Trends",
        "description": "AI code generators like GitHub Copilot and Gemini Code Assist write boilerplate code instantly. What is the impact on entry-level software engineering careers?",
        "pro_arguments": "- Enables junior developers to build complete full-stack products faster\n- Shifts developer focus from repetitive syntax memorization to system design and logic\n- Provides 24/7 personalized code tutoring and architectural explanation",
        "con_arguments": "- May lead to superficial understanding if fundamentals are bypassed\n- Security vulnerabilities and hallucinations can be blindly committed into production\n- Companies may reduce junior intake, shrinking the entry-level talent pipeline",
        "key_discussion_points": "Evolving curriculum in computer science, code review rigor, prompt engineering vs core algorithms, apprenticeship models."
    }
]

def seed_gd_topics():
    count = 0
    for data in SAMPLE_GD_TOPICS:
        obj, created = GDTopic.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
        if created:
            count += 1
    return count

