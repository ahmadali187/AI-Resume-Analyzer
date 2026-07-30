import json


class PromptBuilder:
    """Helper class to build structured prompts for Groq API."""

    @staticmethod
    def build_resume_analysis_prompt(resume_text: str, parsed_json: dict) -> str:
        return f"""
You are an expert ATS System Specialist, Senior Technical Recruiter, and AI Resume Coach.
Analyze the following resume text and structured resume data:

RESUME TEXT:
{resume_text[:4000]}

STRUCTURED DATA:
{json.dumps(parsed_json, indent=2)[:2000]}

Respond ONLY in valid JSON with the following structure:
{{
  "overall_score": 85,
  "formatting_score": 80,
  "skills_score": 90,
  "experience_score": 85,
  "keywords_score": 80,
  "readability_score": 88,
  "executive_summary": "High-level review of the candidate...",
  "grammar_tone_feedback": "Detailed feedback on professional tone and grammar...",
  "weak_statements": ["Statement 1...", "Statement 2..."],
  "strong_statements": ["Statement 1...", "Statement 2..."],
  "missing_sections": ["Missing section 1...", "Missing section 2..."],
  "action_verb_rating": "Strong / Moderate / Needs Improvement",
  "key_strengths": ["Strength 1", "Strength 2"],
  "improvement_areas": ["Area 1", "Area 2"]
}}
"""

    @staticmethod
    def build_job_match_prompt(resume_text: str, job_description: str) -> str:
        return f"""
You are an expert Technical Recruiter matching a Candidate Resume with a Job Description.

RESUME TEXT:
{resume_text[:3500]}

JOB DESCRIPTION:
{job_description[:3500]}

Respond ONLY in valid JSON with the following structure:
{{
  "match_percentage": 82,
  "matching_skills": ["Skill 1", "Skill 2"],
  "missing_skills": ["Missing Skill 1", "Missing Skill 2"],
  "missing_keywords": ["Keyword 1", "Keyword 2"],
  "required_experience_assessment": "Assessment of experience match...",
  "recommended_changes": [
    "Add metric X to experience section...",
    "Highlight technology Y..."
  ]
}}
"""

    @staticmethod
    def build_cover_letter_prompt(resume_text: str, company: str, job_role: str) -> str:
        return f"""
You are a professional Executive Resume Writer. Write a compelling, highly personalized cover letter for:
Candidate Resume: {resume_text[:2500]}
Company: {company}
Job Role: {job_role}

Return ONLY the plain text / markdown content of the cover letter. Include salutation, strong opening paragraph, 2 impact-focused body paragraphs drawing directly from resume achievements, and a strong closing CTA.
"""

    @staticmethod
    def build_interview_prep_prompt(resume_text: str, job_role: str) -> str:
        return f"""
Generate 10 comprehensive interview questions with detailed sample answers for a candidate applying for: {job_role or 'Target Role'}.
Base questions on the candidate's resume:
{resume_text[:2500]}

Include categories: Python/Technical, SQL/Database, System Design/Architecture, Project Deep Dive, HR/Behavioral.
Return ONLY valid JSON format:
[
  {{
    "category": "Technical",
    "difficulty": "Medium",
    "question": "Question text...",
    "ideal_answer": "Detailed recommended response..."
  }}
]
"""

    @staticmethod
    def build_resume_rewrite_prompt(resume_text: str) -> str:
        return f"""
Rewrite and optimize the following resume text to make it high-impact, ATS-optimized, with strong action verbs and quantified achievements.
Original Resume:
{resume_text[:3500]}

Return ONLY valid JSON format:
{{
  "professional_summary": "Updated summary...",
  "improved_bullets": [
    "Architected high-throughput REST API using Flask...",
    "Engineered automated CI/CD pipeline..."
  ],
  "suggested_skills_section": ["Python", "Flask", "Docker", "PostgreSQL", "AWS"]
}}
"""
