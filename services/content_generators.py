from services.groq_service import GroqService


class ContentGenerator:
    """Service to generate professional summaries, cover letters, and interview preparation content."""

    def __init__(self, groq_service: GroqService = None):
        self.groq_service = groq_service or GroqService()

    def generate_summary(self, resume_text: str, job_role: str = "") -> str:
        """Generates executive professional summary."""
        return self.groq_service.generate_summary(resume_text, job_role)

    def generate_cover_letter(self, resume_text: str, company: str, job_role: str) -> str:
        """Generates tailored cover letter."""
        return self.groq_service.generate_cover_letter(resume_text, company, job_role)

    def generate_interview_prep(self, resume_text: str, job_role: str) -> list:
        """Generates interview prep Q&A list."""
        return self.groq_service.generate_interview_prep(resume_text, job_role)
