import re


class ATSAnalyzer:
    """Calculates granular category ATS scores and recommendations."""

    ACTION_VERBS = [
        "architected", "built", "created", "designed", "developed", "engineered",
        "implemented", "launched", "managed", "optimized", "reduced", "increased",
        "spearheaded", "transformed", "streamlined", "automated", "lead", "formulated"
    ]

    @classmethod
    def calculate_scores(cls, resume_text: str, parsed_json: dict, ai_analysis: dict = None) -> dict:
        """
        Calculates category scores:
        - formatting
        - skills
        - experience
        - keywords
        - readability
        - overall_ats
        """
        formatting_score = cls._score_formatting(resume_text, parsed_json)
        skills_score = cls._score_skills(parsed_json)
        experience_score = cls._score_experience(parsed_json)
        keywords_score = cls._score_keywords(resume_text)
        readability_score = cls._score_readability(resume_text)

        # Merge with AI scores if available
        if ai_analysis and isinstance(ai_analysis, dict):
            formatting_score = int((formatting_score + ai_analysis.get("formatting_score", formatting_score)) / 2)
            skills_score = int((skills_score + ai_analysis.get("skills_score", skills_score)) / 2)
            experience_score = int((experience_score + ai_analysis.get("experience_score", experience_score)) / 2)
            keywords_score = int((keywords_score + ai_analysis.get("keywords_score", keywords_score)) / 2)
            readability_score = int((readability_score + ai_analysis.get("readability_score", readability_score)) / 2)

        # Weighted Final Overall ATS Score
        overall_ats = int(
            (formatting_score * 0.20) +
            (skills_score * 0.25) +
            (experience_score * 0.25) +
            (keywords_score * 0.15) +
            (readability_score * 0.15)
        )
        overall_ats = max(0, min(100, overall_ats))

        return {
            "overall_ats": overall_ats,
            "formatting_score": formatting_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "keywords_score": keywords_score,
            "readability_score": readability_score,
            "breakdown": {
                "word_count": parsed_json.get("word_count", len(resume_text.split())),
                "action_verb_count": cls._count_action_verbs(resume_text),
                "skills_count": len(parsed_json.get("skills", [])),
                "has_contact_info": bool(parsed_json.get("contact_info", {}).get("email")),
                "has_linkedin": bool(parsed_json.get("contact_info", {}).get("linkedin")),
                "has_github": bool(parsed_json.get("contact_info", {}).get("github")),
            }
        }

    @classmethod
    def _score_formatting(cls, text: str, parsed: dict) -> int:
        score = 100
        words = parsed.get("word_count", len(text.split()))

        # Ideal word count range: 400 to 1000 words
        if words < 250:
            score -= 30
        elif words < 400:
            score -= 15
        elif words > 1200:
            score -= 20

        # Check contact info
        contact = parsed.get("contact_info", {})
        if not contact.get("email"):
            score -= 20
        if not contact.get("phone"):
            score -= 10

        return max(30, score)

    @classmethod
    def _score_skills(cls, parsed: dict) -> int:
        skills = parsed.get("skills", [])
        count = len(skills)
        if count >= 12:
            return 95
        elif count >= 8:
            return 85
        elif count >= 5:
            return 75
        elif count >= 2:
            return 60
        return 40

    @classmethod
    def _score_experience(cls, parsed: dict) -> int:
        exp = parsed.get("experience", [])
        projects = parsed.get("projects", [])
        if exp or projects:
            return 85
        return 50

    @classmethod
    def _score_keywords(cls, text: str) -> int:
        count = cls._count_action_verbs(text)
        if count >= 8:
            return 90
        elif count >= 5:
            return 80
        elif count >= 2:
            return 65
        return 45

    @classmethod
    def _score_readability(cls, text: str) -> int:
        # Check average line length and paragraph structure
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return 50
        avg_line_len = sum(len(line) for line in lines) / len(lines)
        if 30 <= avg_line_len <= 90:
            return 90
        return 75

    @classmethod
    def _count_action_verbs(cls, text: str) -> int:
        text_lower = text.lower()
        count = 0
        for verb in cls.ACTION_VERBS:
            pattern = r'\b' + re.escape(verb) + r'\b'
            count += len(re.findall(pattern, text_lower))
        return count
