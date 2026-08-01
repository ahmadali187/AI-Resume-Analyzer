import json
import os
import re
from flask import current_app
from utils.logger import logger
from utils.prompt_builder import PromptBuilder


class GroqService:
    """Groq API wrapper with error handling, retries, and offline simulation fallback."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or current_app.config.get("GROQ_API_KEY", "") if current_app else os.getenv("GROQ_API_KEY", "")
        self.model = model or current_app.config.get("GROQ_MODEL", "llama-3.3-70b-versatile") if current_app else os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def analyze_resume(self, resume_text: str, parsed_json: dict) -> dict:
        """Analyze resume for grammar, tone, formatting, weak/strong statements, ATS scores."""
        if self._has_valid_api_key():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                prompt = PromptBuilder.build_resume_analysis_prompt(resume_text, parsed_json)

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional ATS Resume Analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                content = response.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                logger.error(f"Groq API call failed: {e}. Switching to offline fallback engine.")

        # Offline Fallback Engine
        return self._simulate_resume_analysis(resume_text, parsed_json)

    def match_job_description(self, resume_text: str, job_description: str) -> dict:
        """Compare candidate resume against target Job Description."""
        if self._has_valid_api_key():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                prompt = PromptBuilder.build_job_match_prompt(resume_text, job_description)

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an AI Job Matching Specialist."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                content = response.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                logger.error(f"Groq Job Match call failed: {e}. Switching to fallback engine.")

        # Offline Fallback Engine
        return self._simulate_job_match(resume_text, job_description)

    def generate_cover_letter(self, resume_text: str, company: str, job_role: str) -> str:
        """Generate tailored cover letter."""
        if self._has_valid_api_key():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                prompt = PromptBuilder.build_cover_letter_prompt(resume_text, company, job_role)

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an Executive Cover Letter Writer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5
                )

                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq Cover Letter generation failed: {e}. Using fallback.")

        return self._simulate_cover_letter(resume_text, company, job_role)

    def generate_interview_prep(self, resume_text: str, job_role: str, offset: int = 0) -> list:
        """Generate 5 tailored interview prep questions per batch with offset support."""
        if self._has_valid_api_key():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                prompt = PromptBuilder.build_interview_prep_prompt(resume_text, job_role) + f"\nGenerate batch index {offset} (5 questions)."

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a Senior Technical Interviewer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    response_format={"type": "json_object"}
                )

                content = json.loads(response.choices[0].message.content)
                if isinstance(content, dict) and "questions" in content:
                    return content["questions"][:5]
                elif isinstance(content, list):
                    return content[:5]
            except Exception as e:
                logger.error(f"Groq Interview Prep failed: {e}. Using fallback.")

        return self._simulate_interview_prep(job_role, offset=offset)

    def generate_summary(self, resume_text: str, job_role: str = "") -> str:
        """Generate candidate executive summary."""
        if self._has_valid_api_key():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                target = f" for a {job_role} role" if job_role else ""
                prompt = f"Generate a concise 3-sentence executive summary{target} based on this resume:\n{resume_text[:2500]}"
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an Executive Resume Writer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Groq generate_summary failed: {e}")

        role_title = job_role or "Professional"
        return (f"Results-driven {role_title} with demonstrated expertise in technical domain areas, full-stack application development, "
                f"and database design. Proven track record of delivering robust software solutions "
                f"utilizing modern engineering best practices.")

    def parse_resume_with_ai(self, resume_text: str) -> dict:
        """Uses Groq API LLM to extract structured JSON from raw resume text."""
        if self._has_valid_api_key():
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                prompt = (
                    "Extract structured JSON from the following resume text. "
                    "Return ONLY a JSON object with these keys:\n"
                    "{\n"
                    '  "personal_information": {"name": "", "email": "", "phone": "", "address": "", "location": "", "linkedin": "", "github": "", "portfolio": "", "website": "", "dob": "", "nationality": ""},\n'
                    '  "summary": "",\n'
                    '  "objective": "",\n'
                    '  "education": [{"degree": "", "specialization": "", "institute": "", "university": "", "cgpa": "", "duration": "", "location": ""}],\n'
                    '  "experience": [{"company": "", "role": "", "employment_type": "", "duration": "", "location": "", "responsibilities": [], "technologies": []}],\n'
                    '  "internships": [{"company": "", "role": "", "duration": "", "location": "", "responsibilities": [], "technologies": []}],\n'
                    '  "projects": [{"name": "", "category": "", "duration": "", "description": "", "responsibilities": [], "technologies": [], "github": "", "live_demo": ""}],\n'
                    '  "skills": {"programming_languages": [], "frameworks": [], "libraries": [], "databases": [], "cloud": [], "developer_tools": [], "operating_systems": [], "soft_skills": []},\n'
                    '  "certifications": [], "courses": [], "achievements": [], "languages": []\n'
                    "}\n\n"
                    f"Resume Text:\n{resume_text[:4000]}"
                )

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert ATS Resume Parsing AI."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Groq parse_resume_with_ai failed: {e}")
        return {}

    def _has_valid_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10 and not self.api_key.startswith("your_"))

    # =========================================================================
    # OFFLINE SIMULATION FALLBACK ENGINE
    # =========================================================================

    def _simulate_resume_analysis(self, resume_text: str, parsed_json: dict) -> dict:
        word_count = parsed_json.get("word_count", len(resume_text.split()))
        skills = parsed_json.get("skills", [])
        
        # Calculate simulated ATS metrics based on heuristics
        skills_score = min(100, max(50, len(skills) * 8))
        formatting_score = 85 if word_count in range(300, 1000) else 65
        experience_score = 82 if "experience" in parsed_json else 60
        keywords_score = 78
        readability_score = 88 if word_count < 1200 else 70
        
        overall = int((skills_score * 0.3) + (formatting_score * 0.25) + (experience_score * 0.25) + (keywords_score * 0.2))

        return {
            "overall_score": overall,
            "formatting_score": formatting_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "keywords_score": keywords_score,
            "readability_score": readability_score,
            "executive_summary": "Solid technical resume showing strong foundational experience. Clear layout with well-defined technical skills section.",
            "grammar_tone_feedback": "Professional tone maintained throughout. Active verbs utilized across major experience bullets.",
            "weak_statements": [
                "Responsible for maintaining backend database systems.",
                "Worked on creating frontend UI components using HTML and CSS."
            ],
            "strong_statements": [
                f"Architected scalable application components using {skills[0] if skills else 'Python'}.",
                "Optimized database queries resulting in 35% latency reduction."
            ],
            "missing_sections": ["Certifications", "Quantifiable Metrics"] if not parsed_json.get("certifications") else ["Quantifiable Impact Metrics"],
            "action_verb_rating": "Moderate",
            "key_strengths": [
                "Comprehensive technical skills summary",
                "Clear education section",
                "Clean structural layout"
            ],
            "improvement_areas": [
                "Incorporate more quantifiable metrics (percentages, numbers, savings)",
                "Add a tailored 3-line Executive Summary at the top",
                "Include relevant industry certifications"
            ]
        }

    def _simulate_job_match(self, resume_text: str, job_description: str) -> dict:
        text_lower = job_description.lower()
        res_lower = resume_text.lower()

        jd_skills = set()
        from services.resume_parser import ResumeParser
        for cat_skills in ResumeParser.SKILL_TAXONOMY.values():
            for skill in cat_skills:
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, text_lower):
                    jd_skills.add(skill)

        common_tech = ["docker", "aws", "kubernetes", "ci/cd", "redis", "postgresql", "fastapi", "react", "graphql", "next.js", "django", "flask", "python", "mysql", "mongodb", "git", "github", "testing", "microservices"]
        for tech in common_tech:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(tech) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                jd_skills.add(tech)

        matching_skills = []
        missing_skills = []

        for skill in jd_skills:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
            fmt_skill = skill.upper() if len(skill) <= 3 and skill not in ["css", "sql", "git"] else skill.title()
            if skill in ["c++", "c#"]: fmt_skill = skill.upper()
            elif skill == "ci/cd": fmt_skill = "CI/CD"
            elif skill == "rest api": fmt_skill = "REST API"

            if re.search(pattern, res_lower):
                matching_skills.append(fmt_skill)
            else:
                missing_skills.append(fmt_skill)

        if not matching_skills and not missing_skills:
            missing_skills = ["Docker", "AWS Cloud", "CI/CD Automation", "PostgreSQL Optimization"]

        match_pct = 85 if not missing_skills else min(95, max(45, int((len(matching_skills) / max(1, len(jd_skills))) * 100)))

        return {
            "match_percentage": match_pct,
            "matching_skills": sorted(list(set(matching_skills))),
            "missing_skills": sorted(list(set(missing_skills))),
            "missing_keywords": ["Agile Methodology", "Microservices Architecture", "Performance Tuning"],
            "required_experience_assessment": f"Candidate demonstrates {match_pct}% technical match alignment with the target role. Identified {len(matching_skills)} matching skills and {len(missing_skills)} skill gap recommendations.",
            "recommended_changes": [
                "Incorporate missing technical skills into resume project bullet points.",
                "Align experience bullet wording directly with job description key terms."
            ]
        }

    def _simulate_cover_letter(self, resume_text: str, company: str, job_role: str) -> str:
        return f"""
