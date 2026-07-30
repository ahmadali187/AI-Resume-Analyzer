from services.resume_parser import ResumeParser


def test_resume_parser_structured_extraction():
    """Test text parsing of emails, phone numbers, and technical skills."""
    sample_text = """
    John Doe
    john.doe@example.com | +1 (555) 019-2834 | San Francisco, CA
    https://linkedin.com/in/johndoe | https://github.com/johndoe

    SKILLS
    Python, Flask, Docker, PostgreSQL, AWS, Redis, React, Git, CI/CD

    EXPERIENCE
    Senior Software Engineer - Tech Solutions
    Architected RESTful APIs using Flask and optimized PostgreSQL database queries, reducing response times by 40%.
    """

    parsed = ResumeParser.parse_resume(sample_text)

    assert parsed["contact_info"]["email"] == "john.doe@example.com"
    assert "Python" in parsed["skills"]
    assert "Flask" in parsed["skills"]
    assert "Docker" in parsed["skills"]
    assert parsed["word_count"] > 20
