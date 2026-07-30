from services.ats_analyzer import ATSAnalyzer


def test_ats_scoring_calculation():
    """Test ATS score calculations across categories."""
    resume_text = "Architected and built microservices using Python, Flask, Docker, and PostgreSQL. Reduced latency by 35%."
    parsed_json = {
        "word_count": 500,
        "skills": ["Python", "Flask", "Docker", "PostgreSQL", "AWS", "Git", "Redis", "CI/CD"],
        "contact_info": {"email": "dev@test.com", "phone": "1234567890"},
        "experience": ["Senior Software Developer"]
    }

    scores = ATSAnalyzer.calculate_scores(resume_text, parsed_json)

    assert "overall_ats" in scores
    assert scores["overall_ats"] >= 70
    assert scores["skills_score"] >= 80
    assert scores["formatting_score"] >= 80
