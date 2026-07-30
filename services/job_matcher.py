import re
from services.groq_service import GroqService


class JobMatcher:
    """Service to compare candidate resume with Job Description and compute Skill Gap Roadmaps."""

    @classmethod
    def match(cls, resume_text: str, parsed_json: dict, job_description: str, groq_service: GroqService = None) -> dict:
        """Compares resume text against target job description."""
        if not groq_service:
            groq_service = GroqService()

        ai_match = groq_service.match_job_description(resume_text, job_description)

        # Generate learning roadmap for missing skills
        missing_skills = ai_match.get("missing_skills", [])
        roadmap = cls.generate_skill_roadmap(missing_skills)
        ai_match["skill_roadmap"] = roadmap

        return ai_match

    @classmethod
    def generate_skill_roadmap(cls, missing_skills: list) -> list:
        """Build structured learning recommendations for missing skills."""
        roadmap = []
        
        resource_db = {
            "docker": {
                "course": "Docker & Kubernetes: The Practical Guide (Udemy)",
                "book": "Docker Deep Dive by Nigel Poulton",
                "project": "Containerize a Flask REST API with PostgreSQL & Redis",
                "certification": "Docker Certified Associate (DCA)"
            },
            "aws": {
                "course": "AWS Certified Solutions Architect Associate (A Cloud Guru)",
                "book": "AWS in Action by Andreas Wittig",
                "project": "Deploy a serverless Python web app using S3, Lambda, and DynamoDB",
                "certification": "AWS Certified Developer / Solutions Architect"
            },
            "ci/cd": {
                "course": "GitHub Actions: The Complete Guide",
                "book": "Continuous Delivery by Jez Humble",
                "project": "Configure automated GitHub Actions pipeline with Pytest & Docker Hub",
                "certification": "GitLab / GitHub Actions Certification"
            },
            "redis": {
                "course": "Redis University - RU101: Introduction to Redis",
                "book": "Redis in Action by Josiah L. Carlson",
                "project": "Implement caching layer & session management in Flask app",
                "certification": "Redis Certified Developer"
            },
            "postgresql": {
                "course": "Complete SQL & PostgreSQL Bootcamp",
                "book": "Designing Data-Intensive Applications by Martin Kleppmann",
                "project": "Optimize database schemas, indexes, and query performance",
                "certification": "PostgreSQL Certified Engineer"
            }
        }

        for skill in missing_skills:
            skill_clean = skill.lower().strip()
            res = resource_db.get(
                skill_clean,
                {
                    "course": f"Complete Masterclass on {skill}",
                    "book": f"Learning {skill}: From Basics to Production",
                    "project": f"Build a practical hands-on project utilizing {skill}",
                    "certification": f"{skill} Certified Professional"
                }
            )
            roadmap.append({
                "skill": skill.title(),
                "course": res["course"],
                "book": res["book"],
                "project": res["project"],
                "certification": res["certification"]
            })

        return roadmap