Dear Hiring Manager at {company},

I am writing to express my strong enthusiasm for the {job_role} position at {company}. With a robust background in software engineering, full-stack application development, and system architecture, I am confident in my ability to immediately contribute to your engineering team.

Throughout my career, I have specialized in building scalable, production-grade applications and optimizing backend database systems. My technical toolkit aligns closely with {company}'s technology stack, and I thrive in collaborative environments focused on delivering impactful software solutions.

At my previous roles, I successfully architected microservices, reduced API latency, and improved code deployment pipelines. I am eager to bring this same dedication and technical expertise to {job_role} at {company}.

Thank you for your time and consideration. I look forward to discussing how my experience aligns with your team's goals.

Sincerely,
Candidate
"""

    def _simulate_interview_prep(self, job_role: str, offset: int = 0) -> list:
        all_questions = [
            {
                "category": "Python / Backend",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: How does Flask handle request contexts and thread safety under high concurrency?",
                "ideal_answer": "Flask uses context locals (like `request` and `g`) powered by Werkzeug's LocalProxy. Under WSGI/ASGI servers like Gunicorn, each worker thread or process gets its own context stack, isolating state per request."
            },
            {
                "category": "Database / SQL",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: Explain the difference between INNER JOIN, LEFT JOIN, and B-Tree indexing strategies.",
                "ideal_answer": "INNER JOIN returns matching records from both tables. LEFT JOIN returns all records from the left table and matching from the right. Indexes speed up lookups by avoiding full table scans."
            },
            {
                "category": "Frameworks & Web",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: What are the core architectural differences between Django ORM and SQLAlchemy?",
                "ideal_answer": "Django ORM uses Active Record pattern where models handle data & DB methods. SQLAlchemy uses Data Mapper pattern, separating domain models from database persistence."
            },
            {
                "category": "System Design",
                "difficulty": "Hard",
                "question": f"For a {job_role} role: How would you architect an ATS resume analysis system for high throughput?",
                "ideal_answer": "Use an asynchronous task queue (Celery + Redis/RabbitMQ) for background document parsing and AI requests, storing raw files in S3 and metadata in PostgreSQL with CDN caching."
            },
            {
                "category": "Behavioral",
                "difficulty": "Easy",
                "question": f"For a {job_role} role: Describe a time when you resolved a critical production bug under time pressure.",
                "ideal_answer": "Use STAR method: Situation, Task, Action (log diagnosis, hotfix, regression tests), and Result (restored 99.9% uptime and zero data loss)."
            },
            # Batch 2
            {
                "category": "REST API Architecture",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: What are RESTful best practices for handling pagination, filtering, and rate limiting?",
                "ideal_answer": "Use query params `?page=1&limit=20`, return total counts in headers, and enforce rate limits using Redis token buckets with `X-RateLimit-Remaining`."
            },
            {
                "category": "DevOps & Cloud",
                "difficulty": "Hard",
                "question": f"For a {job_role} role: Explain Docker multi-stage builds and how they reduce container size and security risk.",
                "ideal_answer": "Multi-stage builds compile code in a heavy build container and copy only the final compiled binaries to a scratch runtime container, shrinking image size and reducing attack surface."
            },
            {
                "category": "Data Structures",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: How would you design an LRU Cache with O(1) time complexity for get and put operations?",
                "ideal_answer": "Combine a HashMap (for O(1) lookup) with a Doubly Linked List (for O(1) node removals and insertions at head)."
            },
            {
                "category": "Web Security",
                "difficulty": "Hard",
                "question": f"For a {job_role} role: How do CSRF tokens and JWT authentication protect against web vulnerabilities?",
                "ideal_answer": "CSRF tokens prevent cross-site request forgery by requiring a unique secret header per session. JWTs authenticate stateless API requests using cryptographic signatures."
            },
            {
                "category": "Behavioral",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: How do you handle technical disagreements with senior team members?",
                "ideal_answer": "Focus on benchmark data and trade-off analysis. Present proof-of-concept tests and align recommendations with business objectives."
            },
            # Batch 3
            {
                "category": "Python / Async",
                "difficulty": "Hard",
                "question": f"For a {job_role} role: What is Python GIL and how does asyncio differ from multiprocessing?",
                "ideal_answer": "The GIL locks single-threaded bytecode execution. asyncio handles single-threaded I/O concurrency, while multiprocessing spawns distinct OS processes for CPU-bound tasks."
            },
            {
                "category": "Frontend / React",
                "difficulty": "Medium",
                "question": f"For a {job_role} role: Explain React Virtual DOM diffing and why unique key props are critical.",
                "ideal_answer": "Virtual DOM diffing calculates minimal real DOM updates. Unique keys allow React to track modified, inserted, or removed items efficiently."
            },
            {
                "category": "Database Design",
                "difficulty": "Hard",
                "question": f"For a {job_role} role: Explain ACID compliance vs Eventual Consistency in NoSQL databases.",
                "ideal_answer": "ACID guarantees strict transactional integrity. Eventual Consistency prioritizes high availability and horizontal scalability across distributed nodes."
            },
            {
                "category": "Microservices",
                "difficulty": "Hard",
                "question": f"For a {job_role} role: How do you handle distributed transactions across microservices without 2PC?",
                "ideal_answer": "Use the Saga Pattern (Choreography/Orchestration) where each service executes local transactions and triggers compensating transactions if downstream steps fail."
            },
            {
                "category": "Behavioral",
                "difficulty": "Easy",
                "question": f"For a {job_role} role: How do you prioritize competing deadlines across multiple projects?",
                "ideal_answer": "Use the Eisenhower Matrix to rank tasks by urgency and impact, communicate proactively with project managers, and break work into sprint milestones."
            }
        ]

        start = (offset * 5) % len(all_questions)
        batch = all_questions[start:start + 5]
        if len(batch) < 5:
            batch.extend(all_questions[:5 - len(batch)])
        return batch
